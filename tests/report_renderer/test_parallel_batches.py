"""Interlevação real de I/O, persistência única e dependências entre páginas."""

import copy
import hashlib
import threading

import pytest
from fastapi.testclient import TestClient

from infra.report_renderer import anvisa_v8 as v, incremental as inc, parallel_batches as parallel
from infra.report_renderer import analysis_checkpoint as storage, migrate_checkpoint as migration
from infra.report_renderer.app import app
from tests.report_renderer.test_incremental import source, record, response, request_data, checkpoint, analyze


@pytest.fixture(autouse=True)
def two_batches(monkeypatch):
    monkeypatch.setattr(inc, "MAX_PARALLEL_BATCHES", 2)


def test_out_of_order_completion_has_one_writer_and_canonical_final_order(monkeypatch):
    text = source(20)
    release_first = threading.Event()
    main = threading.get_ident()
    saves, starts, workers = [], [], set()
    active = 0
    maximum = 0
    lock = threading.Lock()
    save = storage.AnalysisCheckpoint.save

    def observed_save(store, state):
        assert threading.get_ident() == main
        save(store, state)
        saves.append(copy.deepcopy(state))
        if any(row["targets"][0] == 11 for row in state["completed"]):
            release_first.set()

    def request(messages, *_):
        nonlocal active, maximum
        data = request_data(messages); first = data["paginas_alvo"][0]
        with lock:
            active += 1; maximum = max(maximum, active); starts.append(first); workers.add(threading.get_ident())
        try:
            if first == 1:
                assert release_first.wait(3), "O segundo lote deve concluir antes do primeiro."
            return v.ModelResult(response(data["paginas_alvo"], [record(first)]), "gen-sintetico")
        finally:
            with lock: active -= 1

    monkeypatch.setattr(storage.AnalysisCheckpoint, "save", observed_save)
    monkeypatch.setattr(v, "_request", request)
    rows, coverage = analyze(text)
    assert maximum == 2 and len(workers) == 2 and main not in workers
    assert starts[:2] == [1, 11]
    assert any(s["completed"] and s["completed"][0]["targets"][0] == 11 for s in saves)
    assert [r["id"] for r in rows] == [record(n)["id"] for n in (1, 6, 11, 16)]
    assert coverage["processamento_incremental"]["chamadas_simultaneas_maximas"] == 2
    with checkpoint(text) as store:
        state = store.load()
        assert not state["pending"]
        assert [row["targets"][0] for row in state["completed"]] == [1, 6, 11, 16]
    monkeypatch.setattr(v, "_request", lambda *_: pytest.fail("Estado completo deve ser reutilizado."))
    assert analyze(text)[0] == rows


def test_context_expansion_waits_for_overlapping_inflight_batch(monkeypatch):
    text = source(15)
    requested = threading.Event(); committed = threading.Event()
    counts = {}
    save = storage.AnalysisCheckpoint.save

    def observed_save(store, state):
        save(store, state)
        if any(row["targets"][0] == 1 and 11 in row["context"]["requested"] for row in state["pending"]):
            requested.set()
        if any(row["targets"][0] == 11 for row in state["completed"]): committed.set()

    def request(messages, *_):
        data = request_data(messages); first = data["paginas_alvo"][0]
        counts[first] = counts.get(first, 0) + 1
        if first == 1 and counts[first] == 1: return {"contexto_necessario": [11]}
        if first == 11: assert requested.wait(3)
        if first == 1:
            assert committed.is_set(), "A janela ampliada deve aguardar o lote sobreposto."
            assert 11 in data["contexto_recuperado"]["paginas_nesta_chamada"]
        return response(data["paginas_alvo"], [record(first)])

    monkeypatch.setattr(storage.AnalysisCheckpoint, "save", observed_save)
    monkeypatch.setattr(v, "_request", request)
    assert len(analyze(text)[0]) == 3
    assert counts[1] == 2


def test_adjacent_context_windows_are_not_executed_together(monkeypatch):
    active = 0; maximum = 0
    lock = threading.Lock()

    def request(messages, *_):
        nonlocal active, maximum
        with lock: active += 1; maximum = max(maximum, active)
        data = request_data(messages)
        with lock: active -= 1
        return response(data["paginas_alvo"], [record(data["paginas_alvo"][0])])

    monkeypatch.setattr(v, "_request", request)
    _, coverage = analyze(source(10))
    assert maximum == 1 and coverage["processamento_incremental"]["chamadas_simultaneas_maximas"] == 1


def test_inventory_page_dependency_is_kept_even_without_a_literal_quote():
    pages = {n: f"\nEvento A{n}\n" for n in range(1, 21)}
    task = inc._tasks(list(range(1, 6)), pages)[0]
    task["continuation"] = {"reconciliacao_anexos": [{"unidades_fonte": [
        {"paginas_origem": [1, 11], "ids_eventos": []}]}]}
    assert 11 in parallel.scope(task, pages)
    assert parallel.scope(task, pages) & parallel.scope(inc._tasks(list(range(11, 16)), pages)[0], pages)


def test_persistent_failure_stops_new_calls_and_saves_healthy_inflight_result(monkeypatch):
    text = source(20); started = threading.Barrier(2); failed = threading.Event(); calls = []
    original = inc._task_steps

    def observed_steps(*args):
        try:
            return (yield from original(*args))
        except v.AnvisaError:
            failed.set(); raise

    def request(messages, *_):
        data = request_data(messages); first = data["paginas_alvo"][0]; calls.append(first)
        started.wait(3)
        if first == 1: raise v.AnvisaError("IA: OpenRouter retornou HTTP 402.")
        assert failed.wait(3)
        return response(data["paginas_alvo"], [record(first)])

    monkeypatch.setattr(inc, "_task_steps", observed_steps)
    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaError, match="HTTP 402"): analyze(text)
    assert sorted(calls) == [1, 11]
    with checkpoint(text) as store:
        state = store.load()
        inc._validated_state(state, {n: source(20).split(f"## Página {n}")[1].split("## Página ")[0] for n in range(1, 21)})
        assert [row["targets"][0] for row in state["completed"]] == [11]
        assert [row["targets"][0] for row in state["pending"]] == [1, 6, 16]


def test_storage_failure_prevents_peer_promotion_and_further_requests(monkeypatch):
    text = source(20); both = threading.Barrier(2); failed = threading.Event(); calls = []
    save = storage.AnalysisCheckpoint.save

    def failed_save(store, state):
        if any(row["targets"][0] == 1 for row in state["completed"]):
            failed.set(); raise storage.CheckpointStorageError("Falha sintética ao persistir.")
        save(store, state)

    def request(messages, *_):
        data = request_data(messages); first = data["paginas_alvo"][0]; calls.append(first)
        both.wait(3)
        if first == 11: assert failed.wait(3)
        return response(data["paginas_alvo"], [record(first)])

    monkeypatch.setattr(storage.AnalysisCheckpoint, "save", failed_save)
    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(storage.CheckpointStorageError): analyze(text)
    assert sorted(calls) == [1, 11]
    with checkpoint(text) as store: assert not store.load()["completed"]


def test_rollover_and_retries_rebase_on_peer_progress_without_duplicate_calls(monkeypatch):
    text = source(20); markers = list(v.PAGE.finditer(text))
    pages = {i + 1: text[m.end():markers[i + 1].start() if i + 1 < len(markers) else len(text)] for i, m in enumerate(markers)}
    counts = {}; gate = threading.Barrier(2)
    monkeypatch.setattr(inc, "MAX_CONTINUATIONS", 1)
    monkeypatch.setattr(inc, "TRANSPORT_RETRY_DELAYS", (0, 0))

    def request(messages, *_):
        data = request_data(messages); first = data["paginas_alvo"][0]
        counts[first] = counts.get(first, 0) + 1
        gate.wait(3)
        if counts[first] == 1: raise v.TransientAnvisaError("IA: falha de conexão sintética.")
        suffix = "A" if counts[first] == 2 else "B"
        ids = [record(first)["id"]] if suffix == "A" else [record(first)["id"], record(first, "B")["id"]]
        return response(data["paginas_alvo"], [record(first, suffix)], partial=True, ids=ids)

    monkeypatch.setattr(v, "_request", request)
    with checkpoint(text) as store:
        with pytest.raises(parallel.AnalysisSampleComplete):
            inc.run(pages, [], "chave-ficticia", None, None, store,
                    sample_budget={tuple(range(1, 6)): 3, tuple(range(11, 16)): 3})
        state = store.load(); inc._validated_state(state, pages)
        assert [len(row["records"]) for row in state["pending"]] == [2, 0, 2, 0]
    assert counts == {1: 3, 11: 3}


def test_parallel_checkpoint_migration_preserves_out_of_order_progress(monkeypatch):
    text = source(15); old = storage.AnalysisCheckpoint(migration.legacy_identity(hashlib.sha256(text.encode()).hexdigest(), 15, 9), "protocolo-sintetico")
    pages = {n: f"\nEvento A{n}\nEvento B{n}\nEvento C{n}\n" for n in range(1, 16)}
    task = inc._tasks(list(range(1, 6)), pages)[0]
    # A origem anterior é prefixada; o destino admite posteriores concluídos na execução seguinte.
    state = {"schema": 3, "completed": [], "pending": [task] + inc._tasks(list(range(6, 11)), pages) + inc._tasks(list(range(11, 16)), pages)}
    with old: old.save(state)
    before = old.path.read_bytes(); result = migration.migrate(text, "protocolo-sintetico", old.key)
    with checkpoint(text) as store: assert store.load()["pending"] == state["pending"]
    assert old.path.read_bytes() == before and result["status"] == "migrado"


def test_http_report_is_only_generated_after_all_parallel_batches_finish(monkeypatch):
    text = source(20); gate = threading.Barrier(2); counts = []
    monkeypatch.setenv("INTERNAL_API_TOKEN", "token-ficticio")
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-ficticia")

    def request(messages, *_):
        data = request_data(messages); first = data["paginas_alvo"][0]; counts.append(first)
        if first in {1, 11}: gate.wait(3)
        return response(data["paginas_alvo"], [record(first)])

    monkeypatch.setattr(v, "_request", request)
    result = TestClient(app).post('/v1/analyze-anvisa-v8', headers={"X-Internal-Token": "token-ficticio"}, json={
        "markdown": text, "page_count": 20, "markdown_sha256": hashlib.sha256(text.encode()).hexdigest(), "source_filename": "sintetico.pdf"})
    assert result.status_code == 200
    assert sorted(counts) == [1, 6, 11, 16]
    assert result.json()["report_context"]["pages_analyzed"] == 20
    assert result.json()["report_context"]["analysis_checkpoint"]["chamadas_simultaneas_maximas"] == 2


def test_retry_wait_releases_api_slot_for_third_independent_batch(monkeypatch):
    third_started = threading.Event()
    pair = threading.Barrier(2)
    calls, packets = {}, []
    active = maximum = 0
    lock = threading.Lock()
    monkeypatch.setattr(inc, "TRANSPORT_RETRY_DELAYS", (0.03, 0.03))

    def request(messages, *_):
        nonlocal active, maximum
        data = request_data(messages); first = data["paginas_alvo"][0]
        with lock:
            calls[first] = calls.get(first, 0) + 1
            number = calls[first]
            active += 1; maximum = max(maximum, active)
        try:
            if first == 1:
                packets.append(copy.deepcopy(messages))
                if number == 1:
                    pair.wait(3)
                    raise v.TransientAnvisaError("IA: conexão sintética indisponível.")
                assert third_started.is_set()
            elif first == 11:
                pair.wait(3)
                assert third_started.wait(3), "A espera de retry não deve reservar uma vaga da API."
            elif first == 21:
                third_started.set()
            return response(data["paginas_alvo"], [record(first)])
        finally:
            with lock: active -= 1

    monkeypatch.setattr(v, "_request", request)
    rows, coverage = analyze(source(30))
    assert maximum == 2 and calls[1] == 2 and packets[0] == packets[1]
    assert [r["id"] for r in rows] == [record(n)["id"] for n in (1, 6, 11, 16, 21, 26)]
    assert coverage["processamento_incremental"]["retentativas_transporte"] == 1


def test_blocked_context_allows_third_independent_batch_without_overlap(monkeypatch):
    third_started = threading.Event()
    peer_committed = threading.Event()
    save = storage.AnalysisCheckpoint.save
    calls = {}

    def observed_save(store, state):
        save(store, state)
        if any(row["targets"][0] == 11 for row in state["completed"]):
            peer_committed.set()

    def request(messages, *_):
        data = request_data(messages); first = data["paginas_alvo"][0]
        calls[first] = calls.get(first, 0) + 1
        if first == 1:
            if calls[first] == 1:
                return {"contexto_necessario": [11]}
            assert peer_committed.is_set(), "A ampliação ainda precisa aguardar a chamada sobreposta."
            assert 11 in data["contexto_recuperado"]["paginas_nesta_chamada"]
        elif first == 11:
            assert third_started.wait(3), "Outro lote independente deve ocupar a vaga livre."
        elif first == 21:
            third_started.set()
        return response(data["paginas_alvo"], [record(first)])

    monkeypatch.setattr(storage.AnalysisCheckpoint, "save", observed_save)
    monkeypatch.setattr(v, "_request", request)
    rows, coverage = analyze(source(30))
    assert len(rows) == 6 and calls[1] == 2
    assert coverage["processamento_incremental"]["chamadas_simultaneas_maximas"] == 2


def test_retry_budget_is_not_renewed_by_third_batch_progress(monkeypatch):
    third_started = threading.Event()
    pair = threading.Barrier(2)
    calls = {}
    monkeypatch.setattr(inc, "TRANSPORT_RETRY_DELAYS", (0.03,))

    def request(messages, *_):
        data = request_data(messages); first = data["paginas_alvo"][0]
        calls[first] = calls.get(first, 0) + 1
        if first == 1:
            if calls[first] == 1: pair.wait(3)
            else: assert third_started.is_set()
            raise v.TransientAnvisaError("IA: erro temporário sintético persistente.")
        if first == 11:
            pair.wait(3)
            assert third_started.wait(3)
        if first == 21: third_started.set()
        return response(data["paginas_alvo"], [record(first)])

    monkeypatch.setattr(v, "_request", request)
    text = source(30)
    with pytest.raises(v.AnvisaError, match="após 2 tentativas"):
        analyze(text)
    assert calls[1] == 2 and calls[21] == 1
    with checkpoint(text) as saved:
        state = saved.load()
        assert any(row["targets"][0] == 1 for row in state["pending"])
        assert any(row["targets"][0] == 21 for row in state["completed"])


def test_dynamic_queue_migration_keeps_adaptive_policy_and_context():
    text = source(15)
    pages = {n: f"\nEvento A{n}\nEvento B{n}\nEvento C{n}\n" for n in range(1, 16)}
    old = storage.AnalysisCheckpoint(migration.legacy_identity(hashlib.sha256(text.encode()).hexdigest(), 15, 11), "protocolo-sintetico")
    tasks = [inc._tasks(list(range(n, n + 5)), pages)[0] for n in (1, 6, 11)]
    tasks[0]["group_policy"] = {"limit": 16, "cooldown": 1, "increases": 2, "reductions": 0}
    state = {"schema": 3, "completed": [], "pending": tasks}
    with old: old.save(state)
    before = old.path.read_bytes()
    result = migration.migrate(text, "protocolo-sintetico", old.key)
    with checkpoint(text) as saved:
        migrated = saved.load()
        assert migrated["pending"] == tasks
    assert old.path.read_bytes() == before and result["status"] == "migrado"
