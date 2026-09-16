from __future__ import annotations

from types import SimpleNamespace

from infra.rag import app


def test_embeddings_uses_batches_and_preserves_order(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_post(_url, *, json, timeout):
        del timeout
        calls.append(json["input"])
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"embeddings": [[float(index)] * 3 for index, _ in enumerate(json["input"])]},
        )

    monkeypatch.setattr(app.httpx, "post", fake_post)
    monkeypatch.setenv("RAG_EMBEDDING_DIMENSION", "3")

    result = app.embeddings(["a", "b", "c", "d", "e"], batch_size=2)

    assert calls == [["a", "b"], ["c", "d"], ["e"]]
    assert result == [[0.0] * 3, [1.0] * 3, [0.0] * 3, [1.0] * 3, [0.0] * 3]


def test_semantic_search_is_opt_in_for_extensive_documents(monkeypatch) -> None:
    monkeypatch.delenv("RAG_ENABLE_SEMANTIC_SEARCH", raising=False)
    assert app.semantic_search_enabled() is False

    monkeypatch.setenv("RAG_ENABLE_SEMANTIC_SEARCH", "true")
    assert app.semantic_search_enabled() is True
