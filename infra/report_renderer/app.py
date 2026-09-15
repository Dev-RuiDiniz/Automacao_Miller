from __future__ import annotations

import io
import json
from html import escape
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


REPORT_VERSION = "1.3.0"
BRAND_NAVY = "#123B5D"
BRAND_TEAL = "#0F766E"
BRAND_GOLD = "#B7791F"
INK = "#1F2937"
MUTED = "#64748B"
LINE = "#D7E1EA"
SURFACE = "#F5F8FB"
SURFACE_BLUE = "#EAF2F8"
SURFACE_TEAL = "#E8F5F2"
SURFACE_GOLD = "#FFF7E6"
SECTIONS: tuple[tuple[str, str], ...] = (
    ("medicamentos_deferidos", "Medicamentos aprovados ou deferidos"),
    ("medicamentos_indeferidos", "Medicamentos indeferidos"),
    ("suplementos_deferidos", "Suplementos aprovados ou deferidos"),
    ("suplementos_indeferidos", "Suplementos indeferidos"),
    ("estudos_clinicos_deferidos", "Ensaios clínicos aprovados ou deferidos"),
    ("estudos_clinicos_indeferidos", "Ensaios clínicos indeferidos"),
    ("outros_atos", "Outros atos regulatórios"),
    ("exigencias", "Exigências e alterações que merecem conferência"),
    ("pendencias", "Pendências para acompanhamento"),
    ("categorias_nao_localizadas", "Categorias sem ocorrência localizada"),
    ("evidencias_insuficientes", "Evidências insuficientes"),
    ("contradicoes", "Contradições identificadas"),
    ("avisos", "Avisos de leitura e contexto"),
)

FINDING_KEYS = tuple(key for key, _ in SECTIONS[:9])
FIELD_LABELS = {
    "id": "ID",
    "empresa": "Empresa",
    "cnpj": "CNPJ",
    "produto": "Produto",
    "marca": "Marca",
    "tipo": "Tipo",
    "numero": "Número",
    "data": "Data",
    "assunto": "Assunto",
    "processo": "Processo",
    "registro": "Registro",
    "status": "Status",
    "prazo": "Prazo",
    "categoria": "Categoria",
    "descricao": "Descrição",
    "observacao": "Observação",
    "evidencia": "Evidência literal",
    "fato_documentado": "Fato documentado",
    "interpretacao_tecnica": "Interpretação técnica",
    "classificacao": "Classificação",
    "titulo": "Título",
    "constatacao": "Constatação",
    "impacto": "Impacto",
    "prioridade": "Prioridade",
    "acao_recomendada": "Ação recomendada",
    "responsavel_sugerido": "Responsável sugerido",
    "prazo_referencia": "Prazo de referência",
    "acao": "Ação",
    "justificativa": "Justificativa",
    "dependencia": "Dependência",
    "base_ids": "Base documental",
}
FIELD_ORDER = tuple(FIELD_LABELS)

TECHNICAL_LABELS = {
    "conforme_indicado": "Conforme indicado no documento",
    "nao_conforme_indicada": "Não conformidade potencial indicada",
    "misto": "Cenário misto",
    "inconclusivo": "Inconclusivo",
    "sem_ocorrencia": "Sem ocorrência localizada no recorte",
}
RISK_LABELS = {
    "baixo": "Baixo",
    "medio": "Médio",
    "alto": "Alto",
    "critico": "Crítico",
    "nao_classificado": "Não classificado",
}

app = FastAPI(
    title="Regulatory Report Renderer",
    version=REPORT_VERSION,
    description="Servico local para gerar relatorios PDF auditaveis.",
)


def _value_text(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _list_text(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(_value_text(item) for item in value) or "Não informado"
    return _value_text(value)


def _paragraph(text: Any, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(_value_text(text)).replace("\n", "<br/>") or "-", style)


def _rich_line(label: str, value: Any) -> str:
    return f"<b>{escape(label)}:</b> {escape(_value_text(value))}"


def _section_heading(title: str, styles: dict[str, ParagraphStyle]) -> Table:
    table = Table(
        [["", _paragraph(title, styles["section_title"])]],
        colWidths=(3.5 * mm, 166.5 * mm),
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), colors.HexColor(BRAND_TEAL)),
                ("BACKGROUND", (1, 0), (1, 0), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(LINE)),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def _notice_box(label: str, text: str, styles: dict[str, ParagraphStyle], background: str = SURFACE_GOLD) -> Table:
    table = Table(
        [[_paragraph(label, styles["notice_label"]), _paragraph(text, styles["notice_body"])]],
        colWidths=(36 * mm, 134 * mm),
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(background)),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor(BRAND_GOLD)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def _metadata_table(metadata: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    rows = [[_paragraph("Campo", styles["table_header"]), _paragraph("Valor", styles["table_header"])]]
    labels = {
        "source_filename": "Documento de origem",
        "submission_id": "Protocolo",
        "source_sha256": "Integridade SHA-256",
        "page_count": "Páginas do documento",
        "converter_version": "Versão do conversor",
    }
    for key in ("source_filename", "submission_id", "source_sha256", "page_count", "converter_version"):
        if key in metadata:
            rows.append([_paragraph(labels[key], styles["table_cell"]), _paragraph(metadata[key], styles["table_cell"])])
    table = Table(rows, colWidths=(55 * mm, 115 * mm), repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(BRAND_NAVY)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor(LINE)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor(SURFACE)),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _item_lines(item: Any) -> list[str]:
    if isinstance(item, dict):
        ordered_keys = [key for key in FIELD_ORDER if key in item] + [key for key in item if key not in FIELD_ORDER]
        lines = []
        for key in ordered_keys:
            value = item[key]
            if value in (None, "", [], {}):
                continue
            label = FIELD_LABELS.get(key, key.replace("_", " ").capitalize())
            if key in {"paginas_origem", "paginas", "evidencias"}:
                continue
            lines.append(f"{label}: {_value_text(value)}")
        pages = item.get("paginas_origem") or item.get("paginas")
        lines.append(f"Páginas de origem: {_pages_text(pages) if pages else 'não informadas - conferir no PDF original'}")
        if item.get("evidencias"):
            lines.append(f"Trecho de apoio: {_value_text(item['evidencias'])}")
        return lines or [_value_text(item)]
    return [_value_text(item), "Páginas de origem: não informadas - conferir no PDF original"]


def _pages_text(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(f"p. {page}" for page in value)
    return f"p. {value}"


def _items_for(analysis: dict[str, Any], key: str) -> list[Any]:
    values = analysis.get(key) or []
    if isinstance(values, list):
        return values
    return [values]


def _finding_count(analysis: dict[str, Any]) -> int:
    return sum(len(_items_for(analysis, key)) for key in FINDING_KEYS)


def _attention_count(analysis: dict[str, Any]) -> int:
    return sum(len(_items_for(analysis, key)) for key in ("evidencias_insuficientes", "contradicoes", "avisos"))


def _confidence_label(status: Any) -> str:
    return {
        "aceitavel": "Leitura preliminar sem alerta automático",
        "baixa_confianca": "Leitura preliminar com revisão humana",
        "inconclusivo": "Leitura preliminar inconclusiva",
    }.get(str(status), "Classificação de confiança não informada")


def _summary_table(analysis: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    confidence = analysis.get("controle_confianca") or {}
    review = analysis.get("revisao_humana") or {}
    cells = [
        ("Achados estruturados", str(_finding_count(analysis))),
        ("Pontos de atenção", str(_attention_count(analysis))),
        ("Confiança", _confidence_label(confidence.get("status"))),
        ("Revisão humana", "Necessária" if review.get("necessaria") else "Não sinalizada"),
    ]
    table = Table(
        [
            [_paragraph(label, styles["metric_label"]) for label, _ in cells],
            [_paragraph(value, styles["metric_value"]) for _, value in cells],
        ],
        colWidths=(43 * mm, 43 * mm, 43 * mm, 43 * mm),
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(SURFACE_BLUE)),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor(SURFACE)),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(LINE)),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor(LINE)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def _record_title(value: Any, index: int) -> str:
    if isinstance(value, dict):
        title = value.get("titulo") or value.get("produto") or value.get("assunto") or value.get("categoria") or value.get("id")
        if title:
            return f"{index:02d}  {_value_text(title)}"
    return f"{index:02d}  Registro documental"


def _record_card(value: Any, index: int, styles: dict[str, ParagraphStyle], *, accent: str = BRAND_TEAL) -> Table:
    if isinstance(value, dict):
        fields = []
        for key in FIELD_ORDER:
            item_value = value.get(key)
            if key in {"id", "paginas_origem", "paginas", "evidencias", "evidencia", "base_ids"} or item_value in (None, "", [], {}):
                continue
            fields.append(_rich_line(FIELD_LABELS.get(key, key.replace("_", " ").capitalize()), item_value))
        pages = value.get("paginas_origem") or value.get("paginas")
        fields.append(_rich_line("Páginas de origem", _pages_text(pages) if pages else "não informadas - conferir no PDF original"))
        if value.get("evidencia"):
            fields.append(_rich_line("Evidência literal", value["evidencia"]))
        if value.get("evidencias"):
            fields.append(_rich_line("Trecho de apoio", value["evidencias"]))
        if value.get("base_ids"):
            fields.append(_rich_line("Base documental", _list_text(value["base_ids"])))
    else:
        fields = [escape(_value_text(value)), _rich_line("Páginas de origem", "não informadas - conferir no PDF original")]
    body = Paragraph("<br/>".join(fields) or "-", styles["record"])
    table = Table(
        [[_paragraph(_record_title(value, index), styles["record_title"])], [body]],
        colWidths=(170 * mm,),
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), colors.HexColor(accent)),
                ("TEXTCOLOR", (0, 0), (0, 0), colors.white),
                ("BACKGROUND", (0, 1), (0, 1), colors.HexColor(SURFACE)),
                ("BOX", (0, 0), (-1, -1), 0.55, colors.HexColor(LINE)),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor(accent)),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table


def _executive_summary(metadata: dict[str, Any], analysis: dict[str, Any]) -> list[str]:
    page_count = metadata.get("page_count", "não informado")
    finding_count = _finding_count(analysis)
    confidence = analysis.get("controle_confianca") or {}
    review = analysis.get("revisao_humana") or {}
    if finding_count:
        opening = (
            f"A leitura do documento de {page_count} páginas localizou {finding_count} "
            "achados estruturados no recorte analisado. Eles estão organizados abaixo "
            "para facilitar a conferência e o acompanhamento da operação."
        )
    else:
        opening = (
            f"A leitura do documento de {page_count} páginas não localizou achados "
            "estruturados no recorte analisado. A ausência de registro não substitui "
            "a conferência do PDF e do Markdown de origem."
        )
    status_text = _confidence_label(confidence.get("status"))
    if review.get("necessaria") or confidence.get("status") in {"baixa_confianca", "inconclusivo"}:
        decision = (
            f"A classificação atual é: {status_text}. Antes de compartilhar este "
            "resultado ou tomar uma decisão comercial, confira os achados no documento "
            "original e registre a revisão humana no painel."
        )
    else:
        decision = (
            f"A classificação atual é: {status_text}. O relatório serve como síntese "
            "para a conferência operacional e deve ser lido junto com o documento de origem."
        )
    scope = metadata.get("analysis_scope") or {}
    pages = scope.get("pages") if isinstance(scope, dict) else None
    if pages:
        scope_text = f"Páginas consideradas pela análise automatizada: {_pages_text(pages)}."
    else:
        scope_text = "A análise automatizada não informou um recorte específico de páginas."
    return [opening, scope_text, decision]


def _practical_implications(analysis: dict[str, Any]) -> list[str]:
    implications: list[str] = []
    if _items_for(analysis, "medicamentos_deferidos"):
        implications.append("Há medicamentos aprovados ou deferidos que podem entrar no acompanhamento de portfólio e registros.")
    if _items_for(analysis, "medicamentos_indeferidos"):
        implications.append("Há medicamentos indeferidos que merecem conferência antes de qualquer comunicação ou planejamento comercial.")
    if _items_for(analysis, "suplementos_deferidos") or _items_for(analysis, "suplementos_indeferidos"):
        implications.append("Há movimentações relacionadas a suplementos que podem exigir atualização de cadastro, status ou comunicação interna.")
    if _items_for(analysis, "estudos_clinicos_deferidos") or _items_for(analysis, "estudos_clinicos_indeferidos"):
        implications.append("Há atos ligados a ensaios clínicos; confirme o produto relacionado e os responsáveis antes de encaminhar o resultado.")
    if _items_for(analysis, "outros_atos"):
        implications.append("Foram identificados outros atos regulatórios; verifique se há impacto em registro, renovação, cancelamento ou acompanhamento de mercado.")
    if _items_for(analysis, "exigencias"):
        implications.append("Existem exigências ou alterações que podem demandar conferência de processo, cadastro, embalagem ou documentação.")
    if _items_for(analysis, "pendencias"):
        implications.append("Há pendências para acompanhamento; confirme responsáveis e prazos antes de considerar o assunto encerrado.")
    if not implications:
        implications.append("Não houve achado estruturado suficiente para indicar uma ação comercial específica neste recorte.")
    return implications


def _technical_opinion(analysis: dict[str, Any]) -> dict[str, Any] | None:
    value = analysis.get("parecer_tecnico")
    return value if isinstance(value, dict) else None


def _technical_opinion_lines(opinion: dict[str, Any]) -> list[str]:
    classification = TECHNICAL_LABELS.get(
        str(opinion.get("classificacao_geral")),
        "Classificação geral não informada",
    )
    risk = RISK_LABELS.get(str(opinion.get("nivel_risco")), "Não classificado")
    lines = [
        f"Escopo: {opinion.get('escopo', 'não informado')}",
        f"Classificação geral: {classification}",
        f"Nível de risco preliminar: {risk}",
        f"Conclusão preliminar: {opinion.get('conclusao_preliminar', 'não informada')}",
    ]
    if opinion.get("base_ids"):
        lines.append(f"Base documental: {_value_text(opinion['base_ids'])}")
    return lines


def _technical_opinion_table(opinion: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    classification = TECHNICAL_LABELS.get(str(opinion.get("classificacao_geral")), "Não informado")
    risk = RISK_LABELS.get(str(opinion.get("nivel_risco")), "Não classificado")
    base_ids = _list_text(opinion.get("base_ids") or "Não informada")
    cells = [
        ("Classificação geral", classification),
        ("Nível de risco preliminar", risk),
        ("Base documental", base_ids),
    ]
    table = Table(
        [
            [_paragraph(label, styles["metric_label"]) for label, _ in cells],
            [_paragraph(value, styles["metric_value"]) for _, value in cells],
        ],
        colWidths=(56.5 * mm, 56.5 * mm, 57 * mm),
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(SURFACE_TEAL)),
                ("BACKGROUND", (0, 1), (-1, 1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor(BRAND_TEAL)),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor(LINE)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def _recommendation_lines(item: Any) -> list[str]:
    if not isinstance(item, dict):
        return [_value_text(item)]
    lines = []
    for key in ("id", "acao", "justificativa", "prioridade", "responsavel_sugerido", "dependencia", "base_ids"):
        value = item.get(key)
        if value in (None, "", [], {}):
            continue
        lines.append(f"{FIELD_LABELS.get(key, key)}: {_value_text(value)}")
    return lines or [_value_text(item)]


def _page_decor(canvas: Any, document: Any) -> None:
    canvas.saveState()
    if document.page > 1:
        canvas.setStrokeColor(colors.HexColor(LINE))
        canvas.line(18 * mm, A4[1] - 13 * mm, A4[0] - 18 * mm, A4[1] - 13 * mm)
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.setFillColor(colors.HexColor(BRAND_NAVY))
        canvas.drawString(18 * mm, A4[1] - 10 * mm, "DB TECNOLOGIA")
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor(MUTED))
        canvas.drawRightString(A4[0] - 18 * mm, A4[1] - 10 * mm, "Análise regulatória | uso interno")
    canvas.setStrokeColor(colors.HexColor(LINE))
    canvas.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor(MUTED))
    canvas.drawString(18 * mm, 8 * mm, "Documento de apoio | análise regulatória preliminar")
    canvas.drawRightString(A4[0] - 18 * mm, 8 * mm, f"Página {document.page}")
    canvas.restoreState()


def build_report_pdf(metadata: dict[str, Any], analysis: dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=17 * mm,
        title=f"Relatório executivo - {metadata.get('source_filename', 'documento')}",
        author="DB Tecnologia | Agente de Automação e Análise Regulatória",
    )
    base = getSampleStyleSheet()
    styles = {
        "brand": ParagraphStyle("Brand", parent=base["Normal"], alignment=TA_CENTER, textColor=colors.HexColor(BRAND_NAVY), fontName="Helvetica-Bold", fontSize=10, leading=12, spaceAfter=2),
        "eyebrow": ParagraphStyle("Eyebrow", parent=base["Normal"], alignment=TA_CENTER, textColor=colors.HexColor(BRAND_TEAL), fontName="Helvetica-Bold", fontSize=7.5, leading=10, spaceAfter=7),
        "title": ParagraphStyle("ReportTitle", parent=base["Title"], alignment=TA_CENTER, textColor=colors.HexColor(BRAND_NAVY), fontName="Helvetica-Bold", fontSize=22, leading=26, spaceAfter=4),
        "subtitle": ParagraphStyle("ReportSubtitle", parent=base["Normal"], alignment=TA_CENTER, textColor=colors.HexColor(MUTED), fontSize=10, leading=14, spaceAfter=4),
        "section_title": ParagraphStyle("SectionTitle", parent=base["Heading2"], textColor=colors.HexColor(BRAND_NAVY), fontName="Helvetica-Bold", fontSize=11.5, leading=14),
        "body": ParagraphStyle("Body", parent=base["BodyText"], textColor=colors.HexColor(INK), fontSize=8.8, leading=12, spaceAfter=4),
        "callout": ParagraphStyle("Callout", parent=base["BodyText"], textColor=colors.HexColor(INK), fontSize=9.2, leading=13, spaceAfter=5),
        "muted": ParagraphStyle("Muted", parent=base["BodyText"], textColor=colors.HexColor(MUTED), fontSize=8.5, leading=11, spaceAfter=4),
        "metric_label": ParagraphStyle("MetricLabel", parent=base["BodyText"], textColor=colors.HexColor(BRAND_TEAL), fontName="Helvetica-Bold", fontSize=7.2, leading=9),
        "metric_value": ParagraphStyle("MetricValue", parent=base["BodyText"], textColor=colors.HexColor(BRAND_NAVY), fontName="Helvetica-Bold", fontSize=9, leading=11),
        "notice_label": ParagraphStyle("NoticeLabel", parent=base["BodyText"], textColor=colors.HexColor(BRAND_GOLD), fontName="Helvetica-Bold", fontSize=7.5, leading=10),
        "notice_body": ParagraphStyle("NoticeBody", parent=base["BodyText"], textColor=colors.HexColor(INK), fontSize=8.5, leading=11),
        "record_title": ParagraphStyle("RecordTitle", parent=base["BodyText"], textColor=colors.white, fontName="Helvetica-Bold", fontSize=8.5, leading=11),
        "record": ParagraphStyle("Record", parent=base["BodyText"], textColor=colors.HexColor(INK), fontSize=8.3, leading=11, spaceAfter=0),
        "table_header": ParagraphStyle("TableHeader", parent=base["BodyText"], fontSize=8, leading=10, textColor=colors.white),
        "table_cell": ParagraphStyle("TableCell", parent=base["BodyText"], fontSize=8, leading=10, textColor=colors.HexColor(INK)),
    }
    confidence = analysis.get("controle_confianca") or {}
    review = analysis.get("revisao_humana") or {}
    needs_review = bool(review.get("necessaria") or confidence.get("status") in {"baixa_confianca", "inconclusivo"})
    status_label = "Revisão humana necessária" if needs_review else "Pronto para conferência"
    status_text = (
        "O conteúdo pode orientar a conferência interna, mas deve ser validado no documento original antes de qualquer envio ou decisão."
        if needs_review
        else "A leitura automatizada não gerou alerta de confiança. Confira o documento original antes do uso externo."
    )
    story: list[Any] = [
        Spacer(1, 3 * mm),
        _paragraph("DB TECNOLOGIA", styles["brand"]),
        _paragraph("INTELIGÊNCIA DOCUMENTAL PARA DECISÕES MAIS RÁPIDAS", styles["eyebrow"]),
        _paragraph("Relatório executivo de análise regulatória", styles["title"]),
        _paragraph("Síntese técnica e operacional para conferência e acompanhamento comercial", styles["subtitle"]),
        HRFlowable(width="100%", thickness=1.2, color=colors.HexColor(BRAND_TEAL), spaceBefore=3, spaceAfter=8),
        _notice_box("STATUS DA LEITURA", f"{status_label}. {status_text}", styles, SURFACE_GOLD if needs_review else SURFACE_TEAL),
        Spacer(1, 5 * mm),
        _section_heading("Identificação do documento", styles),
        _metadata_table(metadata, styles),
        Spacer(1, 4 * mm),
        _section_heading("Resumo executivo", styles),
    ]

    story.extend(_paragraph(text, styles["callout"]) for text in _executive_summary(metadata, analysis))
    story.extend([_summary_table(analysis, styles), Spacer(1, 2 * mm)])
    story.append(_section_heading("O que isso significa na prática", styles))
    story.extend(_paragraph(f"- {text}", styles["body"]) for text in _practical_implications(analysis))
    story.append(_section_heading("Parecer técnico preliminar", styles))
    opinion = _technical_opinion(analysis)
    if opinion is None:
        story.append(_notice_box("LIMITAÇÃO", "O modelo não forneceu o bloco de análise técnica v2. Os achados abaixo permanecem como extração documental e não devem ser tratados como parecer.", styles))
    else:
        story.append(_paragraph(f"Escopo analisado: {opinion.get('escopo', 'não informado')}", styles["muted"]))
        story.append(_technical_opinion_table(opinion, styles))
        story.append(Spacer(1, 2 * mm))
        story.append(_notice_box("CONCLUSÃO", str(opinion.get("conclusao_preliminar", "Não informada.")), styles, SURFACE_TEAL))
        foundations = _items_for(opinion, "fundamentos")
        if foundations:
            story.append(KeepTogether([_section_heading("Fundamentos técnicos", styles), _record_card(foundations[0], 1, styles), Spacer(1, 2 * mm)]))
            for index, value in enumerate(foundations[1:], start=2):
                story.append(KeepTogether([_record_card(value, index, styles), Spacer(1, 2 * mm)]))
        else:
            story.append(KeepTogether([_section_heading("Fundamentos técnicos", styles), _paragraph("Nenhum fundamento técnico estruturado foi localizado.", styles["muted"])]))
        technical_findings = _items_for(opinion, "apontamentos_tecnicos")
        if technical_findings:
            story.append(KeepTogether([_section_heading("Apontamentos técnicos", styles), _record_card(technical_findings[0], 1, styles, accent=BRAND_NAVY), Spacer(1, 2 * mm)]))
            for index, value in enumerate(technical_findings[1:], start=2):
                story.append(KeepTogether([_record_card(value, index, styles, accent=BRAND_NAVY), Spacer(1, 2 * mm)]))
        else:
            story.append(KeepTogether([_section_heading("Apontamentos técnicos", styles), _paragraph("Nenhum apontamento técnico estruturado foi localizado.", styles["muted"])]))
        recommendations = _items_for(opinion, "recomendacoes")
        if recommendations:
            story.append(KeepTogether([_section_heading("Recomendações priorizadas", styles), _record_card(recommendations[0], 1, styles, accent=BRAND_GOLD), Spacer(1, 2 * mm)]))
            for index, value in enumerate(recommendations[1:], start=2):
                story.append(KeepTogether([_record_card(value, index, styles, accent=BRAND_GOLD), Spacer(1, 2 * mm)]))
        else:
            story.append(KeepTogether([_section_heading("Recomendações priorizadas", styles), _paragraph("Nenhuma recomendação foi estruturada.", styles["muted"])]))
        limits = _items_for(opinion, "limites")
        if limits:
            story.append(_section_heading("Limites declarados pelo analista", styles))
            story.extend(_paragraph(f"- {text}", styles["muted"]) for text in limits)
    story.append(_section_heading("Achados detalhados", styles))

    for key, title in SECTIONS:
        values = _items_for(analysis, key)
        if not values:
            story.append(KeepTogether([_section_heading(title, styles), _paragraph("Nenhum registro foi localizado no recorte analisado.", styles["muted"])]))
            continue
        story.append(KeepTogether([_section_heading(title, styles), _record_card(values[0], 1, styles), Spacer(1, 2 * mm)]))
        for index, value in enumerate(values[1:], start=2):
            story.append(KeepTogether([_record_card(value, index, styles), Spacer(1, 2 * mm)]))

    story.extend(
        [
            _section_heading("Controle de confiança e revisão humana", styles),
            _paragraph(f"Leitura: {_confidence_label(confidence.get('status'))}", styles["body"]),
            _paragraph(f"Revisão humana necessária: {'Sim' if review.get('necessaria') else 'Não'}", styles["body"]),
            _paragraph(f"Motivos: {_value_text(review.get('motivos', []))}", styles["body"]),
            _section_heading("Próximos passos recomendados", styles),
            _paragraph("1. Conferir os achados no PDF original e no Markdown convertido.", styles["body"]),
            _paragraph("2. Registrar a revisão humana quando houver baixa confiança, ambiguidade ou evidência incompleta.", styles["body"]),
            _paragraph("3. Liberar o envio pelo painel somente depois da conferência dos destinatários e do conteúdo.", styles["body"]),
            Spacer(1, 2 * mm),
            _notice_box("RESPONSABILIDADE", "Material de apoio documental; não constitui parecer jurídico, médico ou regulatório definitivo.", styles, SURFACE_BLUE),
        ]
    )
    document.build(story, onFirstPage=_page_decor, onLaterPages=_page_decor)
    return buffer.getvalue()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "report-renderer", "version": REPORT_VERSION}


@app.post("/v1/render")
def render_report(payload: dict[str, Any]) -> Response:
    metadata = payload.get("metadata")
    analysis = payload.get("analysis")
    if not isinstance(metadata, dict) or not isinstance(analysis, dict):
        raise HTTPException(status_code=422, detail="metadata e analysis sao obrigatorios")
    pdf = build_report_pdf(metadata, analysis)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"X-Report-Version": REPORT_VERSION},
    )
