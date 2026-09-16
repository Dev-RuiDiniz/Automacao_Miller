-- O fluxo ativo produz o relatório técnico em Markdown antes do PDF final.
-- A alteração é aditiva e mantém os artefatos legados compatíveis.
ALTER TABLE automacao_miller.artifacts
    DROP CONSTRAINT IF EXISTS artifacts_artifact_type_check;

ALTER TABLE automacao_miller.artifacts
    ADD CONSTRAINT artifacts_artifact_type_check
    CHECK (artifact_type IN ('original_pdf', 'markdown', 'analysis_json', 'report_markdown', 'report_pdf'));
