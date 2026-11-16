"""Grupos de oito e evidências incrementais com integridade preservada."""

import copy
import json

import pytest

from infra.report_renderer import anvisa_v8 as v, incremental as inc, context_window as ctx, transport as wire
from tests.report_renderer.test_incremental import record, full_record, response, analyze, checkpoint, request_data
from tests.report_renderer.test_transport import task_with_inventory, delta


@pytest.mark.parametrize("form", ["adicionar_evidencias", "campos", "somente_adicao"])
def test_inventory_evidence_additions_preserve_original_order_metadata_and_are_idempotent(form):
    previous = wire.inventory(task_with_inventory())
    old = {"pagina": 1, "trecho_literal": "Evento A1", "localizador": "Original completo."}
    new = {"pagina": 1, "trecho_literal": "Evento B1"}
    previous[0]["unidades_fonte"][0]["evidencias"] = [old]
    change = {"id": "B1-U1", "campos": {}}
    if form == "campos": change["campos"]["evidencias"] = [new, old, new]
    else: change["adicionar_evidencias"] = [new, old, new]
    if form == "somente_adicao": change.pop("campos")
    saved = copy.deepcopy(previous)
    patch = delta(previous, [{"id": "B1", "campos": {}, "unidades": [change]}])
    merged = wire.merge_inventory(previous, patch)
    assert merged[0]["unidades_fonte"][0]["evidencias"] == [old, new]
    patch["base_sha256"] = wire.inventory_view(merged)["base_sha256"]
    assert wire.merge_inventory(merged, patch) == merged and previous == saved


def test_empty_evidence_delta_never_erases_existing_evidence():
    previous = wire.inventory(task_with_inventory())
    previous[0]["unidades_fonte"][0]["evidencias"] = record()["evidencias"]
    patch = delta(previous, [{"id": "B1", "campos": {}, "unidades": [
        {"id": "B1-U1", "campos": {"evidencias": []}}]}])
    assert wire.merge_inventory(previous, patch) == previous


@pytest.mark.parametrize("bad", [None, "texto", [None], [{"pagina": 1}], [{"trecho_literal": "Evento A1"}]])
def test_malformed_evidence_addition_does_not_modify_any_previous_unit(bad):
    previous = wire.inventory(task_with_inventory())
    previous[0]["unidades_fonte"][0]["evidencias"] = record()["evidencias"]
    patch = delta(previous, [{"id": "B1", "campos": {}, "unidades": [
        {"id": "B1-U1", "campos": {}, "adicionar_evidencias": bad}]}])
    saved = copy.deepcopy(previous)
    with pytest.raises(v.StructureValidationError, match="delta_evidencias_invalidas"):
        wire.merge_inventory(previous, patch)
    assert previous == saved


def test_ambiguous_addition_and_block_boundary_removal_remain_rejected():
    previous = wire.inventory(task_with_inventory())
    previous[0]["limites"] = {"inicio": record()["evidencias"][0]}
    patch = delta(previous, [{"id": "B1", "campos": {"evidencias": []}, "adicionar_evidencias": []}])
    with pytest.raises(v.StructureValidationError, match="delta_evidencias_ambiguas"):
        wire.merge_inventory(previous, patch)
    patch = delta(previous, [{"id": "B1", "campos": {"limites": {}}}])
    with pytest.raises(v.StructureValidationError, match="delta_limites_invalidos"):
        wire.merge_inventory(previous, patch)


def test_shared_evidence_addition_expands_and_remains_subject_to_literal_validation():
    task = task_with_inventory()
    previous = wire.inventory(task)
    previous[0]["unidades_fonte"][0]["evidencias"] = record()["evidencias"]
    patch = delta(previous, [{"id": "B1", "campos": {}, "unidades": [
        {"id": "B1-U1", "campos": {}, "adicionar_evidencias": [{wire.REF: "N1"}]}]}])
    result = {**response([1], [record()], partial=True), "evidencias_novas": {"N1": record(suffix="B")["evidencias"][0]}}
    result.pop("reconciliacao_anexos"); result["reconciliacao_delta"] = patch
    decoded = wire.decode(result, task, {}, {1: "Evento A1\nEvento B1"}, {1})
    evidence = decoded["reconciliacao_anexos"][0]["unidades_fonte"][0]["evidencias"]
    assert evidence == record()["evidencias"] + record(suffix="B")["evidencias"]
    result["evidencias_novas"]["N1"]["trecho_literal"] = "Não existe na fonte."
    with pytest.raises(v.EvidenceValidationError):
        wire.decode(result, task, {}, {1: "Evento A1\nEvento B1"}, {1})


def test_eight_complete_cards_are_validated_saved_and_reused_without_another_call(monkeypatch):
    rows = [full_record(1, f"E{i}") for i in range(8)]
    text = "## Página 1\n" + "".join(f"Evento E{i}1\n" for i in range(8))
    calls = []

    def request(messages, *_):
        data = request_data(messages); calls.append(data)
        assert data["continuidade"]["limite_eventos_resposta"] == 8
        assert data["continuidade"]["limite_novos_eventos"] == 8
        return response([1], rows)

    monkeypatch.setattr(v, "_request", request)
    assert analyze(text)[0] == rows and len(calls) == 1
    monkeypatch.setattr(v, "_request", lambda *_: pytest.fail("Checkpoint completo não deve repetir IA."))
    assert analyze(text)[0] == rows


def test_ninth_card_is_rejected_and_correction_keeps_the_eight_card_limit(monkeypatch):
    rows = [record(1, f"E{i}") for i in range(9)]
    text = "## Página 1\n" + "".join(f"Evento E{i}1\n" for i in range(9))
    calls = []

    def request(messages, *_):
        data = request_data(messages); calls.append(data)
        assert data["continuidade"]["limite_eventos_resposta"] == 8
        if len(calls) == 2:
            assert data["diagnostico_validacao"]["motivo"] == "limite_eventos_resposta_excedido"
        return response([1], rows)

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.StructureValidationError, match="limite_eventos_resposta_excedido"):
        analyze(text)
    assert len(calls) == 2
    with checkpoint(text) as saved:
        assert not saved.load()["pending"][0]["records"]


def test_eight_pending_reviews_are_prioritized_before_the_remaining_review(monkeypatch):
    drafts = [full_record(1, f"E{i}", pending=True) for i in range(9)]
    text = "## Página 1\n" + "".join(f"Evento E{i}1\n" for i in range(9))
    pages = {1: text.split("## Página 1")[1]}
    task = inc._tasks([1], pages)[0]; task["drafts"] = drafts
    task["continuation"] = {k: value for k, value in response([1], drafts, partial=True).items() if k != "registros"}
    with checkpoint(text) as saved: saved.save({"schema": 3, "completed": [], "pending": [task]})
    calls = []

    def request(messages, *_):
        data = request_data(messages); calls.append(data)
        expected = drafts[:8] if len(calls) == 1 else drafts[8:]
        assert data["continuidade"]["ids_para_revisar"] == [row["id"] for row in expected]
        assert data["continuidade"]["limite_novos_eventos"] == 0
        done = [full_record(1, f"E{i}") for i in (range(8) if len(calls) == 1 else [8])]
        return response([1], done, partial=len(calls) == 1, ids=[row["id"] for row in drafts])

    monkeypatch.setattr(v, "_request", request)
    assert analyze(text)[0] == [full_record(1, f"E{i}") for i in range(9)]
    assert len(calls) == 2
