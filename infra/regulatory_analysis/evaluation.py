from __future__ import annotations

from typing import Any

from infra.regulatory_analysis.quality import FINDING_FIELDS, validate_analysis


def citation_metrics(predictions: list[dict[str, Any]], markdown_by_document: dict[str, str]) -> dict[str, float]:
    total = 0
    cited = 0
    schema_valid = 0
    for prediction in predictions:
        document_id = str(prediction.get("submission_id", ""))
        analysis = prediction.get("analysis", {})
        result = validate_analysis(analysis, markdown_by_document.get(document_id, ""), document_id)
        if not result.violations and isinstance(analysis, dict):
            schema_valid += 1
        for field in FINDING_FIELDS:
            for item in analysis.get(field, []) if isinstance(analysis, dict) and isinstance(analysis.get(field), list) else []:
                total += 1
                if isinstance(item, dict) and item.get("paginas_origem") and item.get("evidencia"):
                    cited += 1
    return {"schema_validity": schema_valid / len(predictions) if predictions else 0.0, "citation_coverage": cited / total if total else 1.0, "documents": float(len(predictions))}
