from pathlib import Path

import pytest

from infra.regulatory_analysis.deterministic_context import build_deterministic_context


def test_context_keeps_literal_terms_and_links_process_across_pages() -> None:
    identifier = "25351.123456/2024-78"
    markdown = (
        "---\npage_count: 3\n---\n"
        "## Página 1\nProcesso " + identifier + ": medicamento deferido.\n"
        "## Página 2\nProcesso " + identifier + ": exigência publicada.\n"
        "## Página 3\nProcesso 25351.654321/2024-10: produto cancelado."
    )

    result = build_deterministic_context(markdown)

    assert result["pages_processed"] == [1, 2, 3]
    assert {item["term"].lower() for item in result["anchors"] if item["kind"] == "termo_literal"} >= {
        "deferido",
        "exigência",
        "publicada",
        "cancelado",
    }
    linked = next(item for item in result["cross_page_links"] if item["identifier"] == identifier)
    assert linked["pages"] == [1, 2]
    assert [item["page"] for item in linked["occurrences"]] == [1, 2]
    assert all(identifier in item["evidence"] for item in linked["occurrences"])


def test_repeated_text_on_different_pages_keeps_both_page_references() -> None:
    markdown = "## Página 1\nAto deferido.\n## Página 2\nAto deferido."

    result = build_deterministic_context(markdown)
    anchors = [item for item in result["anchors"] if item["term"].lower() == "deferido"]

    assert [item["page"] for item in anchors] == [1, 2]


def test_synthetic_fixture_finds_deadline_without_treating_document_text_as_instruction() -> None:
    fixture = Path(__file__).parents[1] / "fixtures" / "synthetic-regulatory-sample.md"

    result = build_deterministic_context(fixture.read_text(encoding="utf-8"))

    deadlines = [item for item in result["anchors"] if item["term"].lower() == "prazo"]
    assert deadlines
    assert all(item["page"] == 1 for item in deadlines)
    assert all("status" not in item for item in result["anchors"])


@pytest.mark.parametrize(
    "markdown",
    [
        "Documento sem página.",
        "## Página 1\nA\n## Página 1\nB",
        "## Página 1\nA\n## Página 3\nB",
    ],
)
def test_invalid_page_markers_fail_instead_of_claiming_complete_context(markdown: str) -> None:
    with pytest.raises(ValueError):
        build_deterministic_context(markdown)
