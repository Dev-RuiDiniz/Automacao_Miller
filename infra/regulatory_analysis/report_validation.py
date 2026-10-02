from __future__ import annotations

import re
from typing import Any

from infra.regulatory_analysis.quality import normalize_evidence, source_pages


PAGE_BULLET_RE = re.compile(r"^\s*[-*]\s*P[aá]gina\s*:\s*(\d+)\s*$", re.IGNORECASE)
EVIDENCE_BULLET_RE = re.compile(r"^\s*[-*]\s*Evid[eê]ncia(?:\s+literal)?\s*:\s*(.*?)\s*$", re.IGNORECASE)
PAGE_MENTION_RE = re.compile(r"\b(?:p[aá]gina|p\.)\s*:?\s*(\d+)\b", re.IGNORECASE)


def _unquote(value: str) -> str:
    value = str(value or "").strip().strip("`*_ ")
    return value.strip("\"'“”‘’ ")


def _check_reference(page: int | None, evidence: str, pages: dict[int, str]) -> dict[str, Any]:
    item: dict[str, Any] = {"page": page, "evidence": evidence, "status": "pending"}
    if page is None:
        item.update(code="page_missing", reason="página não identificada")
        return item
    if page not in pages:
        item.update(code="page_not_found", reason="página não existe no Markdown original")
        return item
    normalized = normalize_evidence(evidence)
    if not normalized:
        item.update(code="evidence_missing", reason="trecho literal ausente")
        return item
    page_text = normalize_evidence(pages[page])
    if normalized in page_text:
        item.update(status="confirmed", code="confirmed", reason="página e trecho localizados no Markdown original")
        return item
    found_on_pages = [source_page for source_page, text in pages.items() if normalized in normalize_evidence(text)]
    if found_on_pages:
        item.update(code="evidence_found_on_other_page", reason="trecho localizado em outra página", found_on_pages=found_on_pages)
    else:
        item.update(code="evidence_not_found", reason="trecho não localizado no Markdown original")
    return item


def validate_report_references(
    report_markdown: str,
    source_markdown: str,
    pages_processed: list[int],
) -> dict[str, Any]:
    """Confere cobertura e referências; referências inválidas são marcadas como pendentes."""
    pages = source_pages(source_markdown)
    expected_pages = set(pages)
    processed = {page for page in pages_processed if isinstance(page, int) and not isinstance(page, bool)}
    covered = expected_pages & processed
    missing_pages = sorted(expected_pages - covered)
    unexpected_pages = sorted(processed - expected_pages)
    ratio = round(len(covered) / len(expected_pages), 4) if expected_pages else 0.0
    coverage = {
        "source_pages": len(expected_pages),
        "processed_pages": len(covered),
        "ratio": ratio,
        "complete": bool(expected_pages) and not missing_pages and not unexpected_pages,
        "missing_pages": missing_pages,
        "unexpected_pages": unexpected_pages,
    }

    lines = str(report_markdown or "").splitlines()
    sanitized = list(lines)
    consumed: set[int] = set()
    references: list[dict[str, Any]] = []

    def add_reference(page: int | None, evidence: str, line_indexes: list[int], label: str) -> None:
        reference = _check_reference(page, _unquote(evidence), pages)
        reference["location"] = label
        references.append(reference)
        if reference["status"] == "pending":
            page_label = f"página {page}" if page is not None else "página não identificada"
            sanitized[line_indexes[0]] = f"- Referência pendente (não comprovada): {page_label}."
            if len(line_indexes) > 1:
                quote = reference["evidence"] or "trecho não informado"
                reason = reference["reason"]
                sanitized[line_indexes[1]] = f"- Trecho alegado, não comprovado: “{quote}” — {reason}."

    # Tabelas de referência antigas declaram as colunas pelo cabeçalho.
    index = 0
    while index < len(lines):
        if not lines[index].strip().startswith("|"):
            index += 1
            continue
        headers = [cell.strip().casefold() for cell in lines[index].strip().strip("|").split("|")]
        page_column = next((i for i, value in enumerate(headers) if "página" in value or "pagina" in value), None)
        evidence_column = next((i for i, value in enumerate(headers) if "evidência" in value or "evidencia" in value), None)
        if page_column is None or evidence_column is None:
            index += 1
            continue
        row = index + 1
        while row < len(lines) and lines[row].strip().startswith("|"):
            cells = [cell.strip() for cell in lines[row].strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
                row += 1
                continue
            if page_column < len(cells) and evidence_column < len(cells):
                page_match = re.search(r"\d+", cells[page_column])
                page = int(page_match.group()) if page_match else None
                evidence = _unquote(cells[evidence_column])
                add_reference(page, evidence, [row], "markdown_table")
                consumed.add(row)
            row += 1
        index = row

    # Formato vigente: a página e a evidência literal ficam em duas linhas seguidas.
    index = 0
    while index < len(lines):
        if index in consumed:
            index += 1
            continue
        page_match = PAGE_BULLET_RE.match(lines[index])
        if page_match:
            page = int(page_match.group(1))
            evidence_index = index + 1
            evidence_match = EVIDENCE_BULLET_RE.match(lines[evidence_index]) if evidence_index < len(lines) else None
            if evidence_match:
                add_reference(page, evidence_match.group(1), [index, evidence_index], "markdown_bullets")
                consumed.update((index, evidence_index))
                index += 2
                continue
            references.append({"page": page, "evidence": "", "status": "pending", "code": "evidence_missing", "reason": "trecho literal não acompanha a página", "location": "markdown_bullets"})
            sanitized[index] = f"- Referência pendente (não comprovada): página {page}; trecho literal ausente."
            consumed.add(index)
        index += 1

    # Uma menção a página fora dos dois formatos acima também não pode parecer conferida.
    for index, line in enumerate(lines):
        if index in consumed:
            continue
        mention = PAGE_MENTION_RE.search(line)
        if mention:
            page = int(mention.group(1))
            references.append({"page": page, "evidence": "", "status": "pending", "code": "reference_format_unrecognized", "reason": "página citada sem evidência literal no formato verificável", "location": "markdown_text"})
            sanitized[index] = f"- Referência pendente (não comprovada): {line.strip()}"
            continue
        evidence_match = EVIDENCE_BULLET_RE.match(line)
        if evidence_match:
            evidence = _unquote(evidence_match.group(1))
            references.append({"page": None, "evidence": evidence, "status": "pending", "code": "page_missing", "reason": "evidência sem página verificável", "location": "markdown_text"})
            sanitized[index] = f"- Trecho alegado, não comprovado: “{evidence or 'trecho não informado'}” — página ausente."

    unique: dict[tuple[int | None, str], dict[str, Any]] = {}
    for reference in references:
        key = (reference.get("page"), normalize_evidence(reference.get("evidence", "")))
        previous = unique.get(key)
        if previous is None or (previous["status"] == "confirmed" and reference["status"] == "pending"):
            unique[key] = reference
    if not unique:
        unique[(None, "")] = {"page": None, "evidence": "", "status": "pending", "code": "references_missing", "reason": "o relatório não apresentou citações verificáveis", "location": "report"}

    items = list(unique.values())
    confirmed = sum(item["status"] == "confirmed" for item in items)
    pending = [item for item in items if item["status"] == "pending"]
    return {
        "validated_report_markdown": "\n".join(sanitized),
        "coverage": coverage,
        "references": {"total": len(items), "confirmed": confirmed, "pending": pending, "items": items},
        "evidence_quality": {
            "coverage_complete": coverage["complete"],
            "references_confirmed": confirmed,
            "references_total": len(items),
            "references_pending": len(pending),
            "description": "sinal de cobertura e localização de evidências; não representa confiança da IA",
        },
    }
