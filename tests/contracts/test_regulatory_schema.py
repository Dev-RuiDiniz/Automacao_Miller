import json
from pathlib import Path


SCHEMA_PATH = Path(__file__).parents[2] / "prompts" / "regulatory-extraction.schema.json"
V2_SCHEMA_PATH = Path(__file__).parents[2] / "prompts" / "regulatory-extraction-v2.schema.json"


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


def test_v2_schema_requires_preliminary_technical_opinion() -> None:
    schema = json.loads(V2_SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["title"] == "RegulatoryExtractionV2"
    assert "parecer_tecnico" in schema["required"]
    opinion = schema["$defs"]["parecer_tecnico"]
    assert "fundamentos" in opinion["required"]
    assert "apontamentos_tecnicos" in opinion["required"]
    assert "recomendacoes" in opinion["required"]
    assert schema["$defs"]["apontamento_tecnico"]["properties"]["prioridade"]["enum"] == [
        "critica",
        "alta",
        "media",
        "baixa",
        "informativa",
    ]
