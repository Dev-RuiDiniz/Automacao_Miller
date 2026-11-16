"""Campos comuns são somente transporte; fichas e validações ficam integrais."""

import copy
import json

import pytest

from infra.report_renderer import anvisa_v8 as v, transport as wire
from tests.report_renderer.test_incremental import full_record, response, source, analyze, checkpoint
from tests.report_renderer.test_transport import task_with_inventory


def shared_response():
    first, second = full_record(), full_record(suffix="B")
    # Ato igual, objeto diferente: não há preenchimento nem herança implícita.
    second["ato"] = copy.deepcopy(first["ato"])
    original = response([1], [first, second])
    compact = copy.deepcopy(original)
    compact["campos_compartilhados"] = copy.deepcopy({"C1": first["ato"], "C2": first["entidades"]})
    for row in compact["registros"]:
        row["ato"] = {wire.FIELD_REF: "C1"}
        row["entidades"] = {wire.FIELD_REF: "C2"}
    return original, compact


def decode(result):
    return wire.decode(result, task_with_inventory(), {}, {1: "Evento A1\nEvento B1\n"}, {1})


def test_restores_identical_values_and_preserves_differences_without_mutation():
    original, compact = shared_response()
    before = copy.deepcopy(compact)
    restored = decode(compact)
    assert restored == original and compact == before
    v._validate_block(restored, [1], {1}, {1: "Evento A1\nEvento B1\n"})
    restored["registros"][0]["ato"]["valor"] = "Mutação isolada."
    assert restored["registros"][1]["ato"] == original["registros"][1]["ato"]


def test_shared_field_can_use_new_literal_evidence_references():
    original, compact = shared_response()
    quote = compact["campos_compartilhados"]["C1"]["evidencias"][0]
    compact["evidencias_novas"] = {"N1": quote}
    compact["campos_compartilhados"]["C1"]["evidencias"] = [{wire.REF: "N1"}]
    assert decode(compact) == original


@pytest.mark.parametrize("violation", ["unknown", "chain", "mixed", "id", "nested", "namespace", "dictionary", "scalar", "quote", "page", "records"])
def test_rejects_invalid_references_and_literal_failures(violation):
    _, compact = shared_response()
    row = compact["registros"][0]
    if violation == "unknown": row["ato"] = {wire.FIELD_REF: "C404"}
    if violation == "chain": compact["campos_compartilhados"]["C1"] = {wire.FIELD_REF: "C2"}
    if violation == "mixed": row["ato"]["valor"] = "Sobrescrita proibida."
    if violation == "id": row["id"] = {wire.FIELD_REF: "C1"}
    if violation == "nested": row["objeto"]["valor"] = {wire.FIELD_REF: "C1"}
    if violation == "namespace": compact["campos_compartilhados"]["E1"] = {}
    if violation == "dictionary": compact["campos_compartilhados"] = []
    if violation == "scalar": compact["campos_compartilhados"]["C1"] = "valor sem estrutura"
    if violation == "quote": compact["campos_compartilhados"]["C1"]["evidencias"][0]["trecho_literal"] = "Inventado."
    if violation == "page": compact["campos_compartilhados"]["C1"]["evidencias"][0]["pagina"] = 2
    if violation == "records": compact["registros"] = {"0": row}
    before = copy.deepcopy(compact)
    with pytest.raises(v.AnvisaError): decode(compact)
    assert compact == before


def test_expansion_budget_checked_before_copying_shared_objects(monkeypatch):
    original, compact = shared_response()
    monkeypatch.setattr(wire, "MAX_EXPANDED_BYTES", len(v._json(compact)) + 100)
    compact["campos_compartilhados"]["C1"]["valor"] = "X" * 10000
    with pytest.raises(v.StructureValidationError, match="expansao_excessiva"):
        decode(compact)


def test_missing_field_and_integrity_requirements_still_apply():
    _, compact = shared_response()
    del compact["registros"][0]["decisao"]
    with pytest.raises(v.StructureValidationError):
        v._validate_block(decode(compact), [1], {1}, {1: "Evento A1\nEvento B1\n"})


def test_complete_analysis_persists_full_cards_and_reuses_checkpoint(monkeypatch):
    original, compact = shared_response()
    monkeypatch.setattr(v, "_request", lambda *_: copy.deepcopy(compact))
    found, _ = analyze(source())
    assert found == original["registros"]
    with checkpoint(source()) as saved:
        state = saved.load()
        assert not state["pending"]
        assert "$campo" not in json.dumps(state)
        assert "campos_compartilhados" not in json.dumps(state)
    monkeypatch.setattr(v, "_request", lambda *_: pytest.fail("Checkpoint concluído não chama IA."))
    assert analyze(source())[0] == found


def test_rejected_dictionary_cannot_rebind_reference_in_correction(monkeypatch):
    calls = []

    def request(messages, *_):
        data = json.loads(messages[-1]["content"])
        calls.append(data)
        original, compact = shared_response()
        if len(calls) == 1:
            compact["registros"][0]["ato"] = {wire.FIELD_REF: "C404"}
            return compact
        assert data["diagnostico_validacao"]["motivo"] == "referencia_campo_invalida"
        previous = data["resposta_anterior"]["registros"][0]["ato"]
        assert previous["referencia_campo_rejeitada"]["id"] == "C404"
        return compact

    monkeypatch.setattr(v, "_request", request)
    assert analyze(source())[0] == shared_response()[0]["registros"]
    assert len(calls) == 2


def test_previous_response_keeps_resolved_values_and_no_cross_call_dictionary():
    original, compact = shared_response()
    assert wire.rejected_view(compact, {}) == original
    other = copy.deepcopy(compact)
    del other["campos_compartilhados"]
    with pytest.raises(v.StructureValidationError): decode(other)


def test_queue_checkpoint_migration_preserves_every_value():
    from tests.report_renderer.test_transport import test_recovery_checkpoint_migration_preserves_every_complete_and_pending_value
    test_recovery_checkpoint_migration_preserves_every_complete_and_pending_value(12)


def test_shared_drafts_are_revised_with_ids_and_evidence_preserved(monkeypatch):
    original, compact = shared_response()
    calls = []

    def request(messages, *_):
        calls.append(json.loads(messages[-1]["content"]))
        result = copy.deepcopy(compact)
        if len(calls) == 1:
            result["paginas"][0]["estado"] = "pendente"
            for row in result["registros"]:
                row["conferencia_integridade"] = {"estado": "pendente", "pendencias": ["Conferir inversamente."]}
        else:
            assert calls[-1]["continuidade"]["ids_para_revisar"] == [r["id"] for r in original["registros"]]
        return result

    monkeypatch.setattr(v, "_request", request)
    assert analyze(source())[0] == original["registros"]
    assert len(calls) == 2
    with checkpoint(source()) as saved:
        state = saved.load()
        assert len(state["completed"][0]["review_history"]) == 2


def test_api_generates_pdf_and_zip_with_integral_fields(monkeypatch):
    import base64
    import hashlib
    import io
    import zipfile
    from fastapi.testclient import TestClient
    from infra.report_renderer.app import app

    original, compact = shared_response()
    monkeypatch.setenv("INTERNAL_API_TOKEN", "token-ficticio")
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-ficticia")
    monkeypatch.setattr(v, "_request", lambda *_: copy.deepcopy(compact))
    text = source()
    result = TestClient(app).post('/v1/analyze-anvisa-v8', headers={"X-Internal-Token": "token-ficticio"}, json={
        "markdown": text, "page_count": 1, "markdown_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "source_filename": "sintetico.pdf"})
    assert result.status_code == 200, result.text
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(result.json()["bundle_base64"]))) as archive:
        assert archive.testzip() is None
        found = [json.loads(line) for line in archive.read("dados_anvisa_v8.jsonl").splitlines()]
        assert found == original["registros"]
        assert archive.read("relatorio_anvisa_v8.pdf").startswith(b"%PDF")
