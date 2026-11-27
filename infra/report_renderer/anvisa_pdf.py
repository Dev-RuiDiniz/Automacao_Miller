"""Diagrama o relatório Anvisa a partir dos registros estruturados do V8."""

from __future__ import annotations

import io
from collections import defaultdict
from html import escape
from textwrap import shorten

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate

from .anvisa_v8 import AnvisaError, _walk

TITLE = "Relatório Anvisa - Medicamentos, Estudos Clínicos e Suplementos Alimentares"
MAX_REPORT_PAGES = 20
CATEGORIES = (
    "medicamentos", "estudos/ensaios clínicos", "suplementos alimentares",
    "normas e retificações pertinentes", "AFE/AE e atividades farmacêuticas",
    "certificações farmacêuticas", "laboratórios/escopos analíticos farmacêuticos",
)
LABELS = {
    "objeto": "Objeto", "ato": "Ato", "decisao": "Decisão", "dispositivo": "Dispositivo integral aplicável",
    "composicao": "Composição", "entidades": "Entidade", "processos": "Processo", "peticoes": "Petição",
    "apresentacoes": "Apresentação", "campos_adicionais": "Dados complementares", "relacoes": "Vínculo",
    "ressalvas": "Ressalva", "peticao_matriz": "Petição matriz", "vigencia": "Vigência do ato",
    "vigencia_ato": "Vigência do ato", "validade_certificacao": "Validade da certificação",
    "fundamento_legal": "Fundamento legal", "fundamento_do_decurso": "Fundamento do decurso de prazo",
    "escopo_certificacao": "Escopo da certificação", "cnpj": "CNPJ", "uf": "UF", "pais": "País",
    "endereco": "Endereço", "expedientes": "Expediente", "autorizacao": "Autorização", "descricao": "Descrição",
}
FIELD_STATES = {
    "nao_informado_no_bloco": "Não informado no bloco conferido",
    "nao_aplicavel": "Não aplicável",
    "ambiguo_ou_divergente": "Informação ambígua ou divergente; ver versões e ressalvas",
}


def _value(field) -> str:
    if isinstance(field, dict):
        return str(field.get("valor") or "")
    return str(field or "")


def _label(key: str) -> str:
    return LABELS.get(key, key.replace("_", " ").capitalize())


def _details(label: str, data):
    if isinstance(data, dict):
        if {"estado", "valor", "evidencias"} <= data.keys():
            value = _value(data) or FIELD_STATES.get(data["estado"], data["estado"])
            if data["estado"] != "nao_aplicavel":
                yield f"{label}: {value}"
        else:
            for key, value in data.items():
                if key != "evidencias":
                    yield from _details(f"{label} / {_label(key)}" if label else _label(key), value)
    elif isinstance(data, list):
        for i, item in enumerate(data, 1):
            yield from _details(f"{label} {i}", item)
    elif data is not None and data != "":
        yield f"{label}: {data}"


def _sections(records: list[dict], coverage: dict, filename: str, warnings: list[str]):
    groups = defaultdict(list)
    for record in records:
        if record["destino"] == "incluido":
            groups[record["categoria"].casefold()].append(record)
    pending = [record for record in records if record["destino"] == "pendente"]
    ordered = {**dict.fromkeys(CATEGORIES), **{name: None for name in groups}}
    yield "title", TITLE, ""
    yield "body", f"Fonte: {filename} | {len(coverage['paginas'])} páginas do Markdown. A numeração do relatório é distinta da fonte.", ""
    yield "heading", "Resumo executivo", ""
    counts = coverage["totais_por_destino"]
    yield "body", (f"Páginas analisadas segundo o modelo: {len(coverage['paginas'])}. "
        f"Incluídos: {counts.get('incluido', 0)}. Pendentes: {counts.get('pendente', 0)}. "
        f"Excluídos: {counts.get('excluido', 0)}. Representações duplicadas: {counts.get('representacao_duplicada', 0)}."), ""
    yield "body", f"Evidências literais conferidas mecanicamente: {coverage['evidencias_literais_conferidas']}. A análise automatizada é apoio documental e não constitui parecer ou aceite humano.", ""

    def card(record):
        source_pages = ", ".join(map(str, record["paginas_origem"]))
        yield "card", f"Ficha {record['id']} - {_value(record['objeto']) or 'Objeto não identificado'}", record["id"]
        yield "body", f"Fonte p. {source_pages} | ID interno | {record['categoria']}", ""
        if record["destino"] == "pendente":
            yield "body", f"Pertinência pendente: {record['justificativa_destino']}", ""
        for key in ("ato", "decisao", "dispositivo", "entidades", "processos", "peticoes", "composicao",
                    "apresentacoes", "campos_adicionais", "relacoes", "ressalvas"):
            for detail in _details("" if key == "campos_adicionais" else _label(key), record[key]):
                yield "body", detail, ""
        references = dict.fromkeys((e["pagina"], e["trecho_literal"]) for e in _walk(record)
                                   if {"pagina", "trecho_literal"} <= e.keys())
        for (page, quote) in references:
            yield "evidence", f"Evidência literal (fonte p. {page}): {quote.strip()}", ""

    yield "heading", "Resultados técnicos", ""
    for category in ordered:
        yield "heading", f"Fichas - {category}", ""
        if not groups[category]:
            yield "body", "Nenhum registro incluído nesta categoria no recorte analisado.", ""
        for record in groups[category]:
            yield from card(record)
    yield "heading", "Pendências, divergências e limitações", ""
    if not pending:
        yield "body", "Nenhum evento foi classificado como pendente de pertinência pelo modelo.", ""
    for record in pending:
        yield from card(record)
    for warning in warnings:
        yield "body", f"Aviso do conversor: {warning}", ""
    yield "body", "Os controles automáticos de cobertura, evidências e navegação não comprovam completude semântica. Confira as fichas e a fonte quando necessário.", ""


def _brief(value, length):
    text = " ".join(value.split())
    return shorten(text, width=length, placeholder="...") if len(text) > length else text


def _compact_sections(records, coverage, filename, warnings, limit):
    yield "title", TITLE, ""
    yield "body", f"Fonte: {_brief(filename, 120)} | {len(coverage['paginas'])} páginas do Markdown.", ""
    selected = records[:limit]
    yield "heading", "Resumo executivo", ""
    counts = coverage["totais_por_destino"]
    yield "body", (f"Incluídos: {counts.get('incluido', 0)}. Pendentes: {counts.get('pendente', 0)}. "
                   f"Excluídos: {counts.get('excluido', 0)}. "
                   f"Representações duplicadas: {counts.get('representacao_duplicada', 0)}. "
                   f"Evidências literais conferidas: {coverage['evidencias_literais_conferidas']}."), ""
    yield "body", (f"Este PDF resume {len(selected)} de {len(records)} fichas incluídas ou pendentes. "
                   "O Markdown e o pacote de verificação preservam as fichas e evidências detalhadas."), ""
    if warnings:
        yield "body", f"Avisos do conversor: {len(warnings)}. Consulte o Markdown para ler os avisos.", ""
    yield "body", "A análise automatizada é apoio documental. Confira as fichas e as páginas da fonte.", ""
    yield "heading", "Resultados técnicos", ""
    groups = defaultdict(list)
    for record in selected:
        category = "Pendências de pertinência" if record["destino"] == "pendente" else record["categoria"].capitalize()
        groups[category].append(record)
    for category, group in groups.items():
        yield "subheading", category, ""
        for record in group:
            label = _brief(_value(record["objeto"]), 105) or "Objeto não identificado"
            pages = _brief(", ".join(map(str, record["paginas_origem"])), 50)
            act = _brief(_value(record["ato"]), 80)
            processes = _brief(", ".join(_value(item) for item in record["processos"] if _value(item)), 65)
            references = [f"Fonte p. {pages}"]
            if act:
                references.append(f"Ato: {act}")
            if processes:
                references.append(f"Processo: {processes}")
            if record["apresentacoes"]:
                references.append(f"Apresentações: {len(record['apresentacoes'])}")
            entities = "; ".join(_value(item.get("nome")) for item in record["entidades"]
                                 if isinstance(item, dict) and _value(item.get("nome")))
            detail = [f"Entidade: {_brief(entities, 90)}"] if entities else []
            expiry = _brief(_value(record["campos_adicionais"].get("validade_registro")), 55)
            if expiry:
                detail.append(f"Validade do registro: {expiry}")
            example = next((item for item in record["apresentacoes"]
                            if isinstance(item, dict) and _value(item.get("registro"))), None)
            if example:
                registration = _brief(_value(example["registro"]), 32)
                shelf_life = _brief(_value(example.get("validade")), 40)
                detail.append(f"Exemplo de apresentação: {registration}" + (f" ({shelf_life})" if shelf_life else ""))
            pending = record["destino"] == "pendente"
            decision = record["justificativa_destino"] if pending else _value(record["decisao"])
            summary = _brief(decision, 210) or "Consulte a ficha integral."
            label_decision = "Pendência" if pending else "Decisão"
            lines = [f"Ficha {record['id']} - {label}", " | ".join(references), f"{label_decision}: {summary}"]
            if detail:
                lines.append(" | ".join(detail))
            yield "compact_card", "\n".join(lines), record["id"]


def _footer(canvas, document):
    canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
    canvas.line(16 * mm, 13 * mm, 194 * mm, 13 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#334155"))
    canvas.drawString(16 * mm, 9 * mm, "Relatório Anvisa V8 | Fonte e relatório têm paginações distintas")
    canvas.drawRightString(194 * mm, 9 * mm, f"Página do relatório: {document.page}")


def _verify_pdf(data: bytes, expected: list[str]):
    reader = PdfReader(io.BytesIO(data), strict=True)
    if len(reader.pages) > MAX_REPORT_PAGES:
        raise AnvisaError(f"PDF: o relatório excede o limite de {MAX_REPORT_PAGES} páginas.")
    page_text = [" ".join(page.extract_text().split()) for page in reader.pages]
    if not page_text or "Resumo executivo" not in page_text[0]:
        raise AnvisaError("PDF: resumo executivo inicial não localizado.")
    rendered = " ".join(page_text)
    if any(f"Ficha {rid} -" not in rendered for rid in expected):
        raise AnvisaError("PDF: ficha esperada não localizada no relatório.")
    return {"paginas_relatorio": len(reader.pages), "fichas_no_pdf": len(expected), "entradas_indice": 0}


class _PageLimit(Exception):
    pass


class _CompactCard(Paragraph):
    def split(self, *_):
        # As fichas resumidas cabem em uma página e devem ficar inteiras.
        return []


def _bounded_footer(canvas, document):
    if document.page > MAX_REPORT_PAGES:
        raise _PageLimit
    _footer(canvas, document)


def _build_pdf(sections):
    base = getSampleStyleSheet()
    navy = colors.HexColor("#163353")
    styles = {
        "title": ParagraphStyle("V8Title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=navy, alignment=0, keepWithNext=True),
        "heading": ParagraphStyle("V8Heading", parent=base["Heading2"], fontSize=13, leading=16, textColor=navy, keepWithNext=True),
        "subheading": ParagraphStyle("V8Subheading", parent=base["Heading3"], fontSize=10, leading=13, textColor=navy, keepWithNext=True),
        "card": ParagraphStyle("V8Card", parent=base["Heading3"], fontSize=10, leading=13, spaceBefore=9, textColor=navy, keepWithNext=True),
        "body": ParagraphStyle("V8Body", parent=base["BodyText"], fontSize=9, leading=12, spaceAfter=4),
        "evidence": ParagraphStyle("V8Evidence", parent=base["BodyText"], fontSize=8, leading=10.5, spaceAfter=4, textColor=colors.HexColor("#334155")),
        "compact_card": ParagraphStyle("V8CompactCard", parent=base["BodyText"], fontSize=8.5, leading=10, spaceAfter=4, textColor=navy),
    }
    output = io.BytesIO()
    document = SimpleDocTemplate(output, pagesize=A4, title=TITLE, author="DB Tecnologia",
                                 leftMargin=16 * mm, rightMargin=16 * mm, topMargin=15 * mm, bottomMargin=18 * mm)
    story, expected = [], []
    for kind, text, key in sections:
        safe = escape(text).replace("\n", "<br/>")
        if kind in {"card", "compact_card"}:
            expected.append(key)
        if kind == "compact_card":
            heading, details = safe.split("<br/>", 1)
            story.append(_CompactCard(f"<b>{heading}</b><br/>{details}", styles[kind]))
        else:
            story.append(Paragraph(safe, styles[kind]))
    document.build(story, onFirstPage=_bounded_footer, onLaterPages=_bounded_footer)
    pdf = output.getvalue()
    return pdf, _verify_pdf(pdf, expected)


def render(records: list[dict], coverage: dict, filename: str, warnings: list[str]):
    sections = list(_sections(records, coverage, filename, warnings))
    prefixes = {"title": "# ", "heading": "## ", "subheading": "### ", "card": "### "}
    markdown = "\n\n".join(prefixes.get(kind, "") + text.replace("<", "&lt;").replace(">", "&gt;")
                           for kind, text, _ in sections) + "\n"
    try:
        pdf, checks = _build_pdf(sections)
    except _PageLimit:
        visible = [r for destination in ("pendente", "incluido") for r in records if r["destino"] == destination]
        limit = len(visible)
        while True:
            try:
                pdf, checks = _build_pdf(_compact_sections(visible, coverage, filename, warnings, limit))
                break
            except _PageLimit:
                if not limit:
                    raise AnvisaError("PDF: o resumo excede o limite de páginas.") from None
                limit = limit * 4 // 5
        checks.update(modo="resumido", fichas_no_pdf=limit, fichas_totais=len(visible))
    return markdown, pdf, checks
