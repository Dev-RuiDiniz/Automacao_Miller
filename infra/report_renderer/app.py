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
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


REPORT_VERSION = "1.1.0"
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
}
FIELD_ORDER = tuple(FIELD_LABELS)

app = FastAPI(
    title="Regulatory Report Renderer",
    version=REPORT_VERSION,
    description="Servico local para gerar relatorios PDF auditaveis.",
)


def _value_text(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _paragraph(text: Any, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(_value_text(text)).replace("\n", "<br/>") or "-", style)


def _metadata_table(metadata: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    rows = [[_paragraph("Campo", styles["table_header"]), _paragraph("Valor", styles["table_header"])]]
    for key in ("source_filename", "source_sha256", "page_count", "converter_version"):
        if key in metadata:
            rows.append([_paragraph(key, styles["table_cell"]), _paragraph(metadata[key], styles["table_cell"])])
    table = Table(rows, colWidths=(55 * mm, 115 * mm), repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
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
        "aceitavel": "Leitura sem alerta automático de confiança",
        "baixa_confianca": "Leitura que precisa de revisão humana",
        "inconclusivo": "Leitura inconclusiva por informações conflitantes",
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
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8f0f8")),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#b9c9d9")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d6e0e8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
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


def _page_decor(canvas: Any, document: Any) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d6e0e8"))
    canvas.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(18 * mm, 8 * mm, "Documento de apoio | análise regulatória")
    canvas.drawRightString(A4[0] - 18 * mm, 8 * mm, f"Página {document.page}")
    canvas.restoreState()


def build_report_pdf(metadata: dict[str, Any], analysis: dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=f"Relatorio regulatorio - {metadata.get('source_filename', 'documento')}",
        author="Agente de Automacao e Analise Regulatoria",
    )
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("ReportTitle", parent=base["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#153b63"), fontSize=18, leading=22),
        "subtitle": ParagraphStyle("ReportSubtitle", parent=base["Normal"], alignment=TA_CENTER, textColor=colors.HexColor("#475569"), fontSize=9.5, leading=13),
        "heading": ParagraphStyle("SectionHeading", parent=base["Heading2"], textColor=colors.HexColor("#153b63"), fontSize=12, leading=15, spaceBefore=10, spaceAfter=5),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontSize=9, leading=12, spaceAfter=4),
        "callout": ParagraphStyle("Callout", parent=base["BodyText"], textColor=colors.HexColor("#243b53"), fontSize=9.5, leading=13, spaceAfter=5),
        "metric_label": ParagraphStyle("MetricLabel", parent=base["BodyText"], textColor=colors.HexColor("#486581"), fontSize=7.5, leading=9),
        "metric_value": ParagraphStyle("MetricValue", parent=base["BodyText"], textColor=colors.HexColor("#102a43"), fontSize=9, leading=11),
        "table_header": ParagraphStyle("TableHeader", parent=base["BodyText"], fontSize=8, leading=10, textColor=colors.white),
        "table_cell": ParagraphStyle("TableCell", parent=base["BodyText"], fontSize=8, leading=10),
    }
    story: list[Any] = [
        _paragraph("Relatório executivo de análise regulatória", styles["title"]),
        Spacer(1, 3 * mm),
        _paragraph("Síntese para conferência operacional e acompanhamento comercial", styles["subtitle"]),
        Spacer(1, 2 * mm),
        _paragraph("Material de apoio documental; não constitui parecer jurídico, médico ou regulatório definitivo.", styles["subtitle"]),
        Spacer(1, 6 * mm),
        _paragraph("Metadados do documento", styles["heading"]),
        _metadata_table(metadata, styles),
        Spacer(1, 3 * mm),
        _paragraph("Resumo executivo", styles["heading"]),
    ]

    story.extend(_paragraph(text, styles["callout"]) for text in _executive_summary(metadata, analysis))
    story.extend([_summary_table(analysis, styles), Spacer(1, 2 * mm)])
    story.append(_paragraph("O que isso significa na prática", styles["heading"]))
    story.extend(_paragraph(f"- {text}", styles["body"]) for text in _practical_implications(analysis))
    story.append(_paragraph("Achados detalhados", styles["heading"]))

    for key, title in SECTIONS:
        story.extend([_paragraph(title, styles["heading"])])
        values = _items_for(analysis, key)
        if not values:
            story.append(_paragraph("Nenhum registro foi localizado no recorte analisado.", styles["body"]))
            continue
        for index, value in enumerate(values, start=1):
            lines = _item_lines(value)
            story.append(_paragraph(f"{index}. " + " | ".join(lines), styles["body"]))

    confidence = analysis.get("controle_confianca") or {}
    review = analysis.get("revisao_humana") or {}
    story.extend(
        [
            _paragraph("Controle de confiança e revisão humana", styles["heading"]),
            _paragraph(f"Leitura: {_confidence_label(confidence.get('status'))}", styles["body"]),
            _paragraph(f"Revisão humana necessária: {'Sim' if review.get('necessaria') else 'Não'}", styles["body"]),
            _paragraph(f"Motivos: {_value_text(review.get('motivos', []))}", styles["body"]),
            _paragraph("Próximos passos recomendados", styles["heading"]),
            _paragraph("1. Conferir os achados no PDF original e no Markdown convertido.", styles["body"]),
            _paragraph("2. Registrar a revisão humana quando houver baixa confiança, ambiguidade ou evidência incompleta.", styles["body"]),
            _paragraph("3. Liberar o envio pelo painel somente depois da conferência dos destinatários e do conteúdo.", styles["body"]),
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
