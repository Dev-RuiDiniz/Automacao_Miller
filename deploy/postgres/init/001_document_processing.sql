CREATE SCHEMA IF NOT EXISTS automacao_miller;

CREATE TABLE IF NOT EXISTS automacao_miller.document_processing (
    source_document_id TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    source_filename TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('recebido', 'em_processamento', 'concluido', 'aguardando_revisao', 'erro')),
    current_stage TEXT NOT NULL,
    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    started_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_category TEXT,
    error_message TEXT,
    execution_id TEXT,
    markdown_file_id TEXT,
    report_file_id TEXT,
    PRIMARY KEY (source_document_id, source_sha256)
);

CREATE INDEX IF NOT EXISTS document_processing_status_idx
    ON automacao_miller.document_processing (status, updated_at DESC);

CREATE TABLE IF NOT EXISTS automacao_miller.workflow_errors (
    id BIGSERIAL PRIMARY KEY,
    source_document_id TEXT,
    status TEXT NOT NULL DEFAULT 'erro',
    current_stage TEXT NOT NULL,
    error_category TEXT NOT NULL,
    error_message TEXT NOT NULL,
    execution_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
