import hashlib
import json
import os

import pytest
from fastapi.testclient import TestClient

from infra.report_renderer import anvisa_v8, diagnostics
from infra.report_renderer.app import app


@pytest.mark.parametrize("page,quote,allowed,reason", [
    ("1", "ABC", {1}, "pagina_tipo_invalido"),
    (True, "ABC", {1}, "pagina_tipo_invalido"),
    (2, "ABC", {1}, "pagina_fora_do_registro"),
    (2, "ABC", {2}, "pagina_ausente_na_fonte"),
    (1, None, {1}, "trecho_tipo_invalido"),
    (1, "  ", {1}, "trecho_vazio"),
    (1, "ABC DEF", {1}, "trecho_nao_localizado"),
    (1, "Texto ausente", {1}, "trecho_nao_localizado"),
])
def test_evidence_identifies_reason_pointer_and_record_without_relaxing_check(page, quote, allowed, reason):
    evidence = {"campo/com~nome": [{"pagina": page, "trecho_literal": quote}]}
    with pytest.raises(anvisa_v8.EvidenceValidationError) as failure:
        anvisa_v8._evidence(evidence, {1: "ABC\nDEF"}, allowed, path="/registros/0", record_id="ANV8-P1-TESTE")
    diagnostic = failure.value.diagnostic
    assert diagnostic["motivo"] == reason
    assert diagnostic["campo"] == "/registros/0/campo~1com~0nome/0"
    assert diagnostic["registro_id"] == "ANV8-P1-TESTE"
    assert diagnostic["pagina"] == page and diagnostic["trecho_rejeitado"] == quote
    assert diagnostic["coincide_apenas_normalizando_espacos"] == (quote == "ABC DEF")
    assert "campo/com~nome" not in str(failure.value)
    if quote == "Texto ausente":
        assert quote not in str(failure.value)


def test_literal_evidence_still_requires_original_line_breaks():
    assert anvisa_v8._evidence({"pagina": 1, "trecho_literal": "ABC\nDEF"}, {1: "ABC\nDEF"}, {1}) == 1


def invalid_result():
    return anvisa_v8.ModelResult({
        "paginas": [{"pagina": 1, "estado": "analisada", "observacao": "Caso sintético."}],
        "registros": [{"id": "ANV8-P1-TESTE", "categoria": "outros", "destino": "excluido",
                       "justificativa_destino": "Documento sintético.", "paginas_origem": [1],
                       "evidencias": [{"pagina": 1, "trecho_literal": "TEXTO PRIVADO REJEITADO"}]}],
        "reconciliacao_anexos": [{"estado_revisao": "revisada", "unidades_fonte": [{"ids_eventos": ["ANV8-P1-TESTE"]}]}],
    }, "gen-sintetico")


def endpoint_setup(monkeypatch):
    monkeypatch.setenv("INTERNAL_API_TOKEN", "token-interno-ficticio")
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-protegida-ficticia")
    calls = []

    def request(messages, key, timeout):
        calls.append(messages)
        return invalid_result()

    monkeypatch.setattr(anvisa_v8, "_request", request)
    source = "## Página 1\nABC\nDEF"
    payload = {"markdown": source, "page_count": 1, "markdown_sha256": hashlib.sha256(source.encode()).hexdigest(),
               "source_filename": "sintetico.pdf", "diagnostic_context": {
                   "submission_id": "protocolo-sintetico", "attempt_number": 3, "execution_id": "execucao-sintetica"}}
    return TestClient(app), {"X-Internal-Token": "token-interno-ficticio"}, payload, calls


def test_final_failure_preserves_both_diagnostics_and_returns_safe_reference(monkeypatch, diagnostics_root):
    client, headers, payload, calls = endpoint_setup(monkeypatch)
    response = client.post("/v1/analyze-anvisa-v8", headers=headers, json=payload)
    assert response.status_code == 422 and len(calls) == 2
    files = list(diagnostics_root.rglob("ANV8D-*.json"))
    assert len(files) == 2
    saved = [json.loads(p.read_text()) for p in files]
    assert {d["apos_pedido_correcao"] for d in saved} == {False, True}
    assert {d["chamada_no_bloco"] for d in saved} == {1, 2}
    assert all(d["context"] == payload["diagnostic_context"] for d in saved)
    assert all(d["bloco"]["markdown_documental"] == payload["markdown"] for d in saved)
    assert all(d["falha"]["campo"] == "/registros/0/evidencias/0" for d in saved)
    assert all(d["generation_id"] == "gen-sintetico" for d in saved)
    assert any(d["diagnostic_id"] in response.json()["detail"] for d in saved)
    assert "TEXTO PRIVADO" not in response.text and str(diagnostics_root) not in response.text
    assert "chave-protegida-ficticia" not in "".join(p.read_text() for p in files)
    second_request = json.loads(calls[1][-1]["content"])
    assert second_request["diagnostico_validacao"]["campo"] == "/registros/0/evidencias/0"
    assert second_request["resposta_anterior"]["registros"][0]["id"] == "ANV8-P1-TESTE"
    assert "protocolo-sintetico" not in json.dumps(calls)
    assert "execucao-sintetica" not in json.dumps(calls)


def test_storage_failure_stops_before_correction_and_does_not_publish_partial_file(monkeypatch, diagnostics_root):
    client, headers, payload, calls = endpoint_setup(monkeypatch)
    fsync = os.fsync

    def fail_diagnostic(descriptor):
        if "ANV8D-" in os.readlink(f"/proc/self/fd/{descriptor}"):
            raise OSError("Falha sintética no diagnóstico.")
        return fsync(descriptor)

    monkeypatch.setattr(os, "fsync", fail_diagnostic)
    response = client.post("/v1/analyze-anvisa-v8", headers=headers, json=payload)
    assert response.status_code == 500 and "ARMAZENAMENTO" in response.json()["detail"]
    assert len(calls) == 1
    assert not list(diagnostics_root.rglob("ANV8D-*.json"))
    assert "TEXTO PRIVADO" not in response.text


def test_unavailable_private_directory_prevents_paid_request(monkeypatch, diagnostics_root):
    client, headers, payload, calls = endpoint_setup(monkeypatch)
    diagnostics_root.write_text("Arquivo em vez de diretório")
    response = client.post("/v1/analyze-anvisa-v8", headers=headers, json=payload)
    assert response.status_code == 500 and not calls


@pytest.mark.parametrize("context", [
    {"submission_id": "../outro", "attempt_number": 1, "execution_id": "teste"},
    {"submission_id": "teste", "attempt_number": True, "execution_id": "teste"},
    {"submission_id": "teste", "attempt_number": 1, "execution_id": "teste", "segredo": "não salvar"},
    {},
])
def test_invalid_internal_context_is_not_used_or_sent(monkeypatch, context):
    client, headers, payload, calls = endpoint_setup(monkeypatch)
    payload["diagnostic_context"] = context
    response = client.post("/v1/analyze-anvisa-v8", headers=headers, json=payload)
    assert response.status_code == 422 and not calls
