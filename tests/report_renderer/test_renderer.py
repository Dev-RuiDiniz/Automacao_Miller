from io import BytesIO

from fastapi.testclient import TestClient
from pypdf import PdfReader

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
