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


REPORT_VERSION = "1.0.0"
SECTIONS: tuple[tuple[str, str], ...] = (
    ("medicamentos_deferidos", "Medicamentos deferidos"),
    ("medicamentos_indeferidos", "Medicamentos indeferidos"),
    ("suplementos_deferidos", "Suplementos deferidos"),
    ("suplementos_indeferidos", "Suplementos indeferidos"),
    ("estudos_clinicos_deferidos", "Estudos clinicos deferidos"),
    ("estudos_clinicos_indeferidos", "Estudos clinicos indeferidos"),
    ("outros_atos", "Outros atos regulatórios"),
    ("exigencias", "Exigencias"),
    ("pendencias", "Pendencias"),
    ("categorias_nao_localizadas", "Categorias nao localizadas"),
    ("evidencias_insuficientes", "Evidencias insuficientes"),
    ("contradicoes", "Contradicoes"),
    ("avisos", "Avisos"),
)

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
        return [f"{key}: {_value_text(value)}" for key, value in item.items() if value not in (None, "", [], {})]
    return [_value_text(item)]


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
        "title": ParagraphStyle("ReportTitle", parent=base["Title"], alignment=TA_CENTER, fontSize=17, leading=21),
        "subtitle": ParagraphStyle("ReportSubtitle", parent=base["Normal"], alignment=TA_CENTER, textColor=colors.HexColor("#475569")),
        "heading": ParagraphStyle("SectionHeading", parent=base["Heading2"], fontSize=12, leading=15, spaceBefore=9, spaceAfter=5),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontSize=9, leading=12, spaceAfter=3),
        "table_header": ParagraphStyle("TableHeader", parent=base["BodyText"], fontSize=8, leading=10, textColor=colors.white),
        "table_cell": ParagraphStyle("TableCell", parent=base["BodyText"], fontSize=8, leading=10),
    }
    story: list[Any] = [
        _paragraph("Relatorio de apoio a analise regulatoria", styles["title"]),
        Spacer(1, 3 * mm),
        _paragraph("Documento de apoio documental; nao constitui parecer regulatorio definitivo.", styles["subtitle"]),
        Spacer(1, 6 * mm),
        _paragraph("Metadados do documento", styles["heading"]),
        _metadata_table(metadata, styles),
    ]

    for key, title in SECTIONS:
        story.extend([_paragraph(title, styles["heading"])])
        values = analysis.get(key) or []
        if not isinstance(values, list):
            values = [values]
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
            _paragraph("Controle de confianca e revisao humana", styles["heading"]),
            _paragraph(f"Status: {confidence.get('status', 'nao informado')}", styles["body"]),
            _paragraph(f"Revisao humana necessaria: {review.get('necessaria', 'nao informado')}", styles["body"]),
            _paragraph(f"Motivos: {_value_text(review.get('motivos', []))}", styles["body"]),
        ]
    )
    document.build(story)
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
