import json
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[2]


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js é necessário para testar o código do nó n8n")
def test_workflow_batches_every_page_and_splits_long_pages() -> None:
    workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-internal-v2-hybrid.json").read_text(encoding="utf-8"))
    code = next(node["parameters"]["jsCode"] for node in workflow["nodes"] if node["name"] == "Prepare analysis batches")
    source = {
        "submission_id": "local-test",
        "metadata": {"page_count": 3},
        "markdown": (
            "## Página 1\n"
            + ("contexto sem ato. " * 430)
            + " EVIDENCIA_APOS_7000\n## Página 2\n\nATO_LONGO "
            + ("X" * 12500)
            + "\n## Página 3\nPágina final."
        ),
    }
    deterministic = {
        "page_count": 3,
        "pages_processed": [1, 2, 3],
        "observations": [
            {"page": 2, "category": "termo_regulatorio_literal", "value": "cancelado", "evidence": "ATO_LONGO cancelado."},
        ],
    }
    harness = r"""
const fs = require('fs');
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const lookup = (name) => ({ item: { json: name === 'Gateway - Build deterministic context' ? payload.deterministic : payload.source } });
const result = new Function('$', payload.code)(lookup);
process.stdout.write(JSON.stringify(result.map(item => ({
  pages: item.json.batch_pages,
  markdown: item.json.batch_markdown,
  prompt: item.json.batch_prompt
}))));
"""

    completed = subprocess.run(
        ["node", "-e", harness],
        input=json.dumps({"code": code, "source": source, "deterministic": deterministic}),
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
        cwd=ROOT,
    )
    batches = json.loads(completed.stdout)

    assert len(batches) > 3
    assert all(len(batch["markdown"]) <= 6000 for batch in batches)
    assert {page for batch in batches for page in batch["pages"]} == {1, 2, 3}
    assert any("EVIDENCIA_APOS_7000" in batch["markdown"] for batch in batches)
    assert any('"value":"cancelado"' in batch["prompt"] for batch in batches if 2 in batch["pages"])
    page_two = [batch["markdown"] for batch in batches if "## Página 2" in batch["markdown"]]
    assert len(page_two) > 1
    assert sum(text.count("X") for text in page_two) == 12500


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js é necessário para testar o código do nó n8n")
def test_workflow_adds_cross_page_context_and_literal_terms_to_report() -> None:
    workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-internal-v1.json").read_text(encoding="utf-8"))
    nodes = {node["name"]: node for node in workflow["nodes"]}
    assert "Gateway - Build deterministic context" in nodes
    assert workflow["connections"]["State - Markdown persisted"]["main"][0][0]["node"] == "Gateway - Build deterministic context"
    assert workflow["connections"]["Gateway - Build deterministic context"]["main"][0][0]["node"] == "Prepare analysis batches"
    assert nodes["Gateway - Build deterministic context"]["parameters"]["url"].endswith("/deterministic-context' }}")

    identifier = "25351.123456/2024-78"
    context = {
        "anchor_count": 2,
        "anchors": [
            {"page": 1, "kind": "identificador_processo", "term": identifier, "evidence": f"Processo {identifier}: deferido."},
            {"page": 1, "kind": "termo_literal", "term": "deferido", "evidence": f"Processo {identifier}: deferido."},
        ],
        "cross_page_links": [{
            "identifier": identifier,
            "pages": [1, 2],
            "occurrences": [
                {"page": 1, "evidence": f"Processo {identifier}: deferido."},
                {"page": 2, "evidence": f"Processo {identifier}: cancelado."},
            ],
        }],
    }
    batch = {"json": {"batch_number": 1, "batch_pages": [1, 2], "metadata": {"page_count": 2}, "submission_id": "sintetico"}}
    finding = {"titulo": "Ato regulatório", "fato": "O processo foi citado.", "status": "deferido", "pagina": 1, "evidencia": f"Processo {identifier}: deferido."}
    payload = {
        "code": nodes["Merge batch findings and prepare report"]["parameters"]["jsCode"],
        "response": [{"json": {"response": json.dumps({"achados": [finding]}, ensure_ascii=False)}}],
        "batch": batch,
        "context": context,
    }
    merge_harness = r"""
const fs = require('fs');
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const lookup = (name) => name === 'Prepare analysis batches'
  ? { all: () => [payload.batch] }
  : { item: { json: payload.context } };
const input = { all: () => payload.response };
const result = new Function('$input', '$', payload.code)(input, lookup);
process.stdout.write(JSON.stringify(result[0].json));
"""
    merged = subprocess.run(
        ["node", "-e", merge_harness],
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
        cwd=ROOT,
    )
    merged_json = json.loads(merged.stdout)
    assert merged_json["structured_findings"][0]["contexto_entre_paginas"][0]["occurrences"][1]["page"] == 2
    assert merged_json["report_context"]["cross_page_link_count"] == 1

    report = "\n\n".join([
        "# Relatório Técnico de Inteligência Regulatória",
        "## 1. Resumo executivo", "Conclusão de apoio documental. " * 12,
        "## 2. Respostas às perguntas de negócio", "Resposta. " * 12,
        "## 3. Escopo e identificação do documento", "Escopo. " * 12,
        "## 4. Achados regulatórios", "Achados. " * 12,
        "## 5. Impacto de mercado e comercial", "Impacto. " * 12,
        "## 6. Plano de ação recomendado", "Ação. " * 12,
        "## 7. Riscos, contradições e pontos de atenção", "Risco. " * 12,
        "## 8. Limitações e informações não comprovadas", "Limite. " * 12,
        "## 9. Referências de páginas", f"- Página: 1\n- Evidência literal: \"Processo {identifier}: deferido.\"",
    ])
    validator_payload = {
        "code": nodes["Validate report Markdown"]["parameters"]["jsCode"],
        "report": report,
        "source": merged_json,
    }
    validator_harness = r"""
const fs = require('fs');
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const lookup = () => ({ item: { json: payload.source } });
const result = new Function('$json', '$', payload.code)({ response: payload.report }, lookup);
process.stdout.write(JSON.stringify(result[0].json.report_markdown));
"""
    validated = subprocess.run(
        ["node", "-e", validator_harness],
        input=json.dumps(validator_payload, ensure_ascii=False),
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
        cwd=ROOT,
    )
    report_markdown = json.loads(validated.stdout)
    assert "Menções literais localizadas por regras" in report_markdown
    assert "Identificadores de processo repetidos em páginas diferentes" in report_markdown
    assert f"- Página: 2\n- Evidência literal: \"Processo {identifier}: cancelado.\"" in report_markdown


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js é necessário para testar o código do nó n8n")
def test_hybrid_workflow_only_synthesizes_python_validated_candidates() -> None:
    workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-internal-v2-hybrid.json").read_text(encoding="utf-8"))
    nodes = {node["name"]: node for node in workflow["nodes"]}
    assert workflow["active"] is False
    assert workflow["connections"]["Merge batch findings and prepare report"]["main"][0][0]["node"] == "Gateway - Validate AI audit candidates"
    assert workflow["connections"]["Gateway - Validate AI audit candidates"]["main"][0][0]["node"] == "Prepare validated report prompt"
    assert workflow["connections"]["Prepare validated report prompt"]["main"][0][0]["node"] == "Ollama - Generate report Markdown"
    assert "/validate-ai-audit' }}" in nodes["Gateway - Validate AI audit candidates"]["parameters"]["url"]

    merged = {
        "submission_id": "fixture-sintetico",
        "report_context": {"page_count": 2, "batch_count": 1, "type": "python_deterministic_then_ai_gap_audit"},
        "deterministic_context": {"observations": [], "cross_page_links": []},
    }
    validation = {
        "validated_candidates": [{
            "titulo": "Prazo indicado",
            "fato": "O documento informa prazo de 30 dias.",
            "categoria": "prazo",
            "pagina": 1,
            "evidencia": "O prazo é de 30 dias.",
        }],
        "pending_candidates": [{
            "fato": "AFIRMACAO_INVENTADA_NAO_DEVE_IR_A_SINTESE",
            "pagina": 9,
            "evidencia": "trecho inexistente",
        }],
    }
    harness = r"""
const fs = require('fs');
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const lookup = (name) => ({ item: { json: name === 'Merge batch findings and prepare report' ? payload.merged : payload.validation } });
const result = new Function('$', '$json', payload.code)(lookup, payload.validation);
process.stdout.write(JSON.stringify(result[0].json));
"""
    completed = subprocess.run(
        ["node", "-e", harness],
        input=json.dumps({"code": nodes["Prepare validated report prompt"]["parameters"]["jsCode"], "merged": merged, "validation": validation}, ensure_ascii=False),
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
        cwd=ROOT,
    )
    result = json.loads(completed.stdout)
    assert result["structured_findings"] == validation["validated_candidates"]
    assert "O documento informa prazo de 30 dias." in result["report_prompt"]
    assert "AFIRMACAO_INVENTADA_NAO_DEVE_IR_A_SINTESE" not in result["report_prompt"]
