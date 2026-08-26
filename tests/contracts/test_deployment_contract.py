import json
from pathlib import Path


ROOT = Path(__file__).parents[2]


def test_compose_declares_isolated_required_services() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    for service in ("postgres:", "ollama:", "pdf-converter:", "report-renderer:", "n8n:"):
        assert service in compose
    assert "127.0.0.1:${N8N_HOST_PORT:-25678}:5678" in compose
    assert "automacao_miller_n8n_data" in compose


def test_workflow_export_is_valid_and_contains_required_stages() -> None:
    workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-v1.json").read_text(encoding="utf-8"))
    names = {node["name"] for node in workflow["nodes"]}

    assert {"Google Drive - Search input PDFs", "PDF Converter", "Ollama - Extract", "Report Renderer", "Gmail - Send report"} <= names
    assert workflow["active"] is False


def test_error_workflow_export_records_failures() -> None:
    workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-error-v1.json").read_text(encoding="utf-8"))
    names = {node["name"] for node in workflow["nodes"]}

    assert {"Error Trigger", "Normalize error context", "Record workflow error"} <= names
