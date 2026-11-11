import base64
import hashlib
import json
import zipfile
from io import BytesIO

from fastapi.testclient import TestClient
from pypdf import PdfReader
from reportlab.pdfgen.canvas import Canvas

from infra.pdf_converter.converter import convert_pdf_bytes
from infra.report_renderer import anvisa_v8
from infra.report_renderer.app import app


client = TestClient(app)


def sample_payload() -> dict:
    return {
        "metadata": {
            "source_filename": "referencia.pdf",
            "source_sha256": "abc123",
            "page_count": 2,
            "converter_version": "0.3.0",
            "analysis_scope": {"type": "full_document", "pages": [1, 2]},
        },
        "analysis": {
            "documento": {
                "nome": "referencia.pdf",
                "status_processamento": "concluido",
                "paginas_analisadas": [1, 2],
            },
            "medicamentos_deferidos": [{"empresa": "Empresa A", "produto": "Produto A", "paginas_origem": [1]}],
            "medicamentos_indeferidos": [],
            "suplementos_deferidos": [],
            "suplementos_indeferidos": [],
            "estudos_clinicos_deferidos": [],
            "estudos_clinicos_indeferidos": [],
            "outros_atos": [],
            "exigencias": [],
            "pendencias": [],
            "categorias_nao_localizadas": ["suplementos_indeferidos"],
            "evidencias_insuficientes": [],
            "contradicoes": [],
            "avisos": [],
            "controle_confianca": {"status": "aceitavel", "motivos": []},
            "revisao_humana": {"necessaria": False, "motivos": []},
            "parecer_tecnico": {
                "escopo": "Regulatory act in the reference document",
                "conclusao_preliminar": "The document indicates approval of the product.",
                "classificacao_geral": "conforme_indicado",
                "nivel_risco": "baixo",
                "base_ids": ["F1", "AT1"],
                "fundamentos": [{
                    "id": "F1",
                    "fato_documentado": "The product appears as approved.",
                    "interpretacao_tecnica": "The document supports operational follow-up.",
                    "paginas_origem": [1],
                    "evidencia": "Product A approved",
                }],
                "apontamentos_tecnicos": [{
                    "id": "AT1",
                    "classificacao": "conformidade",
                    "titulo": "Favorable status located",
                    "constatacao": "The approved status was located on the cited page.",
                    "impacto": "It may support portfolio follow-up.",
                    "prioridade": "informativa",
                    "acao_recomendada": "Check the act in the original PDF.",
                    "paginas_origem": [1],
                    "evidencia": "Product A approved",
                }],
                "recomendacoes": [{
                    "id": "R1",
                    "acao": "Check the finding in the original document.",
                    "justificativa": "The analysis is documentary support.",
                    "prioridade": "baixa",
                    "base_ids": ["F1", "AT1"],
                }],
                "limites": ["The conclusion does not replace specialist review."],
            },
        },
    }


def pdf_text(content: bytes) -> str:
    return "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(content)).pages)


def test_anvisa_v8_converts_uses_terra_and_packages_linked_pdf(monkeypatch, tmp_path) -> None:
    synthetic = BytesIO()
    document = Canvas(synthetic)
    for page in range(1, 9):
        lines = {1: ["RESOLUCAO SINTETICA 101", "Art. 1. Aprovar a peticao."],
                 6: ["Produto Sintetico ABC", "Peticao 1111111/26-1", "Peticao 2222222/26-2",
                     "Processo da matriz 25351.000001/2026-00"]}.get(page, [f"Texto de teste da pagina {page}"])
        for i, line in enumerate(lines):
            document.drawString(60, 760 - i * 20, line)
        document.showPage()
    document.save()
    converted = convert_pdf_bytes(synthetic.getvalue(), "sigiloso-teste.pdf", "protocolo-nao-enviado")
    source = converted["markdown"]

    def field(text, page=6):
        return {"estado": "confirmado", "valor": text, "evidencias": [{"pagina": page, "trecho_literal": text}]}

    rid = "ANV8-P6-SINTETICO"
    record = {
        "id": rid, "categoria": "medicamentos", "destino": "incluido", "justificativa_destino": "Caso artificial.",
        "paginas_origem": [1, 6], "ato": field("RESOLUCAO SINTETICA 101", 1),
        "dispositivo": field("Art. 1. Aprovar a peticao.", 1), "decisao": field("Art. 1. Aprovar a peticao.", 1),
        "objeto": field("Produto Sintetico ABC"), "composicao": {"estado": "nao_aplicavel", "valor": None, "evidencias": []},
        "entidades": [], "processos": [], "apresentacoes": [], "ressalvas": [], "relacoes": [],
        "peticoes": [{"assunto": field(f"Peticao {number}"), "expedientes": [field(number)]}
                     for number in ("1111111/26-1", "2222222/26-2")],
        "campos_adicionais": {"peticao_matriz": {"processo": field("25351.000001/2026-00")}},
        "conferencia_integridade": {"estado": "revisada", "pendencias": []},
    }
    calls = []

    class MockOpenRouter:
        def open(self, request, timeout):
            assert request.full_url == "https://openrouter.ai/api/v1/chat/completions"
            assert request.get_header("Authorization") == "Bearer chave-ficticia"
            body = json.loads(request.data)
            assert body["model"] == "openai/gpt-6.1-terra"
            assert hashlib.sha256(body["messages"][0]["content"].encode()).hexdigest() == anvisa_v8.PROMPT_HASH
            assert "protocolo-nao-enviado" not in request.data.decode()
            assert "sigiloso-teste.pdf" not in request.data.decode()
            assert "chave-ficticia" not in request.data.decode()
            data = json.loads(body["messages"][-1]["content"])
            targets = data["paginas_alvo"]
            calls.append(targets)
            if targets == list(range(1, 6)):
                return BytesIO(b'{"choices":[{"finish_reason":"length","message":{"content":"{}"}}]}')
            if targets[0] == 6 and "RESOLUCAO SINTETICA 101" not in data["markdown_documental"]:
                result = {"contexto_necessario": [1]}
            else:
                result = {"paginas": [{"pagina": n, "estado": "analisada", "observacao": "Revisão sintética."} for n in targets],
                          "registros": [record] if targets[0] == 6 else [], "reconciliacao_anexos": []}
                if targets[0] == 6:
                    result["reconciliacao_anexos"] = [{"estado_revisao": "revisada", "unidades_fonte": [{"ids_eventos": [rid]}]}]
                    if "ajuste_tecnico" not in data:
                        result["registros"] = [dict(record, ato=field("Citação inexistente", 1))]
            return BytesIO(json.dumps({"model": anvisa_v8.MODEL,
                "choices": [{"finish_reason": "stop", "message": {"content": json.dumps(result)}}]}).encode())

    monkeypatch.setenv("INTERNAL_API_TOKEN", "token-interno-ficticio")
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-ficticia")
    monkeypatch.setattr(anvisa_v8, "build_opener", lambda handler: MockOpenRouter())
    response = client.post("/v1/analyze-anvisa-v8", headers={"X-Internal-Token": "token-interno-ficticio"}, json={
        "markdown": source, "page_count": 8, "markdown_sha256": converted["metadata"]["markdown_sha256"],
        "source_filename": "sigiloso-teste.pdf", "warnings": [],
    })
    assert response.status_code == 200, response.text
    assert calls == [list(range(1, 6)), [1, 2], [3, 4, 5], [6, 7, 8], [6, 7, 8], [6, 7, 8]]
    payload = response.json()
    assert payload["prompt_version"] == "V8-autossuficiente"
    assert payload["report_context"]["pdf"]["entradas_indice"] == 2
    pdf = base64.b64decode(payload["report_pdf_base64"])
    text = pdf_text(pdf)
    assert text.index("Índice de assuntos") < text.index("Resumo executivo") < text.index("Ficha " + rid)
    assert "25351.000001/2026-00" in text
    assert "Art. 1. Aprovar a peticao." in text
    assert "1111111/26-1" in text and "2222222/26-2" in text
    with zipfile.ZipFile(BytesIO(base64.b64decode(payload["bundle_base64"]))) as bundle:
        assert bundle.testzip() is None and len(bundle.namelist()) == 4
        assert bundle.read("relatorio_anvisa_v8.pdf") == pdf
        assert json.loads(bundle.read("dados_anvisa_v8.jsonl")) == record
        coverage = json.loads(bundle.read("cobertura_anvisa_v8.json"))
        assert [row["pagina"] for row in coverage["paginas"]] == list(range(1, 9))
        assert coverage["artefatos_finais_pdf_jsonl"]["relatorio_anvisa_v8.pdf"]["sha256"] == hashlib.sha256(pdf).hexdigest()
    (tmp_path / "relatorio_anvisa_v8_sintetico.pdf").write_bytes(pdf)


def test_anvisa_v8_rejects_unauthorized_missing_key_and_wrong_source_hash(monkeypatch) -> None:
    monkeypatch.setenv("INTERNAL_API_TOKEN", "token-ficticio")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    endpoint = "/v1/analyze-anvisa-v8"
    headers = {"X-Internal-Token": "token-ficticio"}
    assert client.post(endpoint, json={}).status_code == 403
    assert client.post(endpoint, json={}, headers=headers).status_code == 503
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-ficticia")
    monkeypatch.setattr(anvisa_v8, "build_opener", lambda *_: (_ for _ in ()).throw(AssertionError("A API não deve ser chamada")))
    response = client.post(endpoint, headers=headers, json={"markdown": "## Página 1\nAto de teste",
                           "page_count": 1, "markdown_sha256": "0" * 64, "source_filename": "teste.pdf"})
    assert response.status_code == 422 and "artefato convertido" in response.json()["detail"]


def test_anvisa_v8_does_not_publish_truncated_model_output(monkeypatch) -> None:
    class MockOpenRouter:
        def open(self, request, timeout):
            return BytesIO(b'{"choices":[{"finish_reason":"length","message":{"content":"{}"}}]}')

    monkeypatch.setenv("INTERNAL_API_TOKEN", "token-ficticio")
    monkeypatch.setenv("OPENROUTER_API_KEY", "chave-ficticia")
    monkeypatch.setattr(anvisa_v8, "build_opener", lambda *_: MockOpenRouter())
    source = "## Página 1\nAto de teste"
    response = client.post("/v1/analyze-anvisa-v8", headers={"X-Internal-Token": "token-ficticio"}, json={
        "markdown": source, "page_count": 1, "markdown_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "source_filename": "teste.pdf",
    })
    assert response.status_code == 502 and "incompleta" in response.json()["detail"]
    assert "report_pdf_base64" not in response.json()


def test_render_endpoint_returns_readable_pdf_with_required_sections() -> None:
    response = client.post("/v1/render", json=sample_payload())

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    text = pdf_text(response.content)
    assert "DB TECNOLOGIA" in text
    assert "Produto A" in text
    assert "referencia.pdf" in text
    assert "Resumo executivo" in text
    assert "Parecer" in text
    assert "Recomenda" in text
    assert "p. 1" in text
    assert response.headers["x-report-version"] == "1.3.0"


def test_render_endpoint_marks_quality_alert_as_optional_confirmation() -> None:
    payload = sample_payload()
    payload["analysis"]["controle_confianca"] = {"status": "baixa_confianca", "motivos": ["evidence missing"]}
    payload["analysis"]["revisao_humana"] = {"necessaria": True, "motivos": ["evidence missing"]}

    response = client.post("/v1/render", json=payload)

    assert response.status_code == 200
    text = pdf_text(response.content)
    assert "opcional" in text.lower() or "optional" in text.lower()


def test_render_endpoint_makes_missing_source_page_explicit() -> None:
    payload = sample_payload()
    payload["analysis"]["medicamentos_deferidos"] = [{"produto": "Product without page"}]

    response = client.post("/v1/render", json=payload)

    assert response.status_code == 200
    assert "conferir" in pdf_text(response.content).lower()


def test_render_endpoint_rejects_missing_analysis() -> None:
    response = client.post("/v1/render", json={"metadata": {}})
    assert response.status_code == 422


def test_render_markdown_endpoint_returns_readable_pdf() -> None:
    response = client.post(
        "/v1/render-markdown",
        json={
            "metadata": {
                "source_filename": "dou.pdf",
                "submission_id": "sub-123",
                "source_sha256": "a" * 64,
                "page_count": 128,
            },
            "report_markdown": "# Technical report\n\n## Technical opinion\n\nThe finding was located in the document.\n\n## References\n\n- Page 71: documentary evidence.\n",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["x-report-version"] == "1.3.0"
    text = pdf_text(response.content)
    assert "Technical report" in text
    assert "Technical opinion" in text
    assert "Page 71" in text


def test_render_markdown_endpoint_keeps_bullets_readable_without_raw_tables() -> None:
    response = client.post(
        "/v1/render-markdown",
        json={
            "metadata": {
                "source_filename": "atos.pdf",
                "submission_id": "sub-listas",
                "source_sha256": "b" * 64,
                "page_count": 2,
            },
            "report_markdown": (
                "# Relatório técnico\n\n"
                "## Respostas de negócio\n\n"
                "- Pergunta: o que aconteceu?\n"
                "- Resposta: o produto foi deferido.\n"
                "- Página: 1\n"
                '- Evidência literal: "produto foi deferido"\n\n'
                "## Plano de ação\n\n"
                "- Prioridade: alta.\n"
                "- Ação: conferir o ato original.\n\n"
                "## Referências de páginas\n\n"
                "- Página: 1\n"
                '- Evidência literal: "produto foi deferido"\n'
            ),
        },
    )

    assert response.status_code == 200
    text = pdf_text(response.content)
    assert "Respostas de negócio" in text
    assert "Pergunta: o que aconteceu?" in text
    assert "Evidência literal" in text
    assert "Prioridade: alta" in text
    assert not any(line.strip().startswith("|") for line in text.splitlines())
