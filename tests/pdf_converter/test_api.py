from fastapi.testclient import TestClient

from infra.pdf_converter.app import app

from .test_converter import make_pdf


client = TestClient(app)


def test_health_endpoint_reports_service_ready() -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "pdf-converter"}


def test_convert_endpoint_returns_markdown_and_metadata() -> None:
    response = client.post(
        "/v1/convert",
        files={"file": ("referencia.pdf", make_pdf("Conteúdo regulatório"), "application/pdf")},
        data={"source_document_id": "drive-123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "converted"
    assert body["metadata"]["source_filename"] == "referencia.pdf"
    assert body["metadata"]["source_document_id"] == "drive-123"
    assert "## Página 1" in body["markdown"]


def test_convert_endpoint_returns_structured_error_for_invalid_pdf() -> None:
    response = client.post(
        "/v1/convert",
        files={"file": ("corrompido.pdf", b"not a PDF", "application/pdf")},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_PDF"
