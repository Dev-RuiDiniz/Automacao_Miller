import json
import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js é necessário para conferir a expressão n8n")
@pytest.mark.parametrize("configured,expected", [(None, 0), ("0", 0), ("5400", 5520000)])
def test_openrouter_http_deadline_is_disabled_with_zero(configured, expected):
    workflow = json.loads((Path(__file__).parents[2] / "workflows/automacao-regulatoria-internal-v1.json").read_text())
    node = next(node for node in workflow["nodes"] if node["name"] == "OpenRouter - Analyze and render V8")
    expression = node["parameters"]["options"]["timeout"]
    script = "const fs=require('fs'); const p=JSON.parse(fs.readFileSync(0,'utf8')); const value=new Function('$env','return ('+p.expression.slice(3,-2)+')')({OPENROUTER_TIMEOUT_SECONDS:p.configured}); process.stdout.write(JSON.stringify({value,truthy:!!value,numeric:Number(value)}));"
    result = subprocess.run(["node", "-e", script], input=json.dumps({"expression": expression, "configured": configured}),
                            text=True, capture_output=True, check=True)
    value = json.loads(result.stdout)
    assert value == {"value": expected, "truthy": bool(expected), "numeric": expected}
    assert node["typeVersion"] == 2
    assert node["parameters"]["options"]["fullResponse"] is True
    assert node["parameters"]["options"]["ignoreResponseCode"] is True
    assert "diagnostic_context" in node["parameters"]["bodyParametersJson"]
    assert "INTERNAL_API_TOKEN" in node["parameters"]["headerParametersJson"]
    assert workflow["active"] is False
