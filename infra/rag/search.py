from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoredChunk:
    chunk_id: int
    page_start: int
    page_end: int
    content: str
    lexical_score: float
    semantic_score: float
    combined_score: float


def combine_scores(lexical_score: float, semantic_score: float, lexical_weight: float = 0.45, semantic_weight: float = 0.55) -> float:
    if lexical_weight < 0 or semantic_weight < 0 or lexical_weight + semantic_weight <= 0:
        raise ValueError("pesos de busca inválidos")
    total = lexical_weight + semantic_weight
    return (lexical_score * lexical_weight + semantic_score * semantic_weight) / total


def hybrid_query() -> str:
    """Consulta parametrizada: o filtro do documento é obrigatório."""
    return """
        WITH lexical AS (
            SELECT chunk_id, ts_rank_cd(content_tsv, plainto_tsquery('simple', %(query)s)) AS lexical_score
            FROM automacao_miller.document_chunks
            WHERE submission_id = %(submission_id)s
              AND content_tsv @@ plainto_tsquery('simple', %(query)s)
        ), semantic AS (
            SELECT chunk_id, 1 - (embedding <=> %(embedding)s::vector) AS semantic_score
            FROM automacao_miller.document_chunks
            WHERE submission_id = %(submission_id)s AND embedding IS NOT NULL
            ORDER BY embedding <=> %(embedding)s::vector
            LIMIT %(candidate_limit)s
        )
        SELECT c.chunk_id, c.page_start, c.page_end, c.content,
               COALESCE(l.lexical_score, 0) AS lexical_score,
               COALESCE(s.semantic_score, 0) AS semantic_score
        FROM automacao_miller.document_chunks c
        LEFT JOIN lexical l ON l.chunk_id = c.chunk_id
        LEFT JOIN semantic s ON s.chunk_id = c.chunk_id
        WHERE c.submission_id = %(submission_id)s
          AND (l.chunk_id IS NOT NULL OR s.chunk_id IS NOT NULL)
        ORDER BY (COALESCE(l.lexical_score, 0) * %(lexical_weight)s)
               + (COALESCE(s.semantic_score, 0) * %(semantic_weight)s) DESC
        LIMIT %(top_k)s
    """
