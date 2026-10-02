import json
from pathlib import Path


ROOT = Path(__file__).parents[2]


def test_remote_vps_status_is_explicitly_historical() -> None:
    roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
    log = (ROOT / "LOG.md").read_text(encoding="utf-8")

    assert "Última observação da VPS (2026-09-23)" in roadmap
    assert "a VPS não foi consultada nesta atualização" in roadmap
    assert "O estado remoto atual é desconhecido" in roadmap
    assert "não foram verificados novamente em 2026-10-02" in roadmap
    assert "(registro histórico)" in log
    assert "Esses estados não foram verificados em 2026-10-02" in log
    assert "VPS ainda precisa ser alinhada" not in log


def test_product_docs_match_active_markdown_report_flow() -> None:
    prd = " ".join((ROOT / "PRD.md").read_text(encoding="utf-8").split())
    readme = " ".join((ROOT / "README.md").read_text(encoding="utf-8").split())
    workflows = " ".join((ROOT / "workflows" / "README.md").read_text(encoding="utf-8").split())
    audit = " ".join((ROOT / "RELATORIO_AUDITORIA_PROJETO.md").read_text(encoding="utf-8").split())

    assert "a saída persistida do MVP é o" in prd
    assert "RAG, embeddings, `quality_checks`, análise JSON persistida e nota de confiança" in prd
    assert "prioridade das ações, não uma medida de confiança" in prd
    assert "A saída persistida é o relatório" in readme
    assert "RAG, embeddings e `quality_checks` não são chamados pelo workflow ativo" in readme
    assert "não confiança" in readme
    assert "analysis-v1.json" not in workflows
    assert "o fluxo atual não grava análise estruturada" in workflows
    assert "Aviso de vigência" in audit
    assert "não foi consultada em 2026-10-02; seu estado atual é desconhecido" in audit


def test_compose_declares_isolated_required_services() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    for service in ("postgres:", "ollama:", "rag-service:", "pdf-converter:", "report-renderer:", "n8n:"):
        assert service in compose
    assert "pgvector/pgvector:pg15" in compose
    rag_service = compose.split("  rag-service:\n", 1)[1].split("\n  pdf-converter:", 1)[0]
    n8n_service = compose.split("  n8n:\n", 1)[1].split("\nvolumes:", 1)[0]
    assert 'profiles: ["rag"]' in rag_service
    assert "RAG_ENABLE_SEMANTIC_SEARCH" in rag_service
    assert "RAG_SERVICE_BASE_URL" not in n8n_service
    assert "RAG_TOP_K" not in n8n_service
    assert "rag-service:" not in n8n_service
    assert "N8N_INTERNAL_PROCESSING_WEBHOOK_URL" in n8n_service
    assert "N8N_REPORT_EMAIL_WEBHOOK_URL" in n8n_service
    assert "127.0.0.1:${N8N_HOST_PORT:-25678}:5678" in compose
    assert "automacao_miller_n8n_data" in compose
    assert "automacao_miller_artifacts_data:/data/artifacts" in compose
    assert "ARTIFACT_STORAGE_DIR" in compose
    assert "N8N_RESTRICT_FILE_ACCESS_TO" in compose
    assert "PDF_CONVERTER_TIMEOUT_SECONDS:-300" in compose
    assert "automacao_miller_submission_data:" in compose
    assert '"${ARTIFACTS_GID:-10002}"' in compose
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "RAG é legado/optativo" in env_example
    deployment = (ROOT / "deploy" / "README.md").read_text(encoding="utf-8")
    assert "não inicia `rag-service`" in deployment
    assert "6.912 MiB (6,75 GiB)" in deployment
    assert "docker compose --profile rag up -d rag-service" in deployment
    entrypoint = (ROOT / "infra" / "upload_gateway" / "entrypoint.sh").read_text(encoding="utf-8")
    assert "chmod 2770" in entrypoint


def test_workflow_export_is_valid_and_contains_required_stages() -> None:
    workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-v1.json").read_text(encoding="utf-8"))
    names = {node["name"] for node in workflow["nodes"]}
    assert {
        "Google Drive - Search input PDFs",
        "Google Drive - Move to processing",
        "PDF Converter",
        "Prepare AI context",
        "Reliable AI page scope",
        "Normalize AI response",
        "Ollama - Extract",
        "Report Renderer",
        "Gmail - Send report",
        "Route after email",
    } <= names
    assert workflow["id"] == "automacao-regulatoria-mvp"
    assert workflow["active"] is False
    assert workflow["settings"]["errorWorkflow"] == "automacao-regulatoria-error-handler"
    converter = next(node for node in workflow["nodes"] if node["name"] == "PDF Converter")
    parameters = converter["parameters"]["bodyParameters"]["parameters"]
    assert {item["parameterType"] for item in parameters} == {"formBinaryData", "formData"}
    assert next(item for item in parameters if item["parameterType"] == "formBinaryData")["inputDataFieldName"] == "data"
    gmail = next(node for node in workflow["nodes"] if node["name"] == "Gmail - Send report")
    assert gmail["parameters"]["options"]["attachmentsUi"]["attachmentsBinary"] == [{"property": "data"}]
    assert workflow["connections"]["Duplicate gate"]["main"][0][0]["node"] == "Duplicate ignored"
    assert workflow["connections"]["Duplicate gate"]["main"][1][0]["node"] == "Prepare Markdown file"
    assert workflow["connections"]["Route after email"]["main"][0][0]["node"] == "State - Completed"
    assert workflow["connections"]["Route after email"]["main"][1][0]["node"] == "State - Human review"


def test_error_workflow_export_records_failures() -> None:
    workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-error-v1.json").read_text(encoding="utf-8"))
    names = {node["name"] for node in workflow["nodes"]}
    assert {"Error Trigger", "Normalize error context", "Record workflow error"} <= names
    assert workflow["id"] == "automacao-regulatoria-error-handler"


def test_internal_error_workflow_avoids_code_runner() -> None:
    workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-internal-error-v1.json").read_text(encoding="utf-8"))
    normalize = next(node for node in workflow["nodes"] if node["name"] == "Normalize internal error")
    assert normalize["type"] == "n8n-nodes-base.set"
    assert normalize["typeVersion"] == 3.4
    assignments = normalize["parameters"]["assignments"]["assignments"]
    fields = {item["name"]: item["value"] for item in assignments}
    assert {"submission_id", "delivery_id", "current_stage", "error_category", "error_message", "execution_id"} == set(fields)
    assert "$json.workflowData" in fields["submission_id"]
    assert "$json.execution?.error" in fields["error_message"]
    assert normalize["parameters"]["includeOtherFields"] is False
    assert not any(node["type"] == "n8n-nodes-base.code" for node in workflow["nodes"])
    record = next(node for node in workflow["nodes"] if node["name"] == "Record internal error")
    query = record["parameters"]["query"]
    assert query.startswith("WITH error_context AS (")
    assert "UPDATE automacao_miller.processing_attempts" in query
    assert "UPDATE automacao_miller.documents" in query
    assert "UPDATE automacao_miller.email_deliveries" in query
    assert "; UPDATE" not in query


def test_internal_workflow_uses_simple_markdown_report_path() -> None:
    workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-internal-v1.json").read_text(encoding="utf-8"))
    error_workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-internal-error-v1.json").read_text(encoding="utf-8"))
    names = {node["name"] for node in workflow["nodes"]}
    node_types = {node["type"] for node in workflow["nodes"]}

    assert workflow["id"] == "automacao-regulatoria-internal"
    assert workflow["active"] is False
    assert workflow["settings"]["errorWorkflow"] == "automacao-reg-error-handler"
    assert workflow["settings"]["errorWorkflow"] == error_workflow["id"]
    assert error_workflow["active"] is False
    assert {
        "Landing - Receber documento",
        "State - Claim document",
        "State - Start attempt",
        "Internal Storage - Read PDF",
        "PDF Converter",
        "Validate Markdown",
        "Internal Storage - Write Markdown",
        "Prepare analysis batches",
        "Ollama - Analyze each batch",
        "Merge batch findings and prepare report",
        "Ollama - Generate report Markdown",
        "Validate report Markdown",
        "Gateway - Validate report evidence",
        "Accept evidence validation and add signal",
        "Internal Storage - Write report Markdown",
        "Report Renderer",
        "Internal Storage - Write report PDF",
        "State - Report persisted",
    } <= names
    read_pdf = next(node for node in workflow["nodes"] if node["name"] == "Internal Storage - Read PDF")
    assert "$('Claim guard').item.json.source_storage_key" in read_pdf["parameters"]["filePath"]
    claim_guard = next(node for node in workflow["nodes"] if node["name"] == "Claim guard")
    assert "items[0].json?.submission_id" in claim_guard["parameters"]["jsCode"]
    assert "Gmail - Send report" not in names
    assert "n8n-nodes-base.googleDrive" not in node_types
    assert "automacao_miller.documents" in next(node for node in workflow["nodes"] if node["name"] == "State - Claim document")["parameters"]["query"]
    assert "/data/artifacts/" in " ".join(json.dumps(node["parameters"]) for node in workflow["nodes"])

    markdown_state = next(node for node in workflow["nodes"] if node["name"] == "State - Markdown persisted")
    assert "Internal Storage - Prepare keys" in markdown_state["parameters"]["query"]
    report_markdown_state = next(node for node in workflow["nodes"] if node["name"] == "State - Report Markdown persisted")
    assert "report_markdown" in report_markdown_state["parameters"]["query"]
    assert "prompt_version" in report_markdown_state["parameters"]["query"]

    converter = next(node for node in workflow["nodes"] if node["name"] == "PDF Converter")
    assert converter["parameters"]["options"]["timeout"] == "={{ Number($env.PDF_CONVERTER_TIMEOUT_SECONDS || 300) * 1000 }}"
    assert converter["retryOnFail"] is False
    assert "maxTries" not in converter
    assert "waitBetweenTries" not in converter

    prepare_batches = next(node for node in workflow["nodes"] if node["name"] == "Prepare analysis batches")
    batch_code = prepare_batches["parameters"]["jsCode"]
    assert "6000" in batch_code
    assert "page_count" in batch_code
    assert "slice(0, 7000)" not in batch_code
    assert "pageNumbers" in batch_code
    assert "const batchSource = { ...source }" in batch_code
    assert "delete batchSource.markdown" in batch_code
    assert "...batchSource, batch_number:" in batch_code
    assert "...source, batch_number:" not in batch_code
    assert "sortedPages.length !== expectedPages" in batch_code

    merge_batches = next(node for node in workflow["nodes"] if node["name"] == "Merge batch findings and prepare report")
    merge_code = merge_batches["parameters"]["jsCode"]
    assert "pages.length !== expectedPages" in merge_code
    assert "JSON.parse(raw)" in merge_code
    assert "new Map()" in merge_code
    assert "prompt_version: 'regulatory-extraction-v5-full-document-batched'" in merge_code
    assert "impacto" in merge_code.lower()
    assert "prioridade executiva" in merge_code.lower()
    assert "sem tabelas Markdown" in merge_code

    ollama = next(node for node in workflow["nodes"] if node["name"] == "Ollama - Generate report Markdown")
    ollama_body = ollama["parameters"]["jsonBody"]
    assert "format: 'json'" not in ollama_body
    assert "report_prompt" in ollama_body
    assert "WORKFLOW_TIMEOUT_SECONDS" in ollama["parameters"]["options"]["timeout"]
    assert "* 1000" in ollama["parameters"]["options"]["timeout"]
    assert "num_ctx: 8192" in ollama_body
    assert "num_predict: 4096" in ollama_body

    batch_ollama = next(node for node in workflow["nodes"] if node["name"] == "Ollama - Analyze each batch")
    assert "format: 'json'" in batch_ollama["parameters"]["jsonBody"]
    assert "batch_prompt" in batch_ollama["parameters"]["jsonBody"]
    assert "WORKFLOW_TIMEOUT_SECONDS" in batch_ollama["parameters"]["options"]["timeout"]
    assert "num_ctx: 4096" in batch_ollama["parameters"]["jsonBody"]
    loop = next(node for node in workflow["nodes"] if node["name"] == "Loop Over Items")
    assert loop["type"] == "n8n-nodes-base.splitInBatches"
    assert loop["parameters"]["batchSize"] == 1
    assert workflow["connections"]["Prepare analysis batches"]["main"][0][0]["node"] == "Loop Over Items"
    assert workflow["connections"]["Loop Over Items"]["main"][0][0]["node"] == "Merge batch findings and prepare report"
    assert workflow["connections"]["Loop Over Items"]["main"][1][0]["node"] == "Ollama - Analyze each batch"
    assert workflow["connections"]["Ollama - Analyze each batch"]["main"][0][0]["node"] == "Loop Over Items"

    report_state = next(node for node in workflow["nodes"] if node["name"] == "State - Report persisted")
    assert "status = 'aguardando_envio'" in report_state["parameters"]["query"]
    assert "aguardando_revisao" not in report_state["parameters"]["query"]
    report_payload = next(node for node in workflow["nodes"] if node["name"] == "Prepare report PDF payload")
    assert "report_markdown" in report_payload["parameters"]["jsCode"]
    validate_evidence = next(node for node in workflow["nodes"] if node["name"] == "Gateway - Validate report evidence")
    assert "/validate-report" in validate_evidence["parameters"]["url"]
    assert "X-Internal-Token" in json.dumps(validate_evidence["parameters"])
    accept_evidence = next(node for node in workflow["nodes"] if node["name"] == "Accept evidence validation and add signal")
    assert "coverage.complete" in accept_evidence["parameters"]["jsCode"]
    assert "if (pending.length)" in accept_evidence["parameters"]["jsCode"]
    assert "references_pending" not in accept_evidence["parameters"]["jsCode"]
    assert workflow["connections"]["Validate report Markdown"]["main"][0][0]["node"] == "Gateway - Validate report evidence"
    report_file = next(node for node in workflow["nodes"] if node["name"] == "Prepare report PDF file")
    assert "getBinaryDataBuffer" in report_file["parameters"]["jsCode"]
    renderer = next(node for node in workflow["nodes"] if node["name"] == "Report Renderer")
    assert "/v1/render-markdown" in renderer["parameters"]["url"]
    assert "report_markdown" in json.dumps(workflow)
    assert "RAG - Search context" not in names


def test_market_prompt_file_matches_active_contract() -> None:
    prompt = (ROOT / "prompts" / "regulatory-extraction-v5.md").read_text(encoding="utf-8")
    assert "6.000 caracteres" in prompt
    assert "Todos os\nlotes são analisados" in prompt
    assert "duplicatas" in prompt
    assert "- Página: N" in prompt
    assert "- Evidência literal:" in prompt
    assert "marcados como pendentes" in prompt
    assert "listas com marcadores" in prompt
    assert "Não use tabelas" in prompt
    for marker in (
        "o que aconteceu",
        "qual é o status\nregulatório",
        "qual é a prioridade executiva",
        "trecho literal",
        "Referências de páginas",
    ):
        assert marker.lower() in prompt.lower()
    assert "JSON temporário" in prompt
    assert "RAG_CONTEXT" not in prompt


def test_internal_repository_schema_contract() -> None:
    schema = (ROOT / "deploy" / "postgres" / "init" / "002_internal_repository.sql").read_text(encoding="utf-8")
    for table in ("documents", "artifacts", "processing_attempts", "analysis_results", "human_reviews"):
        assert f"CREATE TABLE IF NOT EXISTS automacao_miller.{table}" in schema
    assert "ADD COLUMN IF NOT EXISTS submission_id" in schema
    assert "legacy_report_file_id" in schema
    assert "UNIQUE (submission_id, artifact_type, version)" in schema
    assert "report_markdown" in schema


def test_rag_and_training_schema_contract() -> None:
    schema = (ROOT / "deploy" / "postgres" / "init" / "004_rag_and_training.sql").read_text(encoding="utf-8")
    assert "CREATE EXTENSION IF NOT EXISTS vector" in schema
    for table in ("document_chunks", "rag_retrievals", "quality_checks", "training_examples", "model_evaluations"):
        assert f"CREATE TABLE IF NOT EXISTS automacao_miller.{table}" in schema
    assert "content_tsv" in schema
    assert "submission_id = %(submission_id)s" in (ROOT / "infra" / "rag" / "search.py").read_text(encoding="utf-8")


def test_reconciliation_routes_recovered_email_to_send_workflow() -> None:
    workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-reconcile-v1.json").read_text(encoding="utf-8"))
    query = next(node for node in workflow["nodes"] if node["name"] == "State - Find pending documents")["parameters"]["query"]
    dispatch = next(node for node in workflow["nodes"] if node["name"] == "Dispatch recovery task")
    send_workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-send-report-v1.json").read_text(encoding="utf-8"))
    send_webhook = next(node for node in send_workflow["nodes"] if node["name"] == "Panel - Request report send")

    assert query.startswith("WITH reset_deliveries AS")
    assert "RETURNING ed.delivery_id, ed.submission_id, ed.requested_at" in query
    assert "'email_delivery'::text AS recovery_type" in query
    assert "'document'::text AS recovery_type" in query
    assert "FROM reset_documents" in query
    assert "public.execution_entity" in query
    assert "ee.status IN ('new', 'running', 'waiting')" in query
    assert "pa.attempt_number = ( SELECT d.attempt_count" in query
    assert "$json.recovery_type === 'email_delivery'" in dispatch["parameters"]["url"]
    assert "automacao-regulatoria-send-report" in dispatch["parameters"]["url"]
    assert "automacao-regulatoria-internal'" in dispatch["parameters"]["url"]
    assert "delivery_id: Number($json.delivery_id)" in dispatch["parameters"]["jsonBody"]
    assert "submission_id: $json.submission_id" in dispatch["parameters"]["jsonBody"]
    assert send_webhook["parameters"]["path"] == "automacao-regulatoria-send-report"
    assert "delivery_id" in next(node for node in send_workflow["nodes"] if node["name"] == "State - Claim email delivery")["parameters"]["query"]


def test_manual_delivery_schema_and_workflow_contract() -> None:
    schema = (ROOT / "deploy" / "postgres" / "init" / "003_panel_operations.sql").read_text(encoding="utf-8")
    for table in ("report_recipients", "document_recipients", "email_deliveries"):
        assert f"CREATE TABLE IF NOT EXISTS automacao_miller.{table}" in schema
    assert "aguardando_envio" in schema
    workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-send-report-v1.json").read_text(encoding="utf-8"))
    names = {node["name"] for node in workflow["nodes"]}
    assert workflow["active"] is False
    assert {"Panel - Request report send", "State - Claim email delivery", "Gmail - Send report", "State - Report sent"} <= names
    assert "report_recipients" in (ROOT / "infra" / "upload_gateway" / "app.py").read_text(encoding="utf-8")


def test_reconciliation_and_internal_error_workflows_are_database_driven() -> None:
    reconcile = json.loads((ROOT / "workflows" / "automacao-regulatoria-reconcile-v1.json").read_text(encoding="utf-8"))
    error = json.loads((ROOT / "workflows" / "automacao-regulatoria-internal-error-v1.json").read_text(encoding="utf-8"))
    reconcile_query = next(node for node in reconcile["nodes"] if node["name"] == "State - Find pending documents")["parameters"]["query"]
    error_query = next(node for node in error["nodes"] if node["name"] == "Record internal error")["parameters"]["query"]
    assert "processing_attempts" in reconcile_query
    assert "status = 'recebido'" in reconcile_query
    assert "workflow_errors" in error_query
    assert "attempt_id" in error_query
    assert "googleDrive" not in json.dumps(reconcile)
    assert "googleDrive" not in json.dumps(error)
