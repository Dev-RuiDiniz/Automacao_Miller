BEGIN;

-- Compatibilidade com protocolos que já tinham relatório na versão anterior.
WITH migrated_documents AS (
    UPDATE automacao_miller.documents d
    SET status = 'concluido', current_stage = 'relatorio_pronto',
        completed_at = COALESCE(d.completed_at, pdf.created_at),
        updated_at = NOW(), message = NULL
    FROM automacao_miller.artifacts pdf
    WHERE pdf.submission_id = d.submission_id
      AND pdf.artifact_type = 'report_pdf'
      AND pdf.storage_key = d.report_storage_key
      AND pdf.version = d.attempt_count
      AND (
          d.status = 'aguardando_envio'
          OR (d.status = 'erro' AND (
              d.current_stage IN ('Gmail - Send report', 'State - Report sent', 'Internal Storage - Read report')
              OR (d.current_stage = 'relatorio_pronto' AND d.message = 'Falha ao iniciar o envio do relatório.')
          ))
      )
    RETURNING d.submission_id, d.attempt_count, d.completed_at
)
UPDATE automacao_miller.processing_attempts pa
SET status = 'concluido', current_stage = 'relatorio_pronto',
    finished_at = COALESCE(pa.finished_at, d.completed_at),
    error_category = NULL, error_message = NULL
FROM migrated_documents d
WHERE pa.submission_id = d.submission_id AND pa.attempt_number = d.attempt_count;

UPDATE automacao_miller.processing_attempts pa
SET status = 'concluido', current_stage = 'relatorio_pronto',
    finished_at = COALESCE(pa.finished_at, pdf.created_at)
FROM automacao_miller.artifacts pdf
WHERE pa.status = 'aguardando_envio' AND pdf.artifact_type = 'report_pdf'
  AND pdf.submission_id = pa.submission_id AND pdf.version = pa.attempt_number;

UPDATE automacao_miller.documents
SET status = 'erro', current_stage = 'relatorio_indisponivel', updated_at = NOW(),
    message = 'PDF do relatório não localizado. Reprocesse o documento.'
WHERE status = 'aguardando_envio';

UPDATE automacao_miller.processing_attempts
SET status = 'erro', current_stage = 'relatorio_indisponivel',
    error_category = 'armazenamento', error_message = 'PDF do relatório não localizado.',
    finished_at = COALESCE(finished_at, NOW())
WHERE status = 'aguardando_envio';

UPDATE automacao_miller.documents SET current_stage = 'relatorio_pronto'
WHERE status = 'concluido' AND current_stage = 'email_enviado';

UPDATE automacao_miller.processing_attempts SET current_stage = 'relatorio_pronto'
WHERE status = 'concluido' AND current_stage = 'email_enviado';

ALTER TABLE automacao_miller.documents DROP CONSTRAINT IF EXISTS documents_status_check;
ALTER TABLE automacao_miller.documents ADD CONSTRAINT documents_status_check
    CHECK (status IN ('recebido', 'em_processamento', 'processando', 'aguardando_revisao', 'concluido', 'erro'));

ALTER TABLE automacao_miller.processing_attempts DROP CONSTRAINT IF EXISTS processing_attempts_status_check;
ALTER TABLE automacao_miller.processing_attempts ADD CONSTRAINT processing_attempts_status_check
    CHECK (status IN ('em_processamento', 'aguardando_revisao', 'concluido', 'erro'));

COMMIT;
