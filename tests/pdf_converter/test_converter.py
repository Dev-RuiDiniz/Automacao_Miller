from io import BytesIO

import pytest
from reportlab.pdfgen import canvas

from infra.pdf_converter.converter import ConversionError, convert_pdf_bytes


def make_pdf(*pages: str) -> bytes:
    stream = BytesIO()
    document = canvas.Canvas(stream)
    for page_text in pages:
        document.drawString(72, 760, page_text)
        document.showPage()
    document.save()
    return stream.getvalue()


def test_convert_pdf_emits_metadata_and_page_markers() -> None:
    source = make_pdf("Medicamento deferido", "Página complementar")

    result = convert_pdf_bytes(source, "referencia.pdf", "drive-file-123")

    assert result["status"] == "converted"
    assert result["metadata"]["source_filename"] == "referencia.pdf"
    assert result["metadata"]["source_document_id"] == "drive-file-123"
    assert result["metadata"]["page_count"] == 2
    assert result["metadata"]["source_sha256"]
    assert "## Página 1" in result["markdown"]
    assert "## Página 2" in result["markdown"]
    assert "Medicamento deferido" in result["markdown"]
    assert "Página complementar" in result["markdown"]


def test_convert_pdf_rejects_corrupted_input_as_conversion_error() -> None:
    with pytest.raises(ConversionError, match="INVALID_PDF"):
        convert_pdf_bytes(b"not a PDF", "corrompido.pdf")


def test_convert_pdf_rejects_pdf_without_extractable_text() -> None:
    source = make_pdf("", "")

    with pytest.raises(ConversionError, match="NO_TEXT_LAYER"):
        convert_pdf_bytes(source, "escaneado.pdf")


def test_convert_pdf_preserves_detectable_tabular_text_as_markdown_block() -> None:
    stream = BytesIO()
    document = canvas.Canvas(stream)
    document.drawString(72, 760, "Nome do produto     Empresa responsável")
    document.drawString(72, 740, "Produto A            Empresa A")
    document.drawString(72, 720, "Produto B            Empresa B")
    document.save()

    result = convert_pdf_bytes(stream.getvalue(), "tabela.pdf")

    assert "### Conteúdo tabular preservado" in result["markdown"]
    assert "```text" in result["markdown"]
    assert any("geometria original" in warning for warning in result["warnings"])
