from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable


def is_eligible(review: dict[str, Any]) -> bool:
    return (
        review.get("decision") == "aprovado"
        and review.get("training_eligible") is True
        and isinstance(review.get("corrected_payload"), dict)
        and bool(review["corrected_payload"])
    )


def split_for_dataset(submission_id: str, validation_ratio: float = 0.25) -> str:
    if not 0 < validation_ratio < 1:
        raise ValueError("validation_ratio deve estar entre zero e um")
    value = int(hashlib.sha256(submission_id.encode("utf-8")).hexdigest()[:8], 16) / 0xFFFFFFFF
    return "validation" if value < validation_ratio else "train"


def build_record(review: dict[str, Any], context: str, dataset_version: str) -> dict[str, Any]:
    if not is_eligible(review):
        raise ValueError("revisão não é elegível para treinamento")
    payload = review["corrected_payload"]
    return {
        "messages": [
            {"role": "system", "content": "Extraia dados regulatórios somente com evidência de página e trecho literal."},
            {"role": "user", "content": context},
            {"role": "assistant", "content": json.dumps(payload, ensure_ascii=False, sort_keys=True)},
        ],
        "metadata": {"submission_id": review.get("submission_id"), "review_id": review.get("review_id"), "dataset_version": dataset_version},
    }


def readiness(examples: Iterable[dict[str, Any]], minimum_train: int = 30, minimum_validation: int = 10) -> dict[str, Any]:
    counts = {"train": 0, "validation": 0}
    for example in examples:
        if example.get("split") in counts:
            counts[example["split"]] += 1
    return {"ready": counts["train"] >= minimum_train and counts["validation"] >= minimum_validation, "counts": counts, "minimums": {"train": minimum_train, "validation": minimum_validation}}
