DO $$
BEGIN
    ALTER TABLE automacao_miller.documents DROP CONSTRAINT IF EXISTS documents_status_check;
    ALTER TABLE automacao_miller.documents
        ADD CONSTRAINT documents_status_check CHECK (status IN ('recebido', 'em_processamento', 'processando', 'aguardando_revisao', 'aguardando_envio', 'concluido', 'erro'));
EXCEPTION WHEN undefined_table THEN
    NULL;
END $$;

ALTER TABLE automacao_miller.processing_attempts
    DROP CONSTRAINT IF EXISTS processing_attempts_status_check;

ALTER TABLE automacao_miller.processing_attempts
    ADD CONSTRAINT processing_attempts_status_check CHECK (status IN ('em_processamento', 'aguardando_revisao', 'aguardando_envio', 'concluido', 'erro'));

CREATE TABLE IF NOT EXISTS automacao_miller.report_recipients (
    recipient_id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    label TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS automacao_miller.document_recipients (
    submission_id TEXT NOT NULL REFERENCES automacao_miller.documents(submission_id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    position INTEGER NOT NULL CHECK (position > 0),
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (submission_id, email)
);

CREATE TABLE IF NOT EXISTS automacao_miller.email_deliveries (
    delivery_id BIGSERIAL PRIMARY KEY,
    submission_id TEXT NOT NULL REFERENCES automacao_miller.documents(submission_id),
    recipient_emails JSONB NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('solicitado', 'enviando', 'enviado', 'falhou')),
    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    execution_id TEXT,
    requested_by TEXT NOT NULL,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sent_at TIMESTAMPTZ,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS email_deliveries_pending_idx
    ON automacao_miller.email_deliveries (status, requested_at);
