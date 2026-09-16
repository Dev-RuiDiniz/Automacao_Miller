import json
from pathlib import Path


ROOT = Path(__file__).parents[2]


def test_compose_declares_isolated_required_services() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    for service in ("postgres:", "ollama:", "rag-service:", "pdf-converter:", "report-renderer:", "n8n:"):
        assert service in compose
    assert "pgvector/pgvector:pg15" in compose
    assert "RAG_SERVICE_BASE_URL" in compose
    assert "RAG_ENABLE_SEMANTIC_SEARCH" in compose
    assert "127.0.0.1:${N8N_HOST_PORT:-25678}:5678" in compose
    assert "automacao_miller_n8n_data" in compose
    assert "automacao_miller_artifacts_data:/data/artifacts" in compose
    assert "ARTIFACT_STORAGE_DIR" in compose
    assert "N8N_RESTRICT_FILE_ACCESS_TO" in compose
    assert "automacao_miller_submission_data:" in compose
    assert '"${ARTIFACTS_GID:-10002}"' in compose
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


def test_internal_workflow_uses_simple_markdown_report_path() -> None:
    workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-internal-v1.json").read_text(encoding="utf-8"))
    names = {node["name"] for node in workflow["nodes"]}
    node_types = {node["type"] for node in workflow["nodes"]}

    assert workflow["id"] == "automacao-regulatoria-internal"
    assert workflow["active"] is False
    assert workflow["settings"]["errorWorkflow"] == "automacao-reg-error-handler"
    assert {
        "Landing - Receber documento",
        "State - Claim document",
        "State - Start attempt",
        "Internal Storage - Read PDF",
        "PDF Converter",
        "Validate Markdown",
        "Internal Storage - Write Markdown",
        "Prepare expert prompt",
        "Ollama - Generate report Markdown",
        "Validate report Markdown",
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

    prepare_expert = next(node for node in workflow["nodes"] if node["name"] == "Prepare expert prompt")
    expert_code = prepare_expert["parameters"]["jsCode"]
    assert "analista" in expert_code
    assert "relat" in expert_code
    assert "prompt_version: 'regulatory-extraction-v3'" in expert_code
    assert "page_count" in expert_code

    ollama = next(node for node in workflow["nodes"] if node["name"] == "Ollama - Generate report Markdown")
    ollama_body = ollama["parameters"]["jsonBody"]
    assert "format: 'json'" not in ollama_body
    assert "expert_prompt" in ollama_body
    assert "WORKFLOW_TIMEOUT_SECONDS" in ollama["parameters"]["options"]["timeout"]
    assert "* 1000" in ollama["parameters"]["options"]["timeout"]
    assert "num_ctx: 8192" in ollama_body
    assert "num_predict: 2048" in ollama_body

    report_state = next(node for node in workflow["nodes"] if node["name"] == "State - Report persisted")
    assert "status = 'aguardando_envio'" in report_state["parameters"]["query"]
    assert "aguardando_revisao" not in report_state["parameters"]["query"]
    report_payload = next(node for node in workflow["nodes"] if node["name"] == "Prepare report PDF payload")
    assert "report_markdown" in report_payload["parameters"]["jsCode"]
    report_file = next(node for node in workflow["nodes"] if node["name"] == "Prepare report PDF file")
    assert "getBinaryDataBuffer" in report_file["parameters"]["jsCode"]
    renderer = next(node for node in workflow["nodes"] if node["name"] == "Report Renderer")
    assert "/v1/render-markdown" in renderer["parameters"]["url"]
    assert "report_markdown" in json.dumps(workflow)
    assert "RAG - Search context" not in names


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


def test_reconciliation_returns_protocols_for_dispatch() -> None:
    workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-reconcile-v1.json").read_text(encoding="utf-8"))
    query = next(node for node in workflow["nodes"] if node["name"] == "State - Find pending documents")["parameters"]["query"]
    dispatch = next(node for node in workflow["nodes"] if node["name"] == "Dispatch pending document")
    assert query.startswith("WITH reset_deliveries AS")
    assert "SELECT submission_id FROM reset" in query
    assert "public.execution_entity" in query
    assert "ee.status IN ('new', 'running', 'waiting')" in query
    assert "pa.attempt_number = (SELECT d.attempt_count" in query
    assert "submission_id: $json.submission_id" in dispatch["parameters"]["jsonBody"]


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
