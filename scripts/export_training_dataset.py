from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import psycopg

from infra.regulatory_analysis.dataset import build_record, readiness, split_for_dataset


def main() -> int:
    parser = argparse.ArgumentParser(description="Exporta apenas revisões humanas aprovadas para JSONL protegido")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dataset-version", default="regulatory-v1")
    args = parser.parse_args()
    rows: list[dict] = []
    with psycopg.connect(os.environ["DATABASE_URL"]) as connection:
        records = connection.execute(
            """
            SELECT r.review_id, r.submission_id, r.decision, r.corrected_payload, r.training_eligible,
                   COALESCE(string_agg(c.content, E'\\n\\n' ORDER BY c.chunk_index), '') AS context
            FROM automacao_miller.human_reviews r
            LEFT JOIN automacao_miller.document_chunks c ON c.submission_id = r.submission_id
            WHERE r.decision = 'aprovado' AND r.training_eligible = TRUE AND r.corrected_payload IS NOT NULL
            GROUP BY r.review_id, r.submission_id, r.decision, r.corrected_payload, r.training_eligible
            ORDER BY r.review_id
            """
        ).fetchall()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for review_id, submission_id, decision, corrected, eligible, context in records:
            review = {"review_id": review_id, "submission_id": submission_id, "decision": decision, "corrected_payload": corrected, "training_eligible": eligible}
            split = split_for_dataset(str(submission_id))
            record = build_record(review, context, args.dataset_version)
            record["metadata"]["split"] = split
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            rows.append({"submission_id": submission_id, "split": split})
    manifest = readiness(rows)
    manifest["dataset_version"] = args.dataset_version
    args.output.with_suffix(".manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
