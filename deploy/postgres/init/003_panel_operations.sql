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
