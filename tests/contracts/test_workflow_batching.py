import json
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[2]


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js é necessário para testar o código do nó n8n")
def test_workflow_batches_every_page_and_splits_long_pages() -> None:
    workflow = json.loads((ROOT / "workflows" / "automacao-regulatoria-internal-v1.json").read_text(encoding="utf-8"))
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
    harness = r"""
const fs = require('fs');
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const lookup = () => ({ item: { json: payload.source } });
const result = new Function('$', payload.code)(lookup);
process.stdout.write(JSON.stringify(result.map(item => ({
  pages: item.json.batch_pages,
  markdown: item.json.batch_markdown
}))));
"""

    completed = subprocess.run(
        ["node", "-e", harness],
        input=json.dumps({"code": code, "source": source}),
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
    page_two = [batch["markdown"] for batch in batches if "## Página 2" in batch["markdown"]]
    assert len(page_two) > 1
    assert sum(text.count("X") for text in page_two) == 12500
