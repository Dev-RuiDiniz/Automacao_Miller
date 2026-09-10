from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


PAGE_RE = re.compile(r"^##\s+Página\s+(\d+)\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class PageChunk:
    page_start: int
    page_end: int
    chunk_index: int
    content: str
    content_sha256: str


def _split_pages(markdown: str) -> list[tuple[int, str]]:
    pages: list[tuple[int, list[str]]] = []
    current_page: int | None = None
    current_lines: list[str] = []
    for line in str(markdown or "").splitlines():
        match = PAGE_RE.match(line.strip())
        if match:
            if current_page is not None:
                pages.append((current_page, current_lines))
            current_page = int(match.group(1))
            current_lines = [line]
        elif current_page is not None:
            current_lines.append(line)
    if current_page is not None:
        pages.append((current_page, current_lines))
    return [(page, "\n".join(lines).strip()) for page, lines in pages if "\n".join(lines).strip()]


def _windows(text: str, size: int, overlap: int) -> list[str]:
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("chunk_size deve ser positivo e overlap menor que o tamanho")
    if len(text) <= size:
        return [text]
    result: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        result.append(text[start:end].strip())
        if end == len(text):
            break
        start = end - overlap
    return [part for part in result if part]


def split_markdown_by_page(markdown: str, chunk_size: int = 1200, chunk_overlap: int = 150) -> list[PageChunk]:
    """Divide o Markdown em chunks que nunca perdem a página de origem."""
    chunks: list[PageChunk] = []
    for page, content in _split_pages(markdown):
        for part in _windows(content, chunk_size, chunk_overlap):
            digest = hashlib.sha256(part.encode("utf-8")).hexdigest()
            chunks.append(PageChunk(page, page, len(chunks), part, digest))
    return chunks
