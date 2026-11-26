import base64
import hashlib
import io
import json
import stat
import zipfile

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader

from infra.report_renderer import analysis_checkpoint as storage, anvisa_v8 as v
from infra.report_renderer.app import app
from tests.report_renderer.test_incremental import checkpoint, full_record, record, request_data, response, source


@pytest.fixture
def request_report(monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", "token-ficticio")
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-ficticia")
    client = TestClient(app)

    def request(markdown):
        return client.post("/v1/analyze-anvisa-v8", headers={"X-Internal-Token": "token-ficticio"}, json={
            "markdown": markdown, "page_count": markdown.count("## Página "),
            "markdown_sha256": hashlib.sha256(markdown.encode()).hexdigest(),
            "source_filename": "sintetico.pdf", "diagnostic_context": {
                "submission_id": "protocolo-sintetico", "attempt_number": 1, "execution_id": "sintetica"},
        })

    return request


def test_first_part_is_saved_before_the_second_and_rebuilt_on_resume(monkeypatch, request_report):
    text = source(10)
    directory = checkpoint(text).directory
    first_path, second_path = directory / "parte-1.md", directory / "parte-2.md"
    first, second = full_record(1), full_record(6)
    first["paginas_origem"].append(6)
    first["evidencias"].append({"pagina": 6, "trecho_literal": "Evento B6"})

    def interrupted(messages, *_):
        targets = request_data(messages)["paginas_alvo"]
        if targets[0] == 1:
            assert not first_path.exists()
            return response(targets, [first])
        assert first["id"] in first_path.read_text()
        assert not second_path.exists()
        raise v.AnvisaError("IA: interrupção sintética.")

    monkeypatch.setattr(v, "_request", interrupted)
    assert request_report(text).status_code == 502
    saved_markdown = first_path.read_bytes()
    assert b"Evento B6" in saved_markdown
    first_path.unlink()

    def resumed(messages, *_):
        targets = request_data(messages)["paginas_alvo"]
        assert targets == list(range(6, 11))
        assert first_path.read_bytes() == saved_markdown
        return response(targets, [second])

    monkeypatch.setattr(v, "_request", resumed)
    result = request_report(text)
    assert result.status_code == 200, result.text
    assert second["id"] in second_path.read_text()
    assert first["id"] not in second_path.read_text()
    assert second["id"] not in first_path.read_text()
    assert all(stat.S_IMODE(path.stat().st_mode) == 0o600 for path in (first_path, second_path))
    pdf = base64.b64decode(result.json()["report_pdf_base64"])
    pdf_text = " ".join(page.extract_text() for page in PdfReader(io.BytesIO(pdf)).pages)
    assert first["id"] in pdf_text and second["id"] in pdf_text
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(result.json()["bundle_base64"]))) as bundle:
        records = [json.loads(line) for line in bundle.read("dados_anvisa_v8.jsonl").splitlines()]
    assert records == [first, second]


def test_failed_part_write_blocks_pdf_and_resume_regenerates_it(monkeypatch, request_report):
    text = source()
    monkeypatch.setattr(v, "_request", lambda *_: response([1]))
    original = storage.write_atomically

    def fail_second(path, data):
        if path.name == "parte-2.md":
            raise OSError("falha sintética na escrita")
        original(path, data)

    monkeypatch.setattr(storage, "write_atomically", fail_second)
    assert request_report(text).status_code == 500
    with checkpoint(text) as state:
        assert not state.load()["pending"]
        assert (state.directory / "parte-1.md").is_file()
        assert not (state.directory / "parte-2.md").exists()

    monkeypatch.setattr(storage, "write_atomically", original)
    monkeypatch.setattr(v, "_request", lambda *_: pytest.fail("Lote concluído foi reenviado."))
    assert request_report(text).status_code == 200
    assert "sem páginas" in (checkpoint(text).directory / "parte-2.md").read_text()


def test_one_internal_batch_can_cover_both_parts(monkeypatch, request_report):
    text = source(3)
    first, second = record(2), record(3)
    monkeypatch.setattr(v, "_request", lambda *_: response([1, 2, 3], [second, first]))

    result = request_report(text)
    assert result.status_code == 200, result.text
    directory = checkpoint(text).directory
    part1, part2 = [(directory / f"parte-{n}.md").read_text() for n in (1, 2)]
    assert "1 a 2" in part1 and first["id"] in part1 and second["id"] not in part1
    assert "3 a 3" in part2 and second["id"] in part2 and first["id"] not in part2
