from infra.regulatory_analysis.report_validation import validate_report_references


SOURCE = "## Página 1\nAto publicado: produto A deferido.\n## Página 2\nExigência para produto B."


def report_reference(page: int, evidence: str) -> str:
    return f"- Página: {page}\n- Evidência literal: \"{evidence}\""


def test_confirms_page_and_literal_evidence_from_the_same_source_page() -> None:
    report = "# Relatório\n\n" + report_reference(1, "produto A deferido")

    result = validate_report_references(report, SOURCE, [1, 2])

    assert result["coverage"]["complete"] is True
    assert result["references"]["confirmed"] == 1
    assert result["references"]["pending"] == []
    assert result["validated_report_markdown"] == report


def test_marks_nonexistent_page_as_pending_without_blocking_the_result() -> None:
    result = validate_report_references(report_reference(99, "produto A deferido"), SOURCE, [1, 2])

    assert result["references"]["pending"][0]["code"] == "page_not_found"
    assert "Referência pendente (não comprovada)" in result["validated_report_markdown"]
    assert "Trecho alegado, não comprovado" in result["validated_report_markdown"]


def test_marks_missing_evidence_and_evidence_found_on_a_different_page() -> None:
    absent = validate_report_references(report_reference(1, "texto inventado"), SOURCE, [1, 2])
    elsewhere = validate_report_references(report_reference(1, "Exigência para produto B"), SOURCE, [1, 2])

    assert absent["references"]["pending"][0]["code"] == "evidence_not_found"
    assert elsewhere["references"]["pending"][0]["code"] == "evidence_found_on_other_page"
    assert elsewhere["references"]["pending"][0]["found_on_pages"] == [2]


def test_reports_incomplete_page_coverage_and_missing_references_as_warnings() -> None:
    result = validate_report_references("# Relatório sem referência", SOURCE, [1])

    assert result["coverage"]["complete"] is False
    assert result["coverage"]["missing_pages"] == [2]
    assert result["references"]["pending"][0]["code"] == "references_missing"


def test_parses_legacy_reference_tables_during_the_transition_to_bullets() -> None:
    report = "| Página | Evidência curta |\n|---|---|\n| 1 | produto A deferido |"

    result = validate_report_references(report, SOURCE, [1, 2])

    assert result["references"]["confirmed"] == 1


def test_marks_invalid_legacy_table_reference_as_pending_in_the_report() -> None:
    report = "| Página | Evidência curta |\n|---|---|\n| 99 | trecho inventado |"

    result = validate_report_references(report, SOURCE, [1, 2])

    assert result["references"]["pending"][0]["code"] == "page_not_found"
    assert "Referência pendente (não comprovada)" in result["validated_report_markdown"]
    assert "| 99 | trecho inventado |" not in result["validated_report_markdown"]
