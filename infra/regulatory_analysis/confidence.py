from __future__ import annotations

from typing import Any


CATEGORY_FIELDS = (
    "medicamentos_deferidos",
    "medicamentos_indeferidos",
    "suplementos_deferidos",
    "suplementos_indeferidos",
    "estudos_clinicos_deferidos",
    "estudos_clinicos_indeferidos",
    "outros_atos",
)


def _has_page_evidence(item: Any) -> bool:
    if not isinstance(item, dict):
        return False
    for key in ("paginas_origem", "paginas", "evidencias"):
        value = item.get(key)
        if value:
            return True
    return False


def classify_confidence(analysis: dict[str, Any], conversion_warnings: list[str]) -> dict[str, Any]:
    reasons: list[str] = []
    if analysis.get("contradicoes"):
        reasons.append("contradicao")
    if analysis.get("evidencias_insuficientes"):
        reasons.append("evidencia insuficiente")
    if conversion_warnings:
        reasons.append("aviso de layout ou conversao")
    if analysis.get("revisao_humana", {}).get("necessaria"):
        reasons.append("revisao humana solicitada")

    missing_evidence = any(
        isinstance(analysis.get(field), list)
        and any(not _has_page_evidence(item) for item in analysis[field])
        for field in CATEGORY_FIELDS
    )
    if missing_evidence:
        reasons.append("item sem evidencia de pagina")

    if analysis.get("contradicoes"):
        status = "inconclusivo"
    elif reasons:
        status = "baixa_confianca"
    else:
        status = "aceitavel"
    return {"status": status, "motivos": list(dict.fromkeys(reasons))}
