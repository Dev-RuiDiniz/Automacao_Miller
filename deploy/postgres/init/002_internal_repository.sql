CREATE SCHEMA IF NOT EXISTS automacao_miller;

CREATE TABLE IF NOT EXISTS automacao_miller.documents (
    submission_id TEXT PRIMARY KEY,
    source TEXT NOT NULL DEFAULT 'landing',
    source_document_id TEXT,
    legacy_markdown_file_id TEXT,
    legacy_report_file_id TEXT,
    source_filename TEXT NOT NULL,
    source_sha256 CHAR(64) NOT NULL UNIQUE,
    mime_type TEXT NOT NULL DEFAULT 'application/pdf',
    size_bytes BIGINT NOT NULL CHECK (size_bytes > 0),
    source_storage_key TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('recebido', 'em_processamento', 'concluido', 'aguardando_revisao', 'erro')),
    current_stage TEXT NOT NULL DEFAULT 'recebido',
    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    started_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    report_storage_key TEXT,
    message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE automacao_miller.documents
    ADD COLUMN IF NOT EXISTS legacy_markdown_file_id TEXT,
    ADD COLUMN IF NOT EXISTS legacy_report_file_id TEXT;

CREATE INDEX IF NOT EXISTS documents_status_idx
    ON automacao_miller.documents (status, updated_at DESC);

CREATE TABLE IF NOT EXISTS automacao_miller.artifacts (
    artifact_id BIGSERIAL PRIMARY KEY,
    submission_id TEXT NOT NULL REFERENCES automacao_miller.documents(submission_id),
    artifact_type TEXT NOT NULL CHECK (artifact_type IN ('original_pdf', 'markdown', 'analysis_json', 'report_pdf')),
    version INTEGER NOT NULL CHECK (version > 0),
    storage_key TEXT NOT NULL,
    sha256 CHAR(64),
    size_bytes BIGINT CHECK (size_bytes IS NULL OR size_bytes >= 0),
    mime_type TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (submission_id, artifact_type, version),
    UNIQUE (storage_key)
);

CREATE INDEX IF NOT EXISTS artifacts_submission_idx
    ON automacao_miller.artifacts (submission_id, artifact_type, version DESC);

CREATE TABLE IF NOT EXISTS automacao_miller.processing_attempts (
    attempt_id BIGSERIAL PRIMARY KEY,
    submission_id TEXT NOT NULL REFERENCES automacao_miller.documents(submission_id),
    attempt_number INTEGER NOT NULL CHECK (attempt_number > 0),
    execution_id TEXT,
    current_stage TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('em_processamento', 'concluido', 'aguardando_revisao', 'erro')),
    error_category TEXT,
    error_message TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    UNIQUE (submission_id, attempt_number)
);

CREATE TABLE IF NOT EXISTS automacao_miller.analysis_results (
    analysis_id BIGSERIAL PRIMARY KEY,
    submission_id TEXT NOT NULL REFERENCES automacao_miller.documents(submission_id),
    attempt_id BIGINT REFERENCES automacao_miller.processing_attempts(attempt_id),
    markdown_artifact_id BIGINT REFERENCES automacao_miller.artifacts(artifact_id),
    model_name TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    confidence_status TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS analysis_results_submission_idx
    ON automacao_miller.analysis_results (submission_id, created_at DESC);

CREATE TABLE IF NOT EXISTS automacao_miller.human_reviews (
    review_id BIGSERIAL PRIMARY KEY,
    submission_id TEXT NOT NULL REFERENCES automacao_miller.documents(submission_id),
    reason TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('pendente', 'aprovado', 'rejeitado', 'reprocessamento_autorizado')),
    reviewer TEXT,
    notes TEXT,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ
);

ALTER TABLE automacao_miller.workflow_errors
    ADD COLUMN IF NOT EXISTS submission_id TEXT REFERENCES automacao_miller.documents(submission_id),
    ADD COLUMN IF NOT EXISTS attempt_id BIGINT REFERENCES automacao_miller.processing_attempts(attempt_id);

DO $$
BEGIN
    IF to_regclass('automacao_miller.submissions') IS NOT NULL THEN
        INSERT INTO automacao_miller.documents (
            submission_id, source, source_document_id, source_filename, source_sha256,
            mime_type, size_bytes, source_storage_key, status, current_stage,
            attempt_count, updated_at, report_storage_key, message, created_at
        )
        SELECT
            s.submission_id, 'legacy_drive', s.submission_id, s.filename, s.sha256,
            'application/pdf', GREATEST(COALESCE((pg_stat_file(s.source_path, true)).size, 1), 1),
            CASE
                WHEN s.source_path LIKE '/data/submissions/%'
                    THEN regexp_replace(s.source_path, '^/data/submissions/', 'legacy/submissions/')
                ELSE 'legacy/' || s.submission_id || '/original.pdf'
            END,
            CASE WHEN s.status = 'processando' THEN 'em_processamento'
                 WHEN s.status IN ('recebido', 'concluido', 'aguardando_revisao', 'erro') THEN s.status
                 ELSE 'erro' END,
            'migracao_legacy', 0, s.updated_at,
            CASE
                WHEN s.report_path LIKE '/data/submissions/%'
                    THEN regexp_replace(s.report_path, '^/data/submissions/', 'legacy/submissions/')
                ELSE NULL
            END,
            s.message, s.created_at
        FROM automacao_miller.submissions s
        ON CONFLICT DO NOTHING;

        INSERT INTO automacao_miller.artifacts
            (submission_id, artifact_type, version, storage_key, sha256, size_bytes, mime_type, metadata)
        SELECT d.submission_id, 'original_pdf', 1, d.source_storage_key,
               d.source_sha256, d.size_bytes, d.mime_type,
               jsonb_build_object('migrated_from', 'automacao_miller.submissions')
        FROM automacao_miller.documents d
        WHERE d.source = 'legacy_drive'
        ON CONFLICT DO NOTHING;

        INSERT INTO automacao_miller.artifacts
            (submission_id, artifact_type, version, storage_key, mime_type, metadata)
        SELECT d.submission_id, 'report_pdf', 1, d.report_storage_key,
               'application/pdf',
               jsonb_build_object('migrated_from', 'automacao_miller.submissions')
        FROM automacao_miller.documents d
        WHERE d.source = 'legacy_drive' AND d.report_storage_key IS NOT NULL
        ON CONFLICT DO NOTHING;
    END IF;

    IF to_regclass('automacao_miller.document_processing') IS NOT NULL THEN
        INSERT INTO automacao_miller.documents (
            submission_id, source, source_document_id, source_filename, source_sha256,
            mime_type, size_bytes, source_storage_key, status, current_stage,
            attempt_count, started_at, updated_at, completed_at,
            legacy_markdown_file_id, legacy_report_file_id, created_at
        )
        SELECT
            dp.source_document_id, 'legacy_drive', dp.source_document_id, dp.source_filename,
            dp.source_sha256, 'application/pdf', 1,
            'legacy/' || dp.source_document_id || '/original.pdf',
            dp.status, 'migracao_legacy', dp.attempt_count, dp.started_at, dp.updated_at,
            dp.completed_at, dp.markdown_file_id, dp.report_file_id, COALESCE(dp.updated_at, NOW())
        FROM automacao_miller.document_processing dp
        ON CONFLICT DO NOTHING;

        INSERT INTO automacao_miller.processing_attempts (
            submission_id, attempt_number, execution_id, current_stage, status,
            error_category, error_message, started_at, finished_at
        )
        SELECT
            dp.source_document_id, GREATEST(dp.attempt_count, 1), dp.execution_id,
            dp.current_stage, dp.status, dp.error_category, dp.error_message,
            COALESCE(dp.started_at, dp.updated_at, NOW()), dp.completed_at
        FROM automacao_miller.document_processing dp
        WHERE dp.attempt_count > 0
        ON CONFLICT (submission_id, attempt_number) DO NOTHING;
    END IF;
END $$;
