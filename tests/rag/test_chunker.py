from infra.rag.chunker import split_markdown_by_page


def test_split_preserves_pages_and_hashes() -> None:
    chunks = split_markdown_by_page("## Página 71\nAlcovit deferido.\n## Página 79\nResolução 3295.", chunk_size=200)
    assert [(item.page_start, item.page_end) for item in chunks] == [(71, 71), (79, 79)]
    assert len(chunks[0].content_sha256) == 64
    assert chunks[0].content_sha256 != chunks[1].content_sha256


def test_long_page_uses_overlap_without_losing_page_marker() -> None:
    chunks = split_markdown_by_page("## Página 75\n" + "abc " * 40, chunk_size=40, chunk_overlap=8)
    assert len(chunks) > 1
    assert all(item.page_start == 75 for item in chunks)
    assert any(chunks[0].content[-8:].strip() in item.content for item in chunks[1:])
