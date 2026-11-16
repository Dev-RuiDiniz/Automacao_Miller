"""A meta de 90 minutos não interrompe análises com prazo global desabilitado."""

import copy
import hashlib

import pytest
from fastapi.testclient import TestClient

from infra.report_renderer import anvisa_v8 as v, incremental as inc, analysis_checkpoint as storage
from infra.report_renderer import migrate_checkpoint as migration
from infra.report_renderer.app import app
from tests.report_renderer.test_incremental import source, record, response, request_data, checkpoint


def analyze(text, seconds=0):
    with checkpoint(text) as saved:
        return v.analyze(text, text.count("## Página "), hashlib.sha256(text.encode()).hexdigest(),
                         "chave-ficticia", seconds, checkpoint_store=saved)


def test_disabled_global_deadline_continues_after_ninety_minutes_and_keeps_call_timeout(monkeypatch):
    clock = [0]
    calls = []
    monkeypatch.setattr(inc.time, "monotonic", lambda: clock[0])

    def request(messages, key, timeout):
        data = request_data(messages)
        calls.append((data["paginas_alvo"], timeout))
        clock[0] += 6000
        return response(data["paginas_alvo"], [record(data["paginas_alvo"][0])])

    monkeypatch.setattr(v, "_request", request)
    rows, coverage = analyze(source(15))
    assert clock[0] == 18000 and rows == [record(1), record(6), record(11)]
    assert calls == [(list(range(1, 6)), 360), (list(range(6, 11)), 360), (list(range(11, 16)), 360)]
    assert len(coverage["paginas"]) == 15
    monkeypatch.setattr(v, "_request", lambda *_: pytest.fail("Checkpoint concluído não repete IA."))
    assert analyze(source(15))[0] == rows


def test_unlimited_analysis_still_stops_after_no_progress_and_preserves_checkpoint(monkeypatch):
    calls = []

    def request(messages, *_):
        calls.append(request_data(messages))
        return response([1], [record()], partial=True)

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaError, match="sem progresso"):
        analyze(source())
    assert len(calls) == 3
    with checkpoint(source()) as saved:
        assert saved.load()["pending"][0]["records"] == [record()]


def test_unlimited_analysis_continues_between_call_windows(monkeypatch):
    monkeypatch.setattr(inc, "MAX_CONTINUATIONS", 2)
    calls = []

    def request(messages, *_):
        calls.append(True)
        rows = [record(suffix=suffix) for suffix in "ABC"]
        index = len(calls) - 1
        return response([1], [rows[index]], partial=index < 2, ids=[row["id"] for row in rows[:index+1]])

    monkeypatch.setattr(v, "_request", request)
    rows, coverage = analyze(source())
    assert len(calls) == len(rows) == 3
    assert coverage["processamento_incremental"]["continuacoes_automaticas"] == 1


def test_explicit_positive_deadline_remains_available_and_limits_individual_call(monkeypatch):
    clock = [0]
    timeouts = []
    monkeypatch.setattr(inc.time, "monotonic", lambda: clock[0])

    def request(messages, key, timeout):
        data = request_data(messages)
        timeouts.append(timeout)
        clock[0] += 550
        return response(data["paginas_alvo"], [record(data["paginas_alvo"][0])])

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaError, match="tempo total"):
        analyze(source(15), 600)
    assert timeouts == [360, 50]
    with checkpoint(source(15)) as saved:
        assert len(saved.load()["completed"]) == 2


@pytest.mark.parametrize("configured", [None, "0"])
def test_api_accepts_disabled_deadline_by_default_and_with_zero(monkeypatch, configured):
    monkeypatch.setenv("INTERNAL_API_TOKEN", "token-ficticio")
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-ficticia")
    if configured is None:
        monkeypatch.delenv("OPENROUTER_TIMEOUT_SECONDS", raising=False)
    else:
        monkeypatch.setenv("OPENROUTER_TIMEOUT_SECONDS", configured)
    deadlines = []
    original = v.analyze

    def analyze_with_capture(markdown, page_count, expected_hash, key, seconds, **kwargs):
        deadlines.append(seconds)
        return original(markdown, page_count, expected_hash, key, seconds, **kwargs)

    monkeypatch.setattr(v, "analyze", analyze_with_capture)
    monkeypatch.setattr(v, "_request", lambda *_: response([1], [record()]))
    text = source()
    result = TestClient(app).post("/v1/analyze-anvisa-v8", headers={"X-Internal-Token": "token-ficticio"}, json={
        "markdown": text, "page_count": 1, "markdown_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "source_filename": "sintetico.pdf"})
    assert result.status_code == 200 and deadlines == [0]


@pytest.mark.parametrize("configured", ["-1", "inválido", "14401"])
def test_api_rejects_invalid_timeout_without_calling_ai(monkeypatch, configured):
    monkeypatch.setenv("INTERNAL_API_TOKEN", "token-ficticio")
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-ficticia")
    monkeypatch.setenv("OPENROUTER_TIMEOUT_SECONDS", configured)
    monkeypatch.setattr(v, "_request", lambda *_: pytest.fail("Configuração inválida não deve chamar IA."))
    text = source()
    result = TestClient(app).post("/v1/analyze-anvisa-v8", headers={"X-Internal-Token": "token-ficticio"}, json={
        "markdown": text, "page_count": 1, "markdown_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "source_filename": "sintetico.pdf"})
    assert result.status_code == 503 and "OPENROUTER_TIMEOUT_SECONDS" in result.json()["detail"]


def test_explicit_migration_from_index_implementation_preserves_all_progress():
    text = source(10)
    pages = {n: f"\nEvento A{n}\nEvento B{n}\nEvento C{n}\n" for n in range(1, 11)}
    task = inc._tasks(list(range(6, 11)), pages)[0]
    task["records"] = [record(6)]
    task["continuation"] = {key: value for key, value in response(task["targets"], task["records"], partial=True).items() if key != "registros"}
    state = {"schema": 3, "completed": [{"targets": list(range(1, 6)), "sent": list(range(1, 8)),
                                        "result": response(list(range(1, 6)), [record()])}], "pending": [task]}
    old = storage.AnalysisCheckpoint(migration.legacy_identity(hashlib.sha256(text.encode()).hexdigest(), 10, 5), "protocolo-sintetico")
    with old:
        old.save(copy.deepcopy(state))
    before = old.path.read_bytes()
    result = migration.migrate(text, "protocolo-sintetico", old.key)
    assert result["status"] == "migrado"
    with checkpoint(text) as saved:
        current = saved.load()
    assert current["completed"] == state["completed"] and current["pending"] == state["pending"]
    assert migration.migrate(text, "protocolo-sintetico", old.key)["status"] == "ja_migrado"
    assert old.path.read_bytes() == before
