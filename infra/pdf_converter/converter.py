from __future__ import annotations

import hashlib
import io
import re
from pathlib import PurePath
from typing import Any

import pdfplumber
from pypdf import PdfReader

CONVERTER_VERSION = "0.3.0"
STRUCTURED_TABLE_HINTS = (
    "NOME DA EMPRESA",
    "NOME DO MEDICAMENTO",
    "NOME DO PRODUTO",
    "RELATÓRIO DE CONFERÊNCIA",
    "ENSAIOS CLÍNICOS",
    "NOME DO ESTUDO",
)


class ConversionError(Exception):
    """Erro técnico explícito durante a conversão de PDF para Markdown."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def _safe_filename(filename: str) -> str:
    name = PurePath(filename or "document.pdf").name.strip()
    return name or "document.pdf"


def _clean_text(value: Any) -> str:
    text = str(value or "").replace("\x00", "")
    return re.sub(r"[ \t]+\n", "\n", text).strip()


def _markdown_table(table: list[list[Any]]) -> str:
    rows = [[_clean_text(cell).replace("|", "\\|").replace("\n", "<br>") for cell in row] for row in table]
    rows = [row for row in rows if any(row)]
    if not rows:
        return ""

    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]
    header = rows[0]
    separator = ["---"] * width
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(separator) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows[1:])
    return "\n".join(lines)


def _looks_like_tabular_text(text: str) -> bool:
    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) < 3:
        return False
    spaced_lines = sum(bool(re.search(r"\S[ \t]{2,}\S", line)) for line in lines)
    return spaced_lines >= 3 and spaced_lines >= len(lines) // 8


def _should_extract_structured_tables(text: str) -> bool:
    normalized = text.upper()
    return any(hint in normalized for hint in STRUCTURED_TABLE_HINTS)


def _page_markdown(
    page_number: int,
    extracted_text: str | None,
    pdfplumber_page: Any,
    warnings: list[str],
) -> tuple[str, bool]:
    text = _clean_text(extracted_text or "")

    blocks = [f"## Página {page_number}"]
    if text:
        if _looks_like_tabular_text(text):
            blocks.extend(["### Conteúdo tabular preservado", f"```text\n{text}\n```"])
            warnings.append(
                f"Página {page_number}: possível tabela preservada em bloco de texto; "
                "a geometria original não foi reconstruída."
            )
        else:
            blocks.append(text)

        if _should_extract_structured_tables(text):
            try:
                tables = pdfplumber_page.extract_tables() or []
            except Exception as exc:  # pragma: no cover - depends on PDF layout
                warnings.append(
                    f"Página {page_number}: falha de detecção de tabelas: {type(exc).__name__}"
                )
                tables = []
            for table_index, table in enumerate(tables, start=1):
                rendered = _markdown_table(table)
                if rendered:
                    blocks.extend([f"### Tabela estruturada {table_index}", rendered])
                    warnings.append(
                        f"Página {page_number}: tabela {table_index} convertida por detecção automática."
                    )

    if not text:
        warnings.append(f"Página {page_number}: nenhum texto ou tabela extraível.")
        blocks.append("_Nenhum conteúdo textual extraível nesta página._")

    return "\n\n".join(blocks), bool(text)


def convert_pdf_bytes(
    pdf_bytes: bytes,
    source_filename: str,
    source_document_id: str | None = None,
) -> dict[str, Any]:
    """Converte um PDF textual em Markdown com marcadores de página e evidência."""

    if not pdf_bytes:
        raise ConversionError("INVALID_PDF", "O arquivo PDF está vazio.")

    source_sha256 = hashlib.sha256(pdf_bytes).hexdigest()
    warnings: list[str] = []

    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            page_blocks: list[str] = []
            extractable_pages = 0
            page_count = len(pdf.pages)
            if len(reader.pages) != page_count:
                raise ConversionError("INVALID_PDF", "A contagem de páginas diverge entre os leitores PDF.")
            for page_number, pdfplumber_page in enumerate(pdf.pages, start=1):
                try:
                    extracted_text = reader.pages[page_number - 1].extract_text()
                except Exception as exc:  # pragma: no cover - malformed page internals
                    warnings.append(
                        f"Página {page_number}: falha de extração textual: {type(exc).__name__}"
                    )
                    extracted_text = ""
                block, has_content = _page_markdown(
                    page_number,
                    extracted_text,
                    pdfplumber_page,
                    warnings,
                )
                page_blocks.append(block)
                extractable_pages += int(has_content)
    except Exception as exc:
        raise ConversionError("INVALID_PDF", "Não foi possível abrir ou ler o PDF.") from exc

    if page_count == 0 or extractable_pages == 0:
        raise ConversionError("NO_TEXT_LAYER", "O PDF não possui conteúdo textual ou tabelas extraíveis.")

    filename = _safe_filename(source_filename)
    metadata = {
        "source_filename": filename,
        "source_sha256": source_sha256,
        "page_count": page_count,
        "converter_version": CONVERTER_VERSION,
    }
    if source_document_id:
        metadata["source_document_id"] = source_document_id

    front_matter = [
        "---",
        f"converter_version: {CONVERTER_VERSION}",
        f"source_filename: {filename}",
        f"source_sha256: {source_sha256}",
        f"page_count: {page_count}",
    ]
    if source_document_id:
        front_matter.append(f"source_document_id: {source_document_id}")
    front_matter.extend(["---", "# Documento convertido para Markdown"])

    return {
        "status": "converted",
        "markdown": "\n\n".join(["\n".join(front_matter), *page_blocks]),
        "metadata": metadata,
        "warnings": warnings,
    }
