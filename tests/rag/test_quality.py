from infra.regulatory_analysis.quality import validate_analysis


def analysis(**changes):
    value = {"documento": {"submission_id": "doc-1"}, "medicamentos_deferidos": [], "medicamentos_indeferidos": [], "suplementos_deferidos": [], "suplementos_indeferidos": [], "estudos_clinicos_deferidos": [], "estudos_clinicos_indeferidos": [], "outros_atos": [], "exigencias": [], "pendencias": [], "categorias_nao_localizadas": [], "evidencias_insuficientes": [], "contradicoes": [], "avisos": [], "controle_confianca": {"status": "aceitavel", "motivos": []}, "revisao_humana": {"necessaria": False, "motivos": []}}
    value.update(changes)
    return value


def test_valid_finding_requires_real_page_and_excerpt() -> None:
    result = validate_analysis(analysis(outros_atos=[{"status": "outro", "paginas_origem": [71], "evidencia": "Alcovit deferido"}]), "## Página 71\nAlcovit deferido.", "doc-1")
    assert result.status == "aprovado"
    assert result.citation_coverage == 1


def test_page_and_excerpt_from_another_document_are_rejected_as_warning() -> None:
    result = validate_analysis(analysis(outros_atos=[{"paginas_origem": [79], "evidencia": "não consta"}]), "## Página 71\nAlcovit deferido.", "doc-1")
    assert result.status == "aviso"
    assert "page_not_found" in {item["code"] for item in result.violations}
    assert result.needs_review


def test_invalid_status_cancelled_and_device_classification_are_detected() -> None:
    result = validate_analysis(analysis(medicamentos_indeferidos=[{"status": "cancelado", "tipo_produto_relacionado": "dispositivo", "paginas_origem": [71], "evidencia": "Alcovit"}]), "## Página 71\nAlcovit", "doc-1")
    codes = {item["code"] for item in result.violations}
    assert "cancelled_misclassified" in codes
    assert "device_in_product_category" in codes


def test_extra_json_field_is_rejected_and_empty_analysis_has_full_coverage() -> None:
    result = validate_analysis(analysis(campo_extra="não permitido"), "## Página 1\nTexto", "doc-1")
    assert "unexpected_field" in {item["code"] for item in result.violations}
    assert validate_analysis(analysis(), "## Página 1\nTexto", "doc-1").citation_coverage == 1
