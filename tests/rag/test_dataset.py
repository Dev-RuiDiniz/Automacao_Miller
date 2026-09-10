from infra.regulatory_analysis.dataset import build_record, is_eligible, readiness, split_for_dataset


def review(decision="aprovado", eligible=True):
    return {"review_id": 1, "submission_id": "doc-1", "decision": decision, "training_eligible": eligible, "corrected_payload": {"documento": {"submission_id": "doc-1"}}}


def test_dataset_accepts_only_approved_complete_review() -> None:
    assert is_eligible(review())
    assert not is_eligible(review("rejeitado"))
    assert not is_eligible(review(eligible=False))
    record = build_record(review(), "## Página 71\nEvidência", "v1")
    assert record["metadata"]["dataset_version"] == "v1"
    assert record["messages"][-1]["role"] == "assistant"


def test_split_is_deterministic_and_readiness_has_separate_thresholds() -> None:
    assert split_for_dataset("doc-1") == split_for_dataset("doc-1")
    assert readiness([{"split": "train"}] * 30 + [{"split": "validation"}] * 10)["ready"]
    assert not readiness([{"split": "train"}] * 30)["ready"]
