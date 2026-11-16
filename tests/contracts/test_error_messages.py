import json
import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js é necessário para validar as expressões do n8n.")
@pytest.mark.parametrize("error,stage,category,message_parts", [
    ({"message": "ANV8D-" + "a" * 32 + ". [line 4]", "description": "Estrutura do bloco inválida; motivo: justificativa_ausente. Diagnóstico"},
     "OpenRouter - Prepare verification bundle", "validação", ["justificativa_ausente", "ANV8D-"]),
    ({"message": "Falha", "description": "VALIDAÇÃO: campo obrigatório ausente."},
     "OpenRouter - Analyze and render V8", "validação", ["Falha", "campo obrigatório"]),
    ({"message": "IA: OpenRouter retornou HTTP 402."}, "OpenRouter - Prepare verification bundle", "ia", ["HTTP 402"]),
    ({"message": "ARMAZENAMENTO: falha ao preservar diagnóstico."}, "OpenRouter - Analyze and render V8", "infraestrutura", ["ARMAZENAMENTO"]),
    ({"message": "EXTRAÇÃO: página ilegível."}, "PDF Converter", "extração", ["página ilegível"]),
    ({"message": "Falha na referência: arquivo ausente."}, "Internal Storage", "infraestrutura", ["referência"]),
    ({"message": "Mensagem igual", "description": "Mensagem igual"}, "Outro nó", "infraestrutura", ["Mensagem igual"]),
    ({"description": "Descrição sem mensagem."}, "Outro nó", "infraestrutura", ["Descrição sem mensagem"]),
    ({}, "Outro nó", "infraestrutura", ["falha não detalhada"]),
])
def test_error_export_preserves_description_and_classifies_split_message(error, stage, category, message_parts):
    workflow = json.loads((Path(__file__).parents[2] / "workflows/automacao-regulatoria-internal-error-v1.json").read_text())
    assignments = next(n for n in workflow["nodes"] if n["name"] == "Normalize internal error")["parameters"]["assignments"]["assignments"]
    expressions = {a["name"]: a["value"][3:-2].strip() for a in assignments if a["name"] in {"error_message", "error_category"}}
    harness = """let raw=''; process.stdin.on('data',chunk=>raw+=chunk); process.stdin.on('end',()=>{
      const input=JSON.parse(raw), output={};
      for(const [key,expr] of Object.entries(input.expressions)) output[key]=new Function('$json','return ('+expr+');')(input.data);
      process.stdout.write(JSON.stringify(output));
    });"""
    completed = subprocess.run(["node", "-e", harness], input=json.dumps({"expressions": expressions,
        "data": {"execution": {"error": error, "lastNodeExecuted": stage}}}), text=True, capture_output=True, check=True)
    result = json.loads(completed.stdout)
    assert result["error_category"] == category
    assert all(part in result["error_message"] for part in message_parts)
    if error.get("message") == error.get("description") and error:
        assert result["error_message"] == error["message"]
