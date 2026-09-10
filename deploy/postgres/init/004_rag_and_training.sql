CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE automacao_miller.human_reviews
    ADD COLUMN IF NOT EXISTS corrected_payload JSONB,
    ADD COLUMN IF NOT EXISTS training_eligible BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS eligibility_reason TEXT;

CREATE TABLE IF NOT EXISTS automacao_miller.document_chunks (
    chunk_id BIGSERIAL PRIMARY KEY,
    submission_id TEXT NOT NULL REFERENCES automacao_miller.documents(submission_id) ON DELETE CASCADE,
    markdown_artifact_id BIGINT REFERENCES automacao_miller.artifacts(artifact_id),
    page_start INTEGER NOT NULL CHECK (page_start > 0),
    page_end INTEGER NOT NULL CHECK (page_end >= page_start),
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    content TEXT NOT NULL CHECK (length(content) > 0),
    content_sha256 CHAR(64) NOT NULL,
    embedding vector(768),
    content_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (submission_id, chunk_index),
    UNIQUE (submission_id, content_sha256)
);

CREATE INDEX IF NOT EXISTS document_chunks_text_idx
    ON automacao_miller.document_chunks USING GIN (content_tsv);
CREATE INDEX IF NOT EXISTS document_chunks_document_page_idx
    ON automacao_miller.document_chunks (submission_id, page_start, chunk_index);
CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx
    ON automacao_miller.document_chunks USING hnsw (embedding vector_cosine_ops)
    WHERE embedding IS NOT NULL;

CREATE TABLE IF NOT EXISTS automacao_miller.rag_retrievals (
    retrieval_id BIGSERIAL PRIMARY KEY,
    submission_id TEXT NOT NULL REFERENCES automacao_miller.documents(submission_id) ON DELETE CASCADE,
    chunk_id BIGINT NOT NULL REFERENCES automacao_miller.document_chunks(chunk_id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    result_rank INTEGER NOT NULL CHECK (result_rank > 0),
    lexical_score NUMERIC,
    semantic_score NUMERIC,
    combined_score NUMERIC,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS rag_retrievals_document_idx
    ON automacao_miller.rag_retrievals (submission_id, created_at DESC);

CREATE TABLE IF NOT EXISTS automacao_miller.quality_checks (
    quality_check_id BIGSERIAL PRIMARY KEY,
    submission_id TEXT NOT NULL REFERENCES automacao_miller.documents(submission_id) ON DELETE CASCADE,
    analysis_id BIGINT REFERENCES automacao_miller.analysis_results(analysis_id),
    status TEXT NOT NULL CHECK (status IN ('aprovado', 'aviso', 'rejeitado')),
    citation_coverage NUMERIC(5,4) NOT NULL CHECK (citation_coverage >= 0 AND citation_coverage <= 1),
    violations JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS automacao_miller.training_examples (
    example_id BIGSERIAL PRIMARY KEY,
    submission_id TEXT NOT NULL REFERENCES automacao_miller.documents(submission_id) ON DELETE CASCADE,
    review_id BIGINT NOT NULL REFERENCES automacao_miller.human_reviews(review_id) ON DELETE CASCADE,
    source_artifact_id BIGINT REFERENCES automacao_miller.artifacts(artifact_id),
    corrected_payload JSONB NOT NULL,
    split TEXT NOT NULL CHECK (split IN ('train', 'validation', 'excluded')),
    eligibility_reason TEXT NOT NULL,
    dataset_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (review_id)
);

CREATE TABLE IF NOT EXISTS automacao_miller.model_evaluations (
    evaluation_id BIGSERIAL PRIMARY KEY,
    model_name TEXT NOT NULL,
    model_version TEXT,
    dataset_version TEXT NOT NULL,
    metrics JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
