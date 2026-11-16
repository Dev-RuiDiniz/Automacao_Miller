import copy
import hashlib
import io
import json
import zipfile
import base64

import pytest
from fastapi.testclient import TestClient

from infra.report_renderer import anvisa_v8
from infra.report_renderer.app import app


def block(destination="excluido", justification=None):
    record = {"id": "ANV8-P1-TESTE", "categoria": "outros", "destino": destination,
              "paginas_origem": [1], "evidencias": [{"pagina": 1, "trecho_literal": "ABC\nDEF"}],
              **({"justificativa": "Fora do recorte sintético."} if justification is None else justification)}
    if destination in {"incluido", "pendente"}:
        record.update({key: {"estado": "nao_aplicavel", "valor": None, "evidencias": []} for key in anvisa_v8.FIELDS})
        record.update({key: [] for key in anvisa_v8.ARRAYS})
        record.update(campos_adicionais={}, conferencia_integridade={"estado": "revisada", "pendencias": []})
    return {"paginas": [{"pagina": 1, "estado": "analisada", "observacao": "Revisão sintética."}],
            "registros": [record], "reconciliacao_anexos": [
                {"estado_revisao": "revisada", "unidades_fonte": [{"ids_eventos": [record["id"]]}]}]}


def validate(result):
    return anvisa_v8._validate_block(result, [1], {1}, {1: "ABC\nDEF"})


@pytest.mark.parametrize("destination", ["excluido", "representacao_duplicada"])
@pytest.mark.parametrize("justification", [
    {"justificativa": "Justificativa compacta."},
    {"justificativa_destino": "Justificativa anterior."},
    {"justificativa": "Versão A.", "justificativa_destino": "Versão B preservada."},
])
def test_compact_formats_preserve_original_keys_and_values(destination, justification):
    result = block(destination, justification)
    before = copy.deepcopy(result)
    _, records, _, checked = validate(result)
    assert checked == 1 and records == before["registros"]
    assert result == before


@pytest.mark.parametrize("destination", ["incluido", "pendente"])
def test_full_records_still_require_canonical_justification(destination):
    with pytest.raises(anvisa_v8.StructureValidationError) as failure:
        validate(block(destination))
    assert failure.value.diagnostic["campo"] == "/registros/0/justificativa_destino"


@pytest.mark.parametrize("justification,field", [
    ({}, "justificativa"),
    ({"justificativa": " "}, "justificativa"),
    ({"justificativa": None}, "justificativa"),
    ({"justificativa_destino": []}, "justificativa_destino"),
    ({"justificativa": "Válida.", "justificativa_destino": {}}, "justificativa_destino"),
])
def test_compact_records_do_not_accept_missing_or_invalid_justifications(justification, field):
    with pytest.raises(anvisa_v8.StructureValidationError) as failure:
        validate(block(justification=justification))
    assert failure.value.diagnostic["campo"] == "/registros/0/" + field
    assert failure.value.diagnostic["registro_id"] == "ANV8-P1-TESTE"


@pytest.mark.parametrize("field,value,reason", [
    ("id", "ID PRIVADO INVÁLIDO", "id_formato_invalido"),
    ("id", "ANV8-P2-TESTE", "pagina_id_fora_alvo"),
    ("paginas_origem", [], "paginas_origem_invalidas"),
    ("paginas_origem", ["1"], "pagina_origem_nao_enviada"),
    ("paginas_origem", [True], "pagina_origem_nao_enviada"),
    ("paginas_origem", [1, 1], "pagina_origem_duplicada"),
    ("destino", {}, "destino_invalido"),
    ("categoria", "", "categoria_invalida"),
])
def test_record_structure_identifies_rejected_field_without_exposing_value(field, value, reason):
    result = block()
    result["registros"][0][field] = value
    with pytest.raises(anvisa_v8.StructureValidationError) as failure:
        validate(result)
    diagnostic = failure.value.diagnostic
    assert diagnostic["campo"] == "/registros/0/" + field
    assert diagnostic["motivo"] == reason and diagnostic["valor_recebido"] == value
    assert diagnostic["esperado"]
    assert "ID PRIVADO" not in str(failure.value)


@pytest.mark.parametrize("field,value", [
    ("ato", {}), ("entidades", {}), ("campos_adicionais", []),
    ("conferencia_integridade", {"estado": "pendente"}),
])
def test_full_record_requirements_are_not_relaxed(field, value):
    result = block("incluido", {"justificativa_destino": "Caso sintético."})
    result["registros"][0][field] = value
    with pytest.raises(anvisa_v8.StructureValidationError) as failure:
        validate(result)
    assert failure.value.diagnostic["campo"] == "/registros/0/" + field


def test_compact_record_still_rejects_nonliteral_quote():
    result = block()
    result["registros"][0]["evidencias"][0]["trecho_literal"] = "ABC DEF"
    with pytest.raises(anvisa_v8.EvidenceValidationError):
        validate(result)


def test_coverage_inventory_and_duplicate_ids_still_block_invalid_result():
    result = block()
    result["paginas"] = []
    with pytest.raises(anvisa_v8.StructureValidationError) as failure:
        validate(result)
    assert failure.value.diagnostic["campo"] == "/paginas"
    result = block()
    result["reconciliacao_anexos"][0]["unidades_fonte"][0]["ids_eventos"] = []
    with pytest.raises(anvisa_v8.StructureValidationError) as failure:
        validate(result)
    assert failure.value.diagnostic["motivo"] == "ids_inventario_divergentes"
    result = block()
    result["registros"].append(copy.deepcopy(result["registros"][0]))
    with pytest.raises(anvisa_v8.StructureValidationError) as failure:
        validate(result)
    assert failure.value.diagnostic["campo"] == "/registros/1/id"


@pytest.mark.parametrize("corrected", [True, False])
def test_structural_retry_targets_missing_field_and_preserves_compact_output(monkeypatch, diagnostics_root, corrected):
    monkeypatch.setenv("INTERNAL_API_TOKEN", "token-ficticio")
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-ficticia")
    calls = []

    def request(messages, key, timeout):
        data = json.loads(messages[-1]["content"])
        calls.append(data)
        if len(calls) == 2:
            diagnostic = data["diagnostico_validacao"]
            assert diagnostic["campo"] == "/registros/0/justificativa"
            assert diagnostic["motivo"] == "justificativa_ausente"
            assert diagnostic["valor_recebido"] is None and "compacto" in diagnostic["esperado"]
            assert data["resposta_anterior"] == block(justification={})
            assert anvisa_v8.CORRECTION_INSTRUCTIONS in [m["content"] for m in messages]
        assert "protocolo-privado" not in json.dumps(messages)
        return block() if len(calls) == 2 and corrected else block(justification={})

    monkeypatch.setattr(anvisa_v8, "_request", request)
    source = "## Página 1\nABC\nDEF"
    response = TestClient(app).post("/v1/analyze-anvisa-v8", headers={"X-Internal-Token": "token-ficticio"}, json={
        "markdown": source, "page_count": 1, "markdown_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "source_filename": "sintetico.pdf", "diagnostic_context": {
            "submission_id": "protocolo-privado", "attempt_number": 1, "execution_id": "teste"}})
    assert len(calls) == 2
    assert response.status_code == (200 if corrected else 422), response.text
    files = list(diagnostics_root.rglob("ANV8D-*.json"))
    assert len(files) == (1 if corrected else 2)
    assert all(json.loads(p.read_text())["falha"]["campo"] == "/registros/0/justificativa" for p in files)
    if corrected:
        with zipfile.ZipFile(io.BytesIO(base64.b64decode(response.json()["bundle_base64"]))) as archive:
            assert json.loads(archive.read("dados_anvisa_v8.jsonl")) == block()["registros"][0]
    else:
        assert "justificativa_ausente" in response.json()["detail"] and "ANV8D-" in response.json()["detail"]
