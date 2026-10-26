from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from typing import Any


PAGE_RE = re.compile(r"^##\s+Página\s+(\d+)\s*$", re.IGNORECASE | re.MULTILINE)
PROCESS_ID_RE = re.compile(r"\b(?:\d{5}\.\d{3,6}|\d{11})/\d{4}(?:-\d{2})?\b")
REGULATORY_TERMS = {
    "deferido": re.compile(r"\b(?<!in)deferid[oa]s?\b", re.IGNORECASE),
    "indeferido": re.compile(r"\bindeferid[oa]s?\b", re.IGNORECASE),
    "cancelado": re.compile(r"\bcancelad[oa]s?\b", re.IGNORECASE),
    "aprovado": re.compile(r"\baprovad[oa]s?\b", re.IGNORECASE),
    "registrado": re.compile(r"\bregistrad[oa]s?\b", re.IGNORECASE),
    "suspenso": re.compile(r"\bsuspens[oa]s?\b", re.IGNORECASE),
    "revogado": re.compile(r"\brevogad[oa]s?\b", re.IGNORECASE),
    "exigência": re.compile(r"\bexig[eê]ncias?\b", re.IGNORECASE),
    "prazo": re.compile(r"\bprazos?\b", re.IGNORECASE),
    "publicado": re.compile(r"\bpublicad[oa]s?\b", re.IGNORECASE),
    "retificado": re.compile(r"\bretificad[oa]s?\b", re.IGNORECASE),
    "arquivado": re.compile(r"\barquivad[oa]s?\b", re.IGNORECASE),
    "interditado": re.compile(r"\binterditad[oa]s?\b", re.IGNORECASE),
}


def _pages(markdown: str) -> list[tuple[int, str]]:
    matches = list(PAGE_RE.finditer(markdown))
    if not matches:
        raise ValueError("Markdown sem marcadores de página")
    numbers = [int(match.group(1)) for match in matches]
    if numbers != list(range(1, len(numbers) + 1)):
        raise ValueError("Marcadores de página ausentes, duplicados ou fora de ordem")
    pages = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        pages.append((numbers[index], markdown[match.end():end]))
    return pages


def _excerpt(text: str, start: int, end: int, radius: int = 180) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    return " ".join(text[left:right].split())


def build_deterministic_context(markdown: str) -> dict[str, Any]:
    """Localiza menções literais sem inferir o status ou o sentido do ato."""
    source = str(markdown or "")
    pages = _pages(source)
    anchors: list[dict[str, Any]] = []
    occurrences_by_identifier: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for page_number, page_text in pages:
        matches: list[tuple[int, int, str, str]] = []
        for identifier_match in PROCESS_ID_RE.finditer(page_text):
            identifier = identifier_match.group(0)
            excerpt = _excerpt(page_text, identifier_match.start(), identifier_match.end())
            occurrence = {"page": page_number, "evidence": excerpt}
            occurrences_by_identifier[identifier].append(occurrence)
            matches.append((identifier_match.start(), identifier_match.end(), "identificador_processo", identifier))
        for term, pattern in REGULATORY_TERMS.items():
            for term_match in pattern.finditer(page_text):
                matches.append((term_match.start(), term_match.end(), "termo_literal", term_match.group(0)))

        for start, end, kind, literal in sorted(matches, key=lambda item: (item[0], item[1], item[2])):
            anchors.append({
                "page": page_number,
                "kind": kind,
                "term": literal,
                "category": "identificador de processo" if kind == "identificador_processo" else "menção regulatória literal",
                "evidence": _excerpt(page_text, start, end),
            })

    linked = []
    for identifier, occurrences in sorted(occurrences_by_identifier.items()):
        unique_occurrences = list({(item["page"], item["evidence"]): item for item in occurrences}.values())
        page_numbers = sorted({item["page"] for item in unique_occurrences})
        if len(page_numbers) > 1:
            linked.append({
                "identifier": identifier,
                "pages": page_numbers,
                "occurrences": sorted(unique_occurrences, key=lambda item: (item["page"], item["evidence"])),
            })

    return {
        "source_markdown_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "page_count": len(pages),
        "pages_processed": [page for page, _ in pages],
        "anchor_count": len(anchors),
        "anchors": anchors,
        "cross_page_links": linked,
    }
