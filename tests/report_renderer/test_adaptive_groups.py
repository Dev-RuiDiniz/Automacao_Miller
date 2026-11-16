"""Adaptação só após sucesso, com retomada e sem relaxar integridade."""

import copy
import hashlib
import threading

import pytest

from infra.report_renderer import anvisa_v8 as v, incremental as inc, adaptive_groups as policy
from infra.report_renderer import context_window as ctx, analysis_checkpoint as storage, parallel_batches as parallel
from infra.report_renderer import migrate_checkpoint as migration
from tests.report_renderer.test_incremental import record, full_record, response, analyze, checkpoint, request_data


@pytest.fixture(autouse=True)
def adaptation(monkeypatch):
    monkeypatch.setattr(policy, "ENABLED", True)


def compact_source(count=36):
    return "## Página 1\n" + "".join(f"Evento E{i}1\n" for i in range(count))


def reply(rows, total, *, partial=True):
    return v.ModelResult(response([1], rows, partial=partial,
        ids=[record(1, f"E{i}")["id"] for i in range(total)]), "gen-sintetico",
        {"completion_tokens": len(rows) * 100, "duracao_requisicao_segundos": len(rows) * 2})


def test_compact_groups_grow_8_12_16_and_complete_without_losing_any_record(monkeypatch):
    text = compact_source(); rows = [record(1, f"E{i}") for i in range(36)]; limits = []; offset = 0

    def request(messages, *_):
        nonlocal offset
        data = request_data(messages); limit = data["continuidade"]["limite_eventos_resposta"]; limits.append(limit)
        selected = rows[offset:offset + limit]; offset += len(selected)
        return reply(selected, 36, partial=offset < 36)

    monkeypatch.setattr(v, "_request", request)
    assert analyze(text)[0] == rows
    assert limits == [8, 12, 16]
    with checkpoint(text) as store:
        saved = store.load(); assert not saved["pending"]
        assert saved["completed"][0]["group_policy"]["increases"] == 2
    monkeypatch.setattr(v, "_request", lambda *_: pytest.fail("Lote completo não deve repetir IA."))
    assert analyze(text)[0] == rows


def test_saved_policy_resumes_at_16_without_repeating_accepted_groups(monkeypatch):
    text = compact_source(); rows = [record(1, f"E{i}") for i in range(36)]; count = 0

    def request(messages, *_):
        nonlocal count
        count += 1
        if count == 3: raise v.AnvisaError("IA: interrupção sintética.")
        return reply(rows[:8] if count == 1 else rows[8:20], 36)

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaError): analyze(text)
    with checkpoint(text) as store:
        task = store.load()["pending"][0]
        assert task["records"] == rows[:20] and task["group_policy"]["limit"] == 16

    def resume(messages, *_):
        assert request_data(messages)["continuidade"]["limite_eventos_resposta"] == 16
        return reply(rows[20:], 36, partial=False)

    monkeypatch.setattr(v, "_request", resume)
    assert analyze(text)[0] == rows


def test_retry_reuses_the_same_larger_packet_without_growing_on_failure(monkeypatch):
    text = compact_source(); rows = [record(1, f"E{i}") for i in range(36)]; calls = []; sleeps = []
    monkeypatch.setattr(inc.time, "sleep", sleeps.append)

    def request(messages, *_):
        data = request_data(messages); calls.append(data)
        if len(calls) == 1: return reply(rows[:8], 36)
        if len(calls) == 2: raise v.TransientAnvisaError("IA: conexão sintética.")
        if len(calls) == 3: return reply(rows[8:20], 36)
        return reply(rows[20:], 36, partial=False)

    monkeypatch.setattr(v, "_request", request)
    assert analyze(text)[0] == rows
    assert calls[1] == calls[2] and sleeps == [5]
    assert [c["continuidade"]["limite_eventos_resposta"] for c in calls] == [8, 12, 12, 16]


def test_output_truncation_reduces_group_and_preserves_whole_source(monkeypatch):
    text = compact_source(16); rows = [record(1, f"E{i}") for i in range(16)]; limits = []; offset = 0

    def request(messages, *_):
        nonlocal offset
        data = request_data(messages); size = data["continuidade"]["limite_eventos_resposta"]; limits.append(size)
        assert data["markdown_documental"] == text
        if len(limits) == 1: raise v.AnvisaOutputLimit("IA: resposta truncada sintética.")
        part = rows[offset:offset + size]; offset += len(part)
        return reply(part, 16, partial=offset < 16)

    monkeypatch.setattr(v, "_request", request)
    assert analyze(text)[0] == rows
    assert limits == [8, 4, 4, 4, 8]
    with checkpoint(text) as store: assert store.load()["completed"][0]["group_policy"]["reductions"] == 1


def test_mandatory_context_limit_is_not_bypassed_by_adaptation(monkeypatch):
    text = compact_source(8)
    monkeypatch.setattr(ctx, "MAX_DATA_BYTES", 1)
    monkeypatch.setattr(v, "_request", lambda *_: pytest.fail("Não chamar a IA quando a fonte não cabe."))
    with pytest.raises(v.AnvisaOutputLimit): analyze(text)
    with checkpoint(text) as store: assert "group_policy" not in store.load()["pending"][0]


def test_correction_freezes_limit_and_next_group_returns_to_8(monkeypatch):
    text = compact_source(); rows = [record(1, f"E{i}") for i in range(36)]; calls = []

    def request(messages, *_):
        data = request_data(messages); calls.append(data); n = len(calls)
        if n == 1: return reply(rows[:8], 36)
        if n == 2:
            bad = copy.deepcopy(rows[8:20]); bad[0]["evidencias"][0]["trecho_literal"] = "Trecho inexistente."
            return reply(bad, 36)
        if n == 3:
            assert data["diagnostico_validacao"] and data["resposta_anterior"]
            return reply(rows[8:20], 36)
        if n == 4: return reply(rows[20:28], 36)
        return reply(rows[28:], 36, partial=False)

    monkeypatch.setattr(v, "_request", request)
    assert analyze(text)[0] == rows
    assert [c["continuidade"]["limite_eventos_resposta"] for c in calls] == [8, 12, 12, 8, 8]


def test_output_limit_during_correction_does_not_renew_correction_or_discard_group(monkeypatch):
    text = compact_source(); rows = [record(1, f"E{i}") for i in range(36)]; calls = []

    def request(messages, *_):
        calls.append(request_data(messages))
        if len(calls) == 1: return reply(rows[:8], 36)
        if len(calls) == 2:
            bad = copy.deepcopy(rows[8:20]); bad[0]["evidencias"][0]["trecho_literal"] = "Inexistente."
            return reply(bad, 36)
        raise v.AnvisaOutputLimit("IA: correção truncada sintética.")

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaOutputLimit): analyze(text)
    assert len(calls) == 3 and calls[-1]["continuidade"]["limite_eventos_resposta"] == 12
    with checkpoint(text) as store:
        task = store.load()["pending"][0]; assert task["records"] == rows[:8] and task["group_policy"]["limit"] == 12


def test_full_cards_after_compact_groups_return_to_conservative_size(monkeypatch):
    text = compact_source(32); rows = [record(1, f"E{i}") for i in range(8)] + [full_record(1, f"E{i}") for i in range(8, 32)]
    limits = []; offset = 0

    def request(messages, *_):
        nonlocal offset
        data = request_data(messages); limits.append(data["continuidade"]["limite_eventos_resposta"])
        assert data["continuidade"]["limite_fichas_completas"] <= 8
        part = rows[offset:offset + 8]; offset += len(part)
        return reply(part, 32, partial=offset < 32)

    monkeypatch.setattr(v, "_request", request)
    assert analyze(text)[0] == rows and limits == [8, 12, 8, 8]


def test_server_rejects_more_than_8_full_cards_even_if_total_limit_is_16():
    with pytest.raises(v.StructureValidationError, match="grupo_com_fichas_completas_excedido"):
        inc._validate_incoming([full_record(1, f"E{i}") for i in range(9)], [1], {1}, {1: "Fonte sintética."}, 16)


def test_expanded_compact_cards_that_stop_being_short_return_to_8():
    task = {"drafts": [], "group_policy": {"limit": 16, "cooldown": 0, "increases": 2, "reductions": 0}}
    rows = [dict(record(1, f"E{i}"), justificativa="Texto sintético preservado. " * 180) for i in range(16)]
    original = copy.deepcopy(rows)
    result = v.ModelResult({}, "gen-sintetico", {"completion_tokens": 1000, "duracao_requisicao_segundos": 1})
    policy.accepted(task, 16, rows, result)
    assert task["group_policy"]["limit"] == 8 and rows == original


def test_smaller_target_children_keep_the_reduced_policy(monkeypatch):
    text = compact_source(8) + compact_source(8).replace("## Página 1", "## Página 2").replace("E01", "E02")
    limits = []

    def request(messages, *_):
        limits.append(request_data(messages)["continuidade"]["limite_eventos_resposta"])
        raise v.AnvisaOutputLimit("IA: saída excessiva sintética.")

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.AnvisaOutputLimit): analyze(text)
    assert limits == [8, 4, 2, 1, 1]
    with checkpoint(text) as store:
        assert [entry["group_policy"]["limit"] for entry in store.load()["pending"]] == [1, 1]


def test_oversized_full_group_can_be_corrected_in_8_without_losing_reserved_units(monkeypatch):
    text = compact_source(); rows = [record(1, f"E{i}") for i in range(20)] + [full_record(1, f"E{i}") for i in range(20, 36)]; calls = []

    def request(messages, *_):
        data = request_data(messages); calls.append(data); n = len(calls)
        if n == 1: return reply(rows[:8], 36)
        if n == 2: return reply(rows[8:20], 36)
        if n == 3: return reply(rows[20:], 36)
        if n == 4:
            assert data["diagnostico_validacao"]["motivo"] == "grupo_com_fichas_completas_excedido"
            return reply(rows[20:28], 36)
        return reply(rows[28:], 36, partial=False)

    monkeypatch.setattr(v, "_request", request)
    assert analyze(text)[0] == rows
    assert [c["continuidade"]["limite_eventos_resposta"] for c in calls] == [8, 12, 16, 16, 8]


@pytest.mark.parametrize("bad", [{"limit": 32, "cooldown": 0, "increases": 0, "reductions": 0},
    {"limit": 16, "cooldown": 3, "increases": 0, "reductions": 0},
    {"limit": True, "cooldown": 0, "increases": 0, "reductions": 0}])
def test_corrupt_policy_stops_before_another_paid_call(monkeypatch, bad):
    text = compact_source(); task = inc._tasks([1], {1: text.split("## Página 1")[1]})[0]; task["group_policy"] = bad
    with checkpoint(text) as store: store.save({"schema": 3, "completed": [], "pending": [task]})
    monkeypatch.setattr(v, "_request", lambda *_: pytest.fail("Estado corrompido não deve consumir IA."))
    with pytest.raises(storage.CheckpointStorageError): analyze(text)


def test_parallel_batches_keep_independent_group_policies(monkeypatch):
    monkeypatch.setattr(inc, "MAX_PARALLEL_BATCHES", 2)
    pages = {n: "\n" + "".join(f"Evento E{i}{n}\n" for i in range(36)) for n in range(1, 21)}
    text = "".join(f"## Página {n}{body}" for n, body in pages.items()); gate = threading.Barrier(2); offsets = {1: 0, 11: 0}; limits = {1: [], 11: []}

    def request(messages, *_):
        data = request_data(messages); page = data["paginas_alvo"][0]; limit = data["continuidade"]["limite_eventos_resposta"]; limits[page].append(limit)
        gate.wait(3); factory = record if page == 1 else full_record
        found = [factory(page, f"E{i}") for i in range(offsets[page], offsets[page] + limit)]; offsets[page] += limit
        return v.ModelResult(response(data["paginas_alvo"], found, partial=True,
            ids=[factory(page, f"E{i}")["id"] for i in range(36)]), "gen-sintetico",
            {"completion_tokens": len(found) * 100, "duracao_requisicao_segundos": 2})

    monkeypatch.setattr(v, "_request", request)
    with checkpoint(text) as store:
        with pytest.raises(parallel.AnalysisSampleComplete):
            inc.run(pages, [], "chave-ficticia", None, None, store,
                sample_budget={tuple(range(1, 6)): 2, tuple(range(11, 16)): 2})
        state = store.load(); inc._validated_state(state, pages)
        assert state["pending"][0]["group_policy"]["limit"] == 16
        assert state["pending"][2]["group_policy"]["limit"] == 8
    assert limits == {1: [8, 12], 11: [8, 8]}


def test_parallel_implementation_migrates_without_inserting_a_fake_measurement():
    text = compact_source(); task = inc._tasks([1], {1: text.split("## Página 1")[1]})[0]
    previous = {"schema": 3, "completed": [], "pending": [task]}
    old = storage.AnalysisCheckpoint(migration.legacy_identity(hashlib.sha256(text.encode()).hexdigest(), 1, 10), "protocolo-sintetico")
    with old: old.save(previous)
    raw = old.path.read_bytes(); result = migration.migrate(text, "protocolo-sintetico", old.key)
    with checkpoint(text) as store:
        saved = store.load(); assert saved["pending"] == previous["pending"]
        assert "group_policy" not in saved["pending"][0]
    assert result["status"] == "migrado" and old.path.read_bytes() == raw
