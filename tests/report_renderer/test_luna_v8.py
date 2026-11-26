import hashlib
import json

from fastapi.testclient import TestClient

from infra.report_renderer import anvisa_v8 as v, luna_v8 as luna
from infra.report_renderer.app import app
from tests.report_renderer.test_incremental import checkpoint, full_record, response, source


def _payload(text):
    return {
        "markdown": text, "page_count": text.count("## Página "),
        "markdown_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "source_filename": "sintetico.md",
        "diagnostic_context": {"submission_id": "protocolo-sintetico",
                               "attempt_number": 1, "execution_id": "execucao-sintetica"},
    }


def _client(monkeypatch):
    monkeypatch.setenv("ANVISA_V8_MODEL", luna.MODEL)
    monkeypatch.setenv("INTERNAL_API_TOKEN", "token-sintetico")
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-sintetica")
    return TestClient(app)


def test_luna_consolida_duas_partes_com_evidencias_de_fronteira(monkeypatch):
    text = source(8).replace("Evento A4", "Evento A4, processo 25351.004110/2026-19")
    calls = []

    def request(messages, *_):
        data = json.loads(messages[-1]["content"])
        targets = data["paginas_alvo"]
        calls.append(targets)
        start = targets[-1] if targets[0] == 1 else targets[0]
        other = 5 if start == 4 else 4
        assert f"## Página {other}" in data["markdown_documental"]
        assert any(item["pagina"] == 4 and item["alvo"] == (start == 4)
                   for item in data["indice_ocorrencias_literais"])
        record = full_record(start)
        record["paginas_origem"] = [4, 5]
        record["ressalvas"] = [{"pagina": other, "trecho_literal": f"Evento B{other}"}]
        return response(targets, [record])

    monkeypatch.setattr(luna, "_request", request)
    result = _client(monkeypatch).post("/v1/analyze-anvisa-v8", json=_payload(text),
                                      headers={"X-Internal-Token": "token-sintetico"})
    assert result.status_code == 200, result.text
    output = result.json()
    assert sorted(calls) == [[1, 2, 3, 4], [5, 6, 7, 8]]
    assert output["report_context"]["model"] == luna.MODEL
    assert output["report_context"]["pdf"]["entradas_indice"] == 2
    assert output["report_context"]["analysis_checkpoint"]["chamadas"] == 2
    assert output["report_context"]["references_confirmed"] > 0


def test_luna_rejeita_ficha_invalida_sem_terceira_chamada(monkeypatch):
    calls = []

    def request(messages, *_):
        targets = json.loads(messages[-1]["content"])["paginas_alvo"]
        calls.append(targets)
        record = full_record(targets[0])
        record.pop("justificativa_destino")
        return response(targets, [record])

    monkeypatch.setattr(luna, "_request", request)
    result = _client(monkeypatch).post("/v1/analyze-anvisa-v8", json=_payload(source(8)),
                                      headers={"X-Internal-Token": "token-sintetico"})
    assert result.status_code == 422
    assert "ANV8D-" in result.json()["detail"]
    assert len(calls) == 2


def test_luna_bloqueia_protocolo_com_checkpoint_terra(monkeypatch):
    text = source(8)
    with checkpoint(text) as saved:
        saved.save({"completed": [{"lote": n} for n in range(26)]})
    before = saved.path.read_bytes()
    monkeypatch.setattr(luna, "_request", lambda *_: (_ for _ in ()).throw(AssertionError("Luna não pode ser chamado.")))
    result = _client(monkeypatch).post("/v1/analyze-anvisa-v8", json=_payload(text),
                                      headers={"X-Internal-Token": "token-sintetico"})
    assert result.status_code == 409
    assert saved.path.read_bytes() == before


def test_esquema_luna_exige_ficha_completa_e_ids_do_inventario():
    props = luna.output_schema()["properties"]
    full = props["registros"]["items"]["anyOf"][0]
    assert len(full["required"]) == 18
    assert v.FIELDS | v.ARRAYS | {"justificativa_destino", "conferencia_integridade"} <= set(full["required"])
    unit = props["reconciliacao_anexos"]["items"]["properties"]["unidades_fonte"]["items"]
    assert unit["required"] == ["ids_eventos"]
    assert props["paginas"]["items"]["properties"]["observacao"]["maxLength"] == 96
