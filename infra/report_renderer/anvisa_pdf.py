"""Diagrama o relatório Anvisa a partir dos registros estruturados do V8."""

from __future__ import annotations

import io
from collections import Counter, defaultdict
from html import escape

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate

from .anvisa_v8 import AnvisaError, _walk

TITLE = "Relatório Anvisa - Medicamentos, Estudos Clínicos e Suplementos Alimentares"
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


def _index(record):
    companies = [f"{_value(entity.get('nome'))} ({entity.get('papel', 'papel não indicado')})"
                 for entity in record["entidades"] if isinstance(entity, dict) and _value(entity.get("nome"))]
    source_pages = ", ".join(map(str, record["paginas_origem"]))
    main = " | ".join(s for s in (_value(record["objeto"]), "; ".join(companies),
        _value(record["decisao"]), f"Fonte p. {source_pages}") if s)
    for petition in record["peticoes"] or [{}]:
        subject = _value(petition.get("assunto"))
        ids = ", ".join(_value(value) for value in petition.get("expedientes", []) if _value(value))
        if not ids:
            ids = ", ".join(_value(value) for value in record["processos"] if _value(value))
        yield " | ".join(s for s in (record["id"], main, subject, ids) if s)


def _sections(records: list[dict], coverage: dict, filename: str, warnings: list[str]):
    groups = defaultdict(list)
    for record in records:
        if record["destino"] == "incluido":
            groups[record["categoria"].casefold()].append(record)
    pending = [record for record in records if record["destino"] == "pendente"]
    ordered = {**dict.fromkeys(CATEGORIES), **{name: None for name in groups}}
    yield "title", TITLE, ""
    yield "body", f"Fonte: {filename} | {len(coverage['paginas'])} páginas do Markdown. A numeração do relatório é distinta da fonte.", ""
    yield "heading", "Índice de assuntos e páginas de origem", ""
    for category in ordered:
        if groups[category]:
            yield "subheading", category.capitalize(), ""
        for record in groups[category]:
            for entry in _index(record):
                yield "index", entry, record["id"]
    if pending:
        yield "subheading", "Pendências de pertinência", ""
        for record in pending:
            for entry in _index(record):
                yield "index", entry, record["id"]
    if not groups or not any(groups.values()):
        yield "body", "Nenhuma ficha incluída no recorte analisado. Consulte as pendências ao final.", ""
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


class _CardHeading(Paragraph):
    key = ""

    def split(self, *args):
        parts = super().split(*args)
        if parts:
            parts[0].key = self.key
        return parts

    def draw(self):
        if self.key:
            self.canv.bookmarkHorizontal(self.key, 0, self.height)
        super().draw()


class _IndexEntry(Paragraph):
    key = ""

    def split(self, *args):
        parts = super().split(*args)
        for part in parts:
            part.key = self.key
        return parts

    def draw(self):
        super().draw()
        self.canv.linkRect(self.key, self.key, (0, 0, self.width, self.height), relative=1, thickness=0)


def _footer(canvas, document):
    canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
    canvas.line(16 * mm, 13 * mm, 194 * mm, 13 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#334155"))
    canvas.drawString(16 * mm, 9 * mm, "Relatório Anvisa V8 | Fonte e relatório têm paginações distintas")
    canvas.drawRightString(194 * mm, 9 * mm, f"Página do relatório: {document.page}")


def _verify_pdf(data: bytes, expected: list[str]):
    reader = PdfReader(io.BytesIO(data), strict=True)
    page_for = {page.indirect_reference.idnum: page for page in reader.pages}
    text_for = {n: " ".join(page.extract_text().split()) for n, page in page_for.items()}
    if not reader.pages or "Índice de assuntos" not in next(iter(text_for.values()), ""):
        raise AnvisaError("PDF: índice inicial não localizado.")
    found = Counter()
    for page in reader.pages:
        for annotation in page.get("/Annots", []):
            link = annotation.get_object()
            if link.get("/Subtype") == "/Link":
                dest = link.get("/Dest")
                rid = link.get("/Contents")
                if not dest or not rid or f"Ficha {rid} -" not in text_for.get(dest[0].idnum, ""):
                    raise AnvisaError("PDF: índice contém destino sem ficha correspondente.")
                found[rid] += 1
    # Uma entrada partida entre páginas produz mais de uma área clicável.
    counts = Counter(expected)
    if found.keys() != counts.keys() or any(found[rid] < count for rid, count in counts.items()):
        raise AnvisaError("PDF: ficha não acessível pelo índice.")
    return {"paginas_relatorio": len(reader.pages), "entradas_indice": len(expected)}


def render(records: list[dict], coverage: dict, filename: str, warnings: list[str]):
    base = getSampleStyleSheet()
    navy = colors.HexColor("#163353")
    styles = {
        "title": ParagraphStyle("V8Title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=navy, alignment=0, keepWithNext=True),
        "heading": ParagraphStyle("V8Heading", parent=base["Heading2"], fontSize=13, leading=16, textColor=navy, keepWithNext=True),
        "subheading": ParagraphStyle("V8Subheading", parent=base["Heading3"], fontSize=10, leading=13, textColor=navy, keepWithNext=True),
        "card": ParagraphStyle("V8Card", parent=base["Heading3"], fontSize=10, leading=13, spaceBefore=9, textColor=navy, keepWithNext=True),
        "body": ParagraphStyle("V8Body", parent=base["BodyText"], fontSize=9, leading=12, spaceAfter=4),
        "index": ParagraphStyle("V8Index", parent=base["BodyText"], fontSize=8.5, leading=11, spaceAfter=5, textColor=navy),
        "evidence": ParagraphStyle("V8Evidence", parent=base["BodyText"], fontSize=8, leading=10.5, spaceAfter=4, textColor=colors.HexColor("#334155")),
    }
    output = io.BytesIO()
    document = SimpleDocTemplate(output, pagesize=A4, title=TITLE, author="DB Tecnologia",
                                 leftMargin=16 * mm, rightMargin=16 * mm, topMargin=15 * mm, bottomMargin=18 * mm)
    story, markdown, expected = [], [], []
    for kind, text, key in _sections(records, coverage, filename, warnings):
        safe = escape(text).replace("\n", "<br/>")
        md_text = text.replace("<", "&lt;").replace(">", "&gt;")
        if kind == "index":
            expected.append(key)
            markdown.append(f"- {md_text}")
        else:
            prefix = {"title": "# ", "heading": "## ", "subheading": "### ", "card": "### "}.get(kind, "")
            markdown.append(prefix + md_text)
        cls = {"card": _CardHeading, "index": _IndexEntry}.get(kind, Paragraph)
        item = cls(safe, styles[kind])
        if key:
            item.key = key
        story.append(item)
    document.build(story, onFirstPage=_footer, onLaterPages=_footer)
    pdf = output.getvalue()
    return "\n\n".join(markdown) + "\n", pdf, _verify_pdf(pdf, expected)
