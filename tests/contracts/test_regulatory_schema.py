import json
from pathlib import Path


SCHEMA_PATH = Path(__file__).parents[2] / "prompts" / "regulatory-extraction.schema.json"


def test_schema_requires_confidence_and_review_fields() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert "exigencias" in schema["required"]
    assert "pendencias" in schema["required"]
    assert "evidencias_insuficientes" in schema["required"]
    assert "contradicoes" in schema["required"]
    assert "controle_confianca" in schema["required"]
    assert schema["properties"]["controle_confianca"]["properties"]["status"]["enum"] == [
        "aceitavel",
        "baixa_confianca",
        "inconclusivo",
    ]
