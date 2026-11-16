"""Transporte reduzido sem promover, apagar ou alterar dados por omissão."""

import copy
import hashlib
import json

import pytest

from infra.report_renderer import anvisa_v8 as v, context_window as ctx, incremental as inc, transport as wire
from infra.report_renderer import analysis_checkpoint as storage, migrate_checkpoint as migration
from tests.report_renderer.test_incremental import source, record, full_record, response, analyze, checkpoint


def task_with_inventory():
    task = inc._tasks([1], {1: "\nEvento A1\nEvento B1\n"})[0]
    task["records"] = [record()]
    task["continuation"] = {key: value for key, value in response([1], [record()], partial=True).items() if key != "registros"}
    return task


def delta(previous, blocks):
    return {"base_sha256": wire.inventory_view(previous)["base_sha256"], "blocos": blocks}


def test_index_used_for_small_completed_card_and_source_unchanged():
    task = task_with_inventory()
    pages = {1: "\nEvento A1\nEvento B1\n"}
    before = storage.encode(task)
    packet, window = ctx.build(task, pages)
    assert packet["continuidade"]["registros_preservados"] == []
    assert packet["continuidade"]["indice_registros_preservados"] == [ctx.record_index(record())]
    assert packet["markdown_documental"] == "## Página 1" + pages[1]
    assert packet["continuidade"]["inventario_preservado"]["base_sha256"] == delta(wire.inventory(task), [])["base_sha256"]
    assert window == {1} and storage.encode(task) == before


def test_deduplication_preserves_every_value_and_only_reduces_repeated_objects():
    evidence = {"pagina": 1, "trecho_literal": "Texto sintético literal com espaços e\nquebras. " * 8, "localizador": "Sintético"}
    original = {"registros": [{"evidencias": [evidence]} for _ in range(8)], "outro": {"valor": "inalterado"}}
    saved = copy.deepcopy(original)
    packed = wire.pack(original)
    assert len(v._json(packed)) < len(v._json(original))
    assert len(packed["evidencias_compartilhadas"]) == 1
    restored = wire.expand({k: value for k, value in packed.items() if k != "evidencias_compartilhadas"}, packed["evidencias_compartilhadas"])
    assert restored == saved == original
    assert wire.pack({"evidencias": [evidence]}) == {"evidencias": [evidence]}


def test_delta_updates_only_explicit_fields_preserving_all_units_and_original():
    previous = wire.inventory(task_with_inventory())
    previous[0]["localizador"] = "Bloco sintético completo."
    previous[0]["unidades_fonte"].append({"ids_eventos": ["ANV8-P1-B"], "valor_documental": "Preservar integralmente."})
    saved = copy.deepcopy(previous)
    patch = delta(previous, [{"id": "B1", "campos": {"estado_revisao": "revisada", "pendencias": []}}])
    merged = wire.merge_inventory(previous, patch)
    assert merged[0]["unidades_fonte"] == previous[0]["unidades_fonte"]
    assert merged[0]["localizador"] == previous[0]["localizador"]
    assert merged[0]["estado_revisao"] == "revisada" and not merged[0]["pendencias"]
    assert previous == saved and wire.merge_inventory(previous, delta(previous, [])) == saved


@pytest.mark.parametrize("violation", ["base", "unknown_block", "unknown_unit", "duplicate_block", "duplicate_unit", "drop_ids", "replace_units"])
def test_invalid_delta_rejected_atomically(violation):
    previous = wire.inventory(task_with_inventory())
    previous[0]["unidades_fonte"][0]["evidencias"] = record()["evidencias"]
    block = {"id": "B1", "campos": {}, "unidades": [{"id": "B1-U1", "campos": {}}]}
    patch = delta(previous, [block])
    if violation == "base": patch["base_sha256"] = "0" * 64
    if violation == "unknown_block": block["id"] = "B3"
    if violation == "unknown_unit": block["unidades"][0]["id"] = "B1-U3"
    if violation == "duplicate_block": patch["blocos"].append(copy.deepcopy(block))
    if violation == "duplicate_unit": block["unidades"].append(copy.deepcopy(block["unidades"][0]))
    if violation == "drop_ids": block["unidades"][0]["campos"]["ids_eventos"] = []
    if violation == "replace_units": block["campos"]["unidades_fonte"] = []
    saved = storage.encode(previous)
    with pytest.raises(v.StructureValidationError): wire.merge_inventory(previous, patch)
    assert storage.encode(previous) == saved


@pytest.mark.parametrize("violation", ["unknown_ref", "override", "quote", "page", "chain", "mixed"])
def test_evidence_references_cannot_bypass_literal_validation_or_namespace(violation):
    task = task_with_inventory()
    result = response([1], [record()])
    result["registros"][0]["evidencias"] = [{wire.REF: "N1"}]
    result["evidencias_novas"] = {"N1": record()["evidencias"][0]}
    if violation == "unknown_ref": result["registros"][0]["evidencias"] = [{wire.REF: "E404"}]
    if violation == "override": result["evidencias_novas"] = {"E1": record()["evidencias"][0]}
    if violation == "quote": result["evidencias_novas"]["N1"] = {"pagina": 1, "trecho_literal": "Trecho inventado."}
    if violation == "page": result["evidencias_novas"]["N1"] = {"pagina": 2, "trecho_literal": "Evento A1"}
    if violation == "chain": result["evidencias_novas"]["N1"][wire.REF] = "N2"
    if violation == "mixed": result["registros"][0]["evidencias"][0]["pagina"] = 1
    with pytest.raises(v.AnvisaError): wire.decode(result, task, {}, {1: "\nEvento A1\n"}, {1})


def test_full_analysis_accepts_two_deltas_and_shared_evidence_without_loss(monkeypatch):
    calls = []

    def request(messages, *_):
        data = json.loads(messages[-1]["content"])
        calls.append(data)
        first = len(calls) == 1
        row = full_record(suffix="A" if first else "B")
        quote = row["evidencias"][0]
        for _, field in v._walk_paths(row):
            if "evidencias" in field: field["evidencias"] = [{wire.REF: "N1"}]
        inventory = data["continuidade"]["inventario_preservado"]
        if first:
            changes = [{"id": "B1", "campos": {"estado_revisao": "pendente", "pendencias": ["Revisar B1."]},
                        "unidades": [{"id": "B1-U1", "campos": {"ids_eventos": ["ANV8-P1-A", "ANV8-P1-B"]}}]}]
        else:
            assert data["continuidade"]["indice_registros_preservados"] == [ctx.record_index(full_record())]
            changes = [{"id": "B1", "campos": {"estado_revisao": "revisada", "pendencias": []}}]
        return v.ModelResult({"paginas": response([1], partial=first)["paginas"], "registros": [row],
                              "reconciliacao_delta": {"base_sha256": inventory["base_sha256"], "blocos": changes},
                              "evidencias_novas": {"N1": quote}}, "gen-sintetico", {"completion_tokens": 10})

    monkeypatch.setattr(v, "_request", request)
    found, coverage = analyze(source())
    assert found == [full_record(), full_record(suffix="B")]
    assert len(calls) == 2 and coverage["evidencias_literais_conferidas"] == 12
    with checkpoint(source()) as saved:
        state = saved.load()
        assert not state["pending"]
        assert all(wire.REF not in item for _, item in v._walk_paths(state))
    monkeypatch.setattr(v, "_request", lambda *_: pytest.fail("Retomada concluída não chama a IA."))
    assert analyze(source())[0] == found


def test_rejected_references_keep_diagnostic_and_only_one_correction(monkeypatch):
    calls = []

    def request(messages, *_):
        data = json.loads(messages[-1]["content"])
        calls.append(data)
        if len(calls) == 2:
            assert data["diagnostico_validacao"]["motivo"] == "referencia_evidencia_invalida"
            assert "referencia_evidencia_rejeitada" in data["resposta_anterior"]["registros"][0]["evidencias"][0]
        result = response([1], [record()])
        result["registros"][0]["evidencias"] = [{wire.REF: "E404"}]
        return result

    monkeypatch.setattr(v, "_request", request)
    with pytest.raises(v.StructureValidationError): analyze(source())
    assert len(calls) == 2
    with checkpoint(source()) as saved:
        assert not saved.load()["pending"][0]["records"]


def test_expansion_rejects_amplification_before_copying(monkeypatch):
    monkeypatch.setattr(wire, "MAX_EXPANDED_BYTES", 1000)
    with pytest.raises(v.StructureValidationError, match="expansao_excessiva"):
        wire.expand([{wire.REF: "E1"}] * 100, {"E1": {"pagina": 1, "trecho_literal": "X" * 100}})


def test_correction_view_cannot_redefine_existing_or_rebind_unknown_reference():
    known = {"pagina": 1, "trecho_literal": "Evento A1"}
    wrong = {"pagina": 1, "trecho_literal": "Evento B1"}
    result = {"evidencias_novas": {"E1": wrong},
              "registros": [{"evidencias": [{wire.REF: "E1"}, {wire.REF: "E404"}]}]}
    restored = wire.rejected_view(result, {"evidencias_compartilhadas": {"E1": known}})
    assert restored["registros"][0]["evidencias"][0] == known
    unknown = restored["registros"][0]["evidencias"][1]
    assert unknown["referencia_evidencia_rejeitada"]["id"] == "E404"
    assert wire.expand(restored, {"E404": wrong}) == restored


@pytest.mark.parametrize("version", [7, 8])
def test_recovery_checkpoint_migration_preserves_every_complete_and_pending_value(version):
    text = source()
    old = storage.AnalysisCheckpoint(migration.legacy_identity(hashlib.sha256(text.encode()).hexdigest(), 1, version), "protocolo-sintetico")
    task = task_with_inventory()
    state = {"schema": 3, "completed": [], "pending": [task]}
    with old: old.save(state)
    original = old.path.read_bytes()
    result = migration.migrate(text, "protocolo-sintetico", old.key)
    with checkpoint(text) as current:
        migrated = current.load()
        assert migrated["completed"] == state["completed"] and migrated["pending"] == state["pending"]
    assert result["status"] == "migrado" and old.path.read_bytes() == original
    assert migration.migrate(text, "protocolo-sintetico", old.key)["status"] == "ja_migrado"
