import json
from pathlib import Path


ROOT = Path(__file__).parents[2]


def test_compose_declares_isolated_required_services() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    for service in ("postgres:", "ollama:", "pdf-converter:", "report-renderer:", "n8n:"):
        assert service in compose
    assert "127.0.0.1:${N8N_HOST_PORT:-25678}:5678" in compose
    assert "automacao_miller_n8n_data" in compose
    assert "automacao_miller_artifacts_data:/data/artifacts" in compose
    assert "ARTIFACT_STORAGE_DIR" in compose
    assert "N8N_RESTRICT_FILE_ACCESS_TO" in compose
    assert "automacao_miller_submission_data:" in compose


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


def test_internal_workflow_is_landing_only_and_uses_private_repository() -> None:
    workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-internal-v1.json").read_text(encoding="utf-8"))
    names = {node["name"] for node in workflow["nodes"]}
    node_types = {node["type"] for node in workflow["nodes"]}

    assert workflow["id"] == "automacao-regulatoria-internal"
    assert workflow["active"] is False
    assert workflow["settings"]["errorWorkflow"] == "automacao-reg-error-handler"
    assert {"Landing - Receber documento", "State - Claim document", "State - Start attempt", "Internal Storage - Read PDF", "Internal Storage - Write Markdown", "Internal Storage - Write analysis", "Internal Storage - Write report", "State - Human review", "Post-report confidence gate", "State - Awaiting manual send"} <= names
    read_pdf = next(node for node in workflow["nodes"] if node["name"] == "Internal Storage - Read PDF")
    assert "$('Claim guard').item.json.source_storage_key" in read_pdf["parameters"]["filePath"]
    claim_guard = next(node for node in workflow["nodes"] if node["name"] == "Claim guard")
    assert "item.json?.submission_id" in claim_guard["parameters"]["jsCode"]
    assert "Gmail - Send report" not in names
    assert "n8n-nodes-base.googleDrive" not in node_types
    assert "automacao_miller.documents" in next(node for node in workflow["nodes"] if node["name"] == "State - Claim document")["parameters"]["query"]
    assert "/data/artifacts/" in " ".join(json.dumps(node["parameters"]) for node in workflow["nodes"])
    markdown_state = next(node for node in workflow["nodes"] if node["name"] == "State - Markdown persisted")
    assert "Internal Storage - Prepare keys" in markdown_state["parameters"]["query"]
    report_file = next(node for node in workflow["nodes"] if node["name"] == "Prepare report file")
    assert "getBinaryDataBuffer" in report_file["parameters"]["jsCode"]
    report_state = next(node for node in workflow["nodes"] if node["name"] == "State - Report persisted")
    assert "$json.report_size_bytes" in report_state["parameters"]["query"]
    analysis_state = next(node for node in workflow["nodes"] if node["name"] == "State - Analysis persisted")
    assert "Prepare analysis file" in analysis_state["parameters"]["query"]


def test_internal_repository_schema_contract() -> None:
    schema = (ROOT / "deploy" / "postgres" / "init" / "002_internal_repository.sql").read_text(encoding="utf-8")
    for table in ("documents", "artifacts", "processing_attempts", "analysis_results", "human_reviews"):
        assert f"CREATE TABLE IF NOT EXISTS automacao_miller.{table}" in schema
    assert "ADD COLUMN IF NOT EXISTS submission_id" in schema
    assert "legacy_report_file_id" in schema
    assert "UNIQUE (submission_id, artifact_type, version)" in schema


def test_reconciliation_returns_protocols_for_dispatch() -> None:
    workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-reconcile-v1.json").read_text(encoding="utf-8"))
    query = next(node for node in workflow["nodes"] if node["name"] == "State - Find pending documents")["parameters"]["query"]
    dispatch = next(node for node in workflow["nodes"] if node["name"] == "Dispatch pending document")

    assert query.startswith("WITH reset_deliveries AS")
    assert "SELECT submission_id FROM reset" in query
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
