from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from typing import Any


PAGE_RE = re.compile(r"^##\s+Página\s+(\d+)\s*$", re.IGNORECASE | re.MULTILINE)
PROCESS_ID_RE = re.compile(r"\b(?:\d{5}\.\d{3,6}|\d{11})/\d{4}(?:-\d{2})?\b")
MONTHS = (
    "janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|"
    "setembro|outubro|novembro|dezembro"
)
DATE_RE = re.compile(
    rf"\b(?:\d{{1,2}}\s+de\s+(?:{MONTHS})\s+de\s+\d{{4}}|"
    r"\d{1,2}[/.\-]\d{1,2}[/.\-]\d{4})\b",
    re.IGNORECASE,
)
DURATION_RE = re.compile(
    r"\b\d{1,4}\s*(?:dias?(?:\s+úteis?)?|semanas?|meses?|anos?|horas?|minutos?)\b",
    re.IGNORECASE,
)
DURATION_RANGE_RE = re.compile(
    r"\b(\d{1,4})\s+para\s+(\d{1,4})\s*(dias?(?:\s+úteis?)?|semanas?|meses?|anos?|horas?|minutos?)\b",
    re.IGNORECASE,
)
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


def _exact_line(text: str, start: int, end: int) -> str:
    """Retorna a linha original que contém a ocorrência, sem reescrever o texto."""
    left = text.rfind("\n", 0, start) + 1
    right = text.find("\n", end)
    if right < 0:
        right = len(text)
    return text[left:right].strip()


def build_deterministic_context(markdown: str) -> dict[str, Any]:
    """Localiza menções literais sem inferir o status ou o sentido do ato."""
    source = str(markdown or "")
    pages = _pages(source)
    anchors: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    occurrences_by_identifier: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for page_number, page_text in pages:
        matches: list[tuple[int, int, str, str]] = []
        for identifier_match in PROCESS_ID_RE.finditer(page_text):
            identifier = identifier_match.group(0)
            excerpt = _excerpt(page_text, identifier_match.start(), identifier_match.end())
            occurrence = {"page": page_number, "evidence": excerpt}
            occurrences_by_identifier[identifier].append(occurrence)
            matches.append((identifier_match.start(), identifier_match.end(), "identificador_processo", identifier))
            observations.append({
                "page": page_number,
                "category": "identificador_processo",
                "value": identifier,
                "evidence": _exact_line(page_text, identifier_match.start(), identifier_match.end()),
                "rule_id": "process-id-v1",
            })
        for term, pattern in REGULATORY_TERMS.items():
            for term_match in pattern.finditer(page_text):
                matches.append((term_match.start(), term_match.end(), "termo_literal", term_match.group(0)))
                observations.append({
                    "page": page_number,
                    "category": "termo_regulatorio_literal",
                    "value": term_match.group(0),
                    "evidence": _exact_line(page_text, term_match.start(), term_match.end()),
                    "rule_id": "regulatory-term-v1",
                })
        for value_match in DATE_RE.finditer(page_text):
            observations.append({
                "page": page_number,
                "category": "data_literal",
                "value": value_match.group(0),
                "evidence": _exact_line(page_text, value_match.start(), value_match.end()),
                "rule_id": "date-v1",
            })

        duration_mentions: list[tuple[str, int, int]] = []
        range_spans: list[tuple[int, int]] = []
        for range_match in DURATION_RANGE_RE.finditer(page_text):
            unit = range_match.group(3)
            start, end = range_match.span(1)
            duration_mentions.append((range_match.group(1), start, end))
            start, end = range_match.span(2)
            duration_mentions.append((f"{range_match.group(2)} {unit}", start, end))
            range_spans.append(range_match.span())
        for duration_match in DURATION_RE.finditer(page_text):
            if any(start <= duration_match.start() and duration_match.end() <= end for start, end in range_spans):
                continue
            duration_mentions.append((duration_match.group(0), duration_match.start(), duration_match.end()))
        for value, start, end in duration_mentions:
            observations.append({
                "page": page_number,
                "category": "duracao_literal",
                "value": value,
                "evidence": _exact_line(page_text, start, end),
                "rule_id": "duration-v1",
            })

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
        "rule_set_version": "regulatory-rules-v1",
        "page_count": len(pages),
        "pages_processed": [page for page, _ in pages],
        "anchor_count": len(anchors),
        "anchors": anchors,
        "observation_count": len(observations),
        "observations": observations,
        "cross_page_links": linked,
    }
