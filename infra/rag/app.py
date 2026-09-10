from __future__ import annotations

import hashlib
import os
from typing import Any

import httpx
import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from psycopg.types.json import Json

from infra.rag.chunker import split_markdown_by_page
from infra.rag.search import hybrid_query
from infra.regulatory_analysis.quality import validate_analysis

try:
    from pgvector.psycopg import register_vector
except ImportError:  # pragma: no cover - somente ambiente sem a dependência opcional
    register_vector = None


app = FastAPI(title="Automação Miller RAG", version="1.0.0")


def env_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def env_float(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))


class IndexRequest(BaseModel):
    submission_id: str = Field(min_length=1)
    markdown: str = Field(min_length=1)
    markdown_sha256: str | None = None
    markdown_artifact_id: int | None = None


class SearchRequest(BaseModel):
    submission_id: str = Field(min_length=1)
    queries: list[str] = Field(min_length=1, max_length=20)
    top_k: int | None = Field(default=None, ge=1, le=50)


class ValidateRequest(BaseModel):
    submission_id: str = Field(min_length=1)
    analysis: dict[str, Any]


def db_connection() -> psycopg.Connection:
    connection = psycopg.connect(os.environ["DATABASE_URL"])
    if register_vector:
        register_vector(connection)
    return connection


def embedding(text: str) -> list[float]:
    url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434").rstrip("/") + "/api/embeddings"
    response = httpx.post(url, json={"model": os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"), "prompt": text}, timeout=120)
    response.raise_for_status()
    values = response.json().get("embedding")
    if not isinstance(values, list) or not values:
        raise RuntimeError("Ollama não retornou embedding")
    expected = env_int("RAG_EMBEDDING_DIMENSION", 768)
    if len(values) != expected:
        raise RuntimeError(f"Embedding com dimensão {len(values)}; esperado {expected}")
    return [float(value) for value in values]


def ensure_document(connection: psycopg.Connection, submission_id: str) -> None:
    if not connection.execute("SELECT 1 FROM automacao_miller.documents WHERE submission_id = %s", (submission_id,)).fetchone():
        raise HTTPException(status_code=404, detail="Documento não encontrado")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/index")
def index_markdown(payload: IndexRequest) -> dict[str, Any]:
    digest = hashlib.sha256(payload.markdown.encode("utf-8")).hexdigest()
    if payload.markdown_sha256 and payload.markdown_sha256.lower() != digest:
        raise HTTPException(status_code=422, detail="Hash do Markdown não confere")
    chunks = split_markdown_by_page(payload.markdown, env_int("RAG_CHUNK_SIZE", 1200), env_int("RAG_CHUNK_OVERLAP", 150))
    if not chunks:
        raise HTTPException(status_code=422, detail="Markdown não contém marcadores de página")
    try:
        with db_connection() as connection:
            ensure_document(connection, payload.submission_id)
            connection.execute("DELETE FROM automacao_miller.document_chunks WHERE submission_id = %s", (payload.submission_id,))
            for chunk in chunks:
                vector = embedding(chunk.content)
                connection.execute(
                    """
                    INSERT INTO automacao_miller.document_chunks
                    (submission_id, markdown_artifact_id, page_start, page_end, chunk_index, content, content_sha256, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (submission_id, chunk_index) DO UPDATE SET
                      content = EXCLUDED.content, content_sha256 = EXCLUDED.content_sha256,
                      embedding = EXCLUDED.embedding, page_start = EXCLUDED.page_start,
                      page_end = EXCLUDED.page_end, markdown_artifact_id = EXCLUDED.markdown_artifact_id
                    """,
                    (payload.submission_id, payload.markdown_artifact_id, chunk.page_start, chunk.page_end, chunk.chunk_index, chunk.content, chunk.content_sha256, vector),
                )
            connection.commit()
    except HTTPException:
        raise
    except (httpx.HTTPError, psycopg.Error, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=f"Falha ao indexar Markdown: {exc}") from exc
    return {"submission_id": payload.submission_id, "chunks": len(chunks), "markdown_sha256": digest}


@app.post("/v1/search")
def search(payload: SearchRequest) -> dict[str, Any]:
    top_k = payload.top_k or env_int("RAG_TOP_K", 8)
    lexical_weight = env_float("RAG_HYBRID_LEXICAL_WEIGHT", 0.45)
    semantic_weight = env_float("RAG_HYBRID_SEMANTIC_WEIGHT", 0.55)
    found: dict[int, dict[str, Any]] = {}
    try:
        with db_connection() as connection:
            ensure_document(connection, payload.submission_id)
            for query_text in payload.queries:
                vector = embedding(query_text)
                params = {
                    "submission_id": payload.submission_id,
                    "query": query_text,
                    "embedding": vector,
                    "candidate_limit": max(top_k * 4, 20),
                    "top_k": top_k,
                    "lexical_weight": lexical_weight,
                    "semantic_weight": semantic_weight,
                }
                rows = connection.execute(hybrid_query(), params).fetchall()
                for rank, row in enumerate(rows, start=1):
                    chunk_id, page_start, page_end, content, lexical, semantic = row
                    combined = float(lexical) * lexical_weight + float(semantic) * semantic_weight
                    found[chunk_id] = {"chunk_id": chunk_id, "page_start": page_start, "page_end": page_end, "content": content, "lexical_score": float(lexical), "semantic_score": float(semantic), "combined_score": combined, "query": query_text, "rank": rank}
            ranked = sorted(found.values(), key=lambda item: item["combined_score"], reverse=True)[:top_k]
            for rank, item in enumerate(ranked, start=1):
                connection.execute(
                    """
                    INSERT INTO automacao_miller.rag_retrievals
                    (submission_id, chunk_id, query_text, result_rank, lexical_score, semantic_score, combined_score)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (payload.submission_id, item["chunk_id"], item["query"], rank, item["lexical_score"], item["semantic_score"], item["combined_score"]),
                )
            connection.commit()
    except HTTPException:
        raise
    except (httpx.HTTPError, psycopg.Error, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=f"Falha na busca RAG: {exc}") from exc
    return {"submission_id": payload.submission_id, "chunks": ranked}


@app.post("/v1/validate")
def validate(payload: ValidateRequest) -> dict[str, Any]:
    try:
        with db_connection() as connection:
            ensure_document(connection, payload.submission_id)
            rows = connection.execute(
                "SELECT content FROM automacao_miller.document_chunks WHERE submission_id = %s ORDER BY chunk_index",
                (payload.submission_id,),
            ).fetchall()
    except (psycopg.Error,) as exc:
        raise HTTPException(status_code=502, detail=f"Falha ao carregar contexto de validação: {exc}") from exc
    markdown = "\n\n".join(row[0] for row in rows)
    result = validate_analysis(payload.analysis, markdown, payload.submission_id)
    try:
        with db_connection() as connection:
            connection.execute(
                "INSERT INTO automacao_miller.quality_checks (submission_id, status, citation_coverage, violations) VALUES (%s, %s, %s, %s)",
                (payload.submission_id, result.status, result.citation_coverage, Json(result.violations + [{"code": "warning", "message": item} for item in result.warnings])),
            )
            connection.commit()
    except psycopg.Error as exc:
        raise HTTPException(status_code=502, detail=f"Falha ao registrar validação: {exc}") from exc
    return {"submission_id": payload.submission_id, **result.as_dict(), "analysis": payload.analysis}
