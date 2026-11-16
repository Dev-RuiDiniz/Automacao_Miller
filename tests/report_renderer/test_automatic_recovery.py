"""Continuação por checkpoint e retentativas limitadas sem afrouxar validação."""

import copy
import hashlib
import json
import socket
from urllib.error import HTTPError, URLError

import pytest
from fastapi.testclient import TestClient

from infra.report_renderer import anvisa_v8 as v, incremental as inc, analysis_checkpoint as storage
from infra.report_renderer import migrate_checkpoint as migration, context_window as ctx
from infra.report_renderer.app import app
from tests.report_renderer.test_incremental import source, record, response, request_data, checkpoint
from tests.report_renderer.test_execution_deadline import analyze


@pytest.fixture
def sleeps(monkeypatch):
    calls = []
    monkeypatch.setattr(inc.time, "sleep", calls.append)
    return calls


def test_more_than_32_calls_complete_same_batch_with_checkpoint_revalidation(monkeypatch):
    rows = [record(1, f"E{n}") for n in range(36)]
    text = "## Página 1\n" + "".join(f"Evento E{n}1\n" for n in range(36))
    calls, validations = [], []
    original = inc._validated_state

    def validate(state, pages):
        validations.append(len(state["pending"][0]["records"]) if state["pending"] else None)
        return original(state, pages)

    def request(messages, *_):
        data = request_data(messages)
        calls.append(data)
        index = len(calls) - 1
        assert data["continuidade"]["indice_registros_preservados"] == [ctx.record_index(r) for r in rows[:index]]
        return response([1], [rows[index]], partial=index < 35, ids=[r["id"] for r in rows[:index+1]])

    monkeypatch.setattr(inc, "_validated_state", validate)
    monkeypatch.setattr(v, "_request", request)
    found, coverage = analyze(text)
    assert found == rows and len(calls) == 36 and 32 in validations
    assert coverage["processamento_incremental"]["continuacoes_automaticas"] == 1
    with checkpoint(text) as saved:
        assert saved.load()["completed"][0]["result"]["registros"] == rows


def test_retries_reuse_identical_packet_and_do_not_repeat_completed_batch(monkeypatch, sleeps):
    monkeypatch.setattr(inc, "MAX_CONTINUATIONS", 2)
    calls = []

    def request(messages, key, timeout):
        data = request_data(messages)
        calls.append(data)
        assert timeout == 360
        if data["paginas_alvo"][0] == 1:
            return response(data["paginas_alvo"], [record()])
        if len(calls) < 4:
            raise v.TransientAnvisaError("IA: falha de conexão ou tempo limite no OpenRouter.")
        return response(data["paginas_alvo"], [record(6)])

    monkeypatch.setattr(v, "_request", request)
    rows, coverage = analyze(source(10))
    assert rows == [record(), record(6)] and calls[1] == calls[2] == calls[3]
    assert sleeps == [5, 15]
    assert coverage["processamento_incremental"]["retentativas_transporte"] == 2
    assert coverage["processamento_incremental"]["continuacoes_automaticas"] == 1


def test_retry_budget_is_not_reset_by_window_and_keeps_partial_records(monkeypatch, sleeps):
    monkeypatch.setattr(inc, "MAX_CONTINUATIONS", 1)
    calls = []

    def request(messages, *_):
        data = request_data(messages)
        calls.append(data)
        if len(calls) == 1:
            return response(data["paginas_alvo"], [record()])
        if len(calls) == 2:
            return response(data["paginas_alvo"], [record(6)], partial=True)
        raise v.TransientAnvisaError("IA: OpenRouter retornou HTTP 503.")

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaError, match="após 3 tentativas; checkpoint preservado"):
        analyze(source(10))
    assert len(calls) == 5 and sleeps == [5, 15]
    with checkpoint(source(10)) as saved:
        state = saved.load()
    assert state["completed"][0]["result"]["registros"] == [record()]
    assert state["pending"][0]["records"] == [record(6)]

    def resume(messages, *_):
        data = request_data(messages)
        assert data["paginas_alvo"] == list(range(6, 11))
        assert data["continuidade"]["indice_registros_preservados"] == [ctx.record_index(r) for r in [record(6)]]
        return response(data["paginas_alvo"], ids=[record(6)["id"]])

    monkeypatch.setattr(v, "_request", resume)
    assert analyze(source(10))[0] == [record(), record(6)]


def test_retry_budget_reopens_only_after_transport_success(monkeypatch, sleeps):
    calls = []

    def request(messages, *_):
        data = request_data(messages)
        calls.append(data)
        if len(calls) in {1, 2, 4, 5}:
            raise v.TransientAnvisaError("IA: falha de conexão ou tempo limite no OpenRouter.")
        if len(calls) == 3:
            return response([1], [record()], partial=True)
        return response([1], [record(suffix="B")], ids=[record()["id"], record(suffix="B")["id"]])

    monkeypatch.setattr(v, "_request", request)
    rows, coverage = analyze(source())
    assert rows == [record(), record(suffix="B")]
    assert sleeps == [5, 15, 5, 15] and len(calls) == 6
    assert coverage["processamento_incremental"]["retentativas_transporte"] == 4


def test_correction_and_transport_retry_keep_previous_answer_and_single_correction(monkeypatch, sleeps):
    monkeypatch.setattr(inc, "MAX_CONTINUATIONS", 1)
    bad = response([1], [dict(record(), evidencias=[{"pagina": 1, "trecho_literal": "Trecho inexistente."}])])
    calls = []

    def request(messages, *_):
        data = request_data(messages)
        calls.append(data)
        if len(calls) == 1:
            return copy.deepcopy(bad)
        assert data["resposta_anterior"] == bad and data["diagnostico_validacao"]
        if len(calls) == 2:
            raise v.TransientAnvisaError("IA: falha de conexão ou tempo limite no OpenRouter.")
        assert calls[1] == calls[2]
        return response([1], [record()])

    monkeypatch.setattr(v, "_request", request)
    rows, coverage = analyze(source())
    assert rows == [record()] and sleeps == [5]
    assert coverage["processamento_incremental"]["continuacoes_automaticas"] == 2


def test_second_invalid_answer_is_not_granted_another_correction_at_window_boundary(monkeypatch, sleeps):
    monkeypatch.setattr(inc, "MAX_CONTINUATIONS", 1)
    calls = []

    def request(messages, *_):
        calls.append(request_data(messages))
        return response([1], [dict(record(), evidencias=[{"pagina": 1, "trecho_literal": "Ausente."}])])

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.EvidenceValidationError):
        analyze(source())
    assert len(calls) == 2 and sleeps == []


def test_no_progress_counter_survives_automatic_windows(monkeypatch):
    monkeypatch.setattr(inc, "MAX_CONTINUATIONS", 1)
    calls = []

    def request(*_):
        calls.append(True)
        return response([1], [record()], partial=True)

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaError, match="sem progresso"):
        analyze(source())
    assert len(calls) == 3


def test_page_expansion_budget_survives_automatic_windows(monkeypatch):
    monkeypatch.setattr(inc, "MAX_CONTINUATIONS", 1)
    calls = []

    def request(*_):
        calls.append(True)
        return {"contexto_necessario": [[8, 10, 12, 14][len(calls)-1]]}

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaError, match="ampliações de páginas sem avanço"):
        analyze(source(20))
    assert len(calls) == 4
    with checkpoint(source(20)) as saved:
        assert 14 in saved.load()["pending"][0]["context"]["requested"]


@pytest.mark.parametrize("when", ["window", "retry"])
@pytest.mark.parametrize("damage", ["missing", "json", "semantic"])
def test_checkpoint_damage_prevents_automatic_paid_request(monkeypatch, sleeps, when, damage):
    monkeypatch.setattr(inc, "MAX_CONTINUATIONS", 1)
    loads, calls = [], []
    original = storage.AnalysisCheckpoint.load

    def load(saved):
        loads.append(True)
        if len(loads) == 2:
            if damage == "missing":
                saved.path.unlink()
            elif damage == "json":
                saved.path.write_text("Estado sintético inválido.")
            else:
                data = json.loads(saved.path.read_text())
                data["state"]["pending"][0]["sent"].append(999)
                data["sha256"] = hashlib.sha256(storage.encode(data["state"])).hexdigest()
                saved.path.write_text(json.dumps(data))
        return original(saved)

    def request(*_):
        calls.append(True)
        if when == "retry":
            raise v.TransientAnvisaError("IA: falha de conexão ou tempo limite no OpenRouter.")
        return response([1], [record()], partial=True)

    monkeypatch.setattr(storage.AnalysisCheckpoint, "load", load)
    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(storage.CheckpointStorageError):
        analyze(source())
    assert len(calls) == 1 and sleeps == []


@pytest.mark.parametrize("status", [408, 429, 500, 502, 503, 504, 400, 401, 402, 403, 404, 422])
def test_http_errors_have_explicit_retry_classification(monkeypatch, status):
    class Opener:
        def open(self, *_args, **_kwargs):
            raise HTTPError("https://exemplo.invalid", status, "Erro sintético.", {}, None)

    monkeypatch.setattr(v, "build_opener", lambda *_: Opener())
    with pytest.raises(v.AnvisaError) as failure:
        v._request([], "chave-ficticia", 360)
    assert isinstance(failure.value, v.TransientAnvisaError) is (status in {408, 429, 500, 502, 503, 504})
    assert str(failure.value) == f"IA: OpenRouter retornou HTTP {status}."


@pytest.mark.parametrize("exception", [socket.timeout("Tempo sintético."), URLError("Conexão sintética."), ConnectionResetError("Conexão sintética.")])
def test_connection_errors_are_transient(monkeypatch, exception):
    class Opener:
        def open(self, *_args, **_kwargs):
            raise exception

    monkeypatch.setattr(v, "build_opener", lambda *_: Opener())
    with pytest.raises(v.TransientAnvisaError):
        v._request([], "chave-ficticia", 360)


def test_credit_error_does_not_retry(monkeypatch, sleeps):
    calls = []

    def request(*_):
        calls.append(True)
        raise v.AnvisaError("IA: OpenRouter retornou HTTP 402.")

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaError, match="HTTP 402"):
        analyze(source())
    assert len(calls) == 1 and sleeps == []


def test_http_api_recovers_transient_errors_and_generates_pdf(monkeypatch, sleeps):
    monkeypatch.setenv("INTERNAL_API_TOKEN", "token-ficticio")
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-ficticia")
    monkeypatch.setenv("OPENROUTER_TIMEOUT_SECONDS", "0")
    requests = []

    class Reply:
        def __enter__(self): return self
        def __exit__(self, *_): pass
        def read(self, _size):
            return json.dumps({"model": v.MODEL, "choices": [{"finish_reason": "stop", "message": {
                "content": json.dumps(response([1], [record()]))}}]}).encode()

    class Opener:
        def open(self, request, timeout):
            requests.append(request.data)
            if len(requests) < 3:
                raise HTTPError("https://exemplo.invalid", 503, "Erro sintético.", {}, None)
            return Reply()

    monkeypatch.setattr(v, "build_opener", lambda *_: Opener())
    text = source()
    result = TestClient(app).post("/v1/analyze-anvisa-v8", headers={"X-Internal-Token": "token-ficticio"}, json={
        "markdown": text, "page_count": 1, "markdown_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "source_filename": "sintetico.pdf"})
    assert result.status_code == 200 and result.json()["report_pdf_base64"]
    assert requests[0] == requests[1] == requests[2] and sleeps == [5, 15]
    assert result.json()["report_context"]["analysis_checkpoint"]["retentativas_transporte"] == 2


def test_migration_from_no_deadline_implementation_preserves_pending_state():
    text = source()
    pages = {1: "\nEvento A1\nEvento B1\nEvento C1\n"}
    task = inc._tasks([1], pages)[0]
    task["records"] = [record()]
    task["continuation"] = {key: value for key, value in response([1], [record()], partial=True).items() if key != "registros"}
    previous = {"schema": 3, "completed": [], "pending": [task]}
    old = storage.AnalysisCheckpoint(migration.legacy_identity(hashlib.sha256(text.encode()).hexdigest(), 1, 6), "protocolo-sintetico")
    with old:
        old.save(previous)
    before = old.path.read_bytes()
    result = migration.migrate(text, "protocolo-sintetico", old.key)
    assert result["status"] == "migrado"
    with checkpoint(text) as saved:
        current = saved.load()
    assert current["completed"] == previous["completed"] and current["pending"] == previous["pending"]
    assert migration.migrate(text, "protocolo-sintetico", old.key)["status"] == "ja_migrado"
    assert old.path.read_bytes() == before
