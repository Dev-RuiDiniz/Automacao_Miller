from io import BytesIO

from pypdf import PdfReader
from fastapi.testclient import TestClient

from infra.report_renderer.app import app


client = TestClient(app)


def sample_payload() -> dict:
    return {
        "metadata": {
            "source_filename": "referencia.pdf",
            "source_sha256": "abc123",
            "page_count": 2,
            "converter_version": "0.3.0",
        },
        "analysis": {
            "documento": {
                "nome": "referencia.pdf",
                "status_processamento": "concluido",
                "paginas_analisadas": [1, 2],
            },
            "medicamentos_deferidos": [
                {"empresa": "Empresa A", "produto": "Produto A", "paginas_origem": [1]}
            ],
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
        },
    }


def test_render_endpoint_returns_readable_pdf_with_required_sections() -> None:
    response = client.post("/v1/render", json=sample_payload())

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

    reader = PdfReader(BytesIO(response.content))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    assert len(reader.pages) >= 1
    assert "Medicamentos deferidos" in text
    assert "Suplementos indeferidos" in text
    assert "Produto A" in text
    assert "referencia.pdf" in text


def test_render_endpoint_rejects_missing_analysis() -> None:
    response = client.post("/v1/render", json={"metadata": {}})

    assert response.status_code == 422
