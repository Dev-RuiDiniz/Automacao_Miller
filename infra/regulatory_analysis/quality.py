from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any


REQUIRED_FIELDS = (
    "documento", "medicamentos_deferidos", "medicamentos_indeferidos",
    "suplementos_deferidos", "suplementos_indeferidos",
    "estudos_clinicos_deferidos", "estudos_clinicos_indeferidos", "outros_atos",
    "exigencias", "pendencias", "categorias_nao_localizadas",
    "evidencias_insuficientes", "contradicoes", "avisos",
    "controle_confianca", "revisao_humana",
)
FINDING_FIELDS = (
    "medicamentos_deferidos", "medicamentos_indeferidos",
    "suplementos_deferidos", "suplementos_indeferidos",
    "estudos_clinicos_deferidos", "estudos_clinicos_indeferidos",
    "outros_atos", "exigencias", "pendencias", "cancelados",
)
ALLOWED_STATUSES = {"deferido", "indeferido", "cancelado", "outro"}
PAGE_RE = re.compile(r"^##\s+Página\s+(\d+)\s*$", re.IGNORECASE)


@dataclass
class QualityResult:
    status: str
    citation_coverage: float
    violations: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    pages: list[int] = field(default_factory=list)

    @property
    def needs_review(self) -> bool:
        return bool(self.violations or self.warnings)

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "citation_coverage": self.citation_coverage,
            "violations": self.violations,
            "warnings": self.warnings,
            "pages": self.pages,
            "needs_review": self.needs_review,
        }


def normalize_evidence(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", value).strip().casefold()


def source_pages(markdown: str) -> dict[int, str]:
    pages: dict[int, list[str]] = {}
    current: int | None = None
    for line in str(markdown or "").splitlines():
        match = PAGE_RE.match(line.strip())
        if match:
            current = int(match.group(1))
            pages[current] = [line]
        elif current is not None:
            pages[current].append(line)
    return {page: "\n".join(lines) for page, lines in pages.items()}


def _violation(code: str, field: str, message: str, **extra: Any) -> dict[str, Any]:
    return {"code": code, "field": field, "message": message, **extra}


def validate_analysis(
    analysis: dict[str, Any],
    markdown: str,
    submission_id: str | None = None,
) -> QualityResult:
    """Valida qualidade documental sem transformar falha de qualidade em falha técnica."""
    violations: list[dict[str, Any]] = []
    warnings: list[str] = []
    if not isinstance(analysis, dict):
        return QualityResult("rejeitado", 0.0, [_violation("schema", "$", "A análise precisa ser um objeto JSON")])

    expected = set(REQUIRED_FIELDS) | {"cancelados"}
    for key in sorted(set(analysis) - expected):
        violations.append(_violation("unexpected_field", key, "Campo fora do schema"))
    for key in REQUIRED_FIELDS:
        if key not in analysis:
            violations.append(_violation("missing_field", key, "Campo obrigatório ausente"))
    pages = source_pages(markdown)
    all_pages = sorted(pages)
    cited = 0
    cited_valid = 0

    for field in FINDING_FIELDS:
        values = analysis.get(field, [])
        if not isinstance(values, list):
            violations.append(_violation("type", field, "Categoria precisa ser uma lista"))
            continue
        for index, item in enumerate(values):
            location = f"{field}[{index}]"
            cited += 1
            if not isinstance(item, dict):
                violations.append(_violation("citation_required", location, "Achado precisa conter página e evidência"))
                continue
            item_pages = item.get("paginas_origem")
            evidence = item.get("evidencia")
            if not isinstance(item_pages, list) or not item_pages:
                violations.append(_violation("page_required", location, "Achado sem paginas_origem"))
                continue
            if not isinstance(evidence, str) or not evidence.strip():
                violations.append(_violation("evidence_required", location, "Achado sem evidência curta"))
                continue
            invalid_pages = [page for page in item_pages if not isinstance(page, int) or page not in pages]
            if invalid_pages:
                violations.append(_violation("page_not_found", location, "Página não pertence ao documento atual", pages=invalid_pages))
                continue
            evidence_normalized = normalize_evidence(evidence)
            page_text = " ".join(normalize_evidence(pages[page]) for page in item_pages)
            if evidence_normalized not in page_text:
                violations.append(_violation("evidence_not_found", location, "Trecho não foi localizado na página indicada", pages=item_pages))
                continue
            cited_valid += 1
            status = item.get("status")
            if status is not None and status not in ALLOWED_STATUSES:
                violations.append(_violation("invalid_status", location, "Status regulatório inválido", status=status))
            if status == "cancelado" and field.endswith("indeferidos"):
                violations.append(_violation("cancelled_misclassified", location, "Cancelado deve permanecer separado de indeferido"))
            product_type = normalize_evidence(item.get("tipo_produto_relacionado", ""))
            if product_type == "dispositivo" and field.startswith(("medicamentos_", "suplementos_")):
                violations.append(_violation("device_in_product_category", location, "Dispositivo não pode ser classificado como medicamento ou suplemento"))

    for field in ("evidencias_insuficientes", "contradicoes", "avisos"):
        values = analysis.get(field, [])
        if not isinstance(values, list):
            violations.append(_violation("type", field, "Campo precisa ser uma lista"))
    confidence = analysis.get("controle_confianca")
    if not isinstance(confidence, dict) or confidence.get("status") not in {"aceitavel", "baixa_confianca", "inconclusivo"}:
        violations.append(_violation("confidence", "controle_confianca", "Controle de confiança inválido"))
    review = analysis.get("revisao_humana")
    if not isinstance(review, dict) or not isinstance(review.get("necessaria"), bool):
        violations.append(_violation("review", "revisao_humana", "Revisão humana inválida"))
    if submission_id and isinstance(analysis.get("documento"), dict):
        reported = analysis["documento"].get("submission_id") or analysis["documento"].get("protocolo")
        if reported and str(reported) != submission_id:
            violations.append(_violation("wrong_document", "documento", "A análise referencia outro documento", expected=submission_id, received=reported))
    if analysis.get("contradicoes"):
        warnings.append("Contradições preservadas exigem conferência das duas afirmações e suas páginas")
    if cited and cited_valid < cited:
        warnings.append("Há achados sem citação comprovável; o resultado é preliminar")
    coverage = cited_valid / cited if cited else 1.0
    status = "aprovado" if not violations and not warnings else "aviso"
    return QualityResult(status, round(coverage, 4), violations, warnings, all_pages)
