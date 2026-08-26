from infra.regulatory_analysis.confidence import classify_confidence


def test_accepts_complete_analysis_without_warnings() -> None:
    result = classify_confidence(
        {
            "medicamentos_deferidos": [
                {"produto": "Produto A", "paginas_origem": [71]}
            ],
            "evidencias_insuficientes": [],
            "contradicoes": [],
            "revisao_humana": {"necessaria": False, "motivos": []},
        },
        [],
    )

    assert result == {"status": "aceitavel", "motivos": []}


def test_routes_missing_evidence_to_low_confidence() -> None:
    result = classify_confidence(
        {
            "medicamentos_deferidos": [{"produto": "Produto A"}],
            "evidencias_insuficientes": ["medicamentos_deferidos"],
            "contradicoes": [],
            "revisao_humana": {"necessaria": False, "motivos": []},
        },
        ["Pagina 71: aviso de layout"],
    )

    assert result["status"] == "baixa_confianca"
    assert "evidencia insuficiente" in result["motivos"]


def test_routes_contradiction_to_inconclusive_review() -> None:
    result = classify_confidence(
        {
            "medicamentos_deferidos": [],
            "evidencias_insuficientes": [],
            "contradicoes": ["status divergente nas paginas 1 e 2"],
            "revisao_humana": {"necessaria": True, "motivos": ["contradicao"]},
        },
        [],
    )

    assert result["status"] == "inconclusivo"
    assert "contradicao" in result["motivos"]
