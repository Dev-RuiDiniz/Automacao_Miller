"""Materializa as duas partes da análise V8 a partir de lotes validados."""

from __future__ import annotations

import json
from pathlib import Path

from . import analysis_checkpoint, anvisa_pdf, anvisa_v8, incremental


def _escape_html(text: str) -> str:
    return text.replace("<", "&lt;").replace(">", "&gt;")


def _markdown(part: int, pages: range, records: list[dict]) -> bytes:
    page_range = f"{pages[0]} a {pages[-1]}" if pages else "sem páginas"
    lines = [f"# Parte {part} — Anvisa V8", "", f"Páginas-alvo: {page_range}.",
             f"Registros validados: {len(records)}.", ""]
    for value in records:
        record = json.loads(analysis_checkpoint.encode(value))
        lines.extend([f"## {record['id']}", ""])
        fields = {key: value for key, value in record.items() if key != "id"}
        lines.extend(f"- {_escape_html(detail)}" for detail in anvisa_pdf._details("", fields))
        lines.append("")
        references = dict.fromkeys((value["pagina"], value["trecho_literal"])
                                   for value in anvisa_v8._walk(record)
                                   if {"pagina", "trecho_literal"} <= value.keys())
        for page, quote in references:
            lines.extend([f"Evidência literal da página {page}:", ""])
            lines.extend(f"> {_escape_html(line)}" for line in quote.split("\n"))
            lines.append("")
    return ("\n".join(lines) + "\n").encode("utf-8")


class ReportParts:
    def __init__(self, page_count: int):
        midpoint = (page_count + 1) // 2
        self.pages = (range(1, midpoint + 1), range(midpoint + 1, page_count + 1))
        self.records: list[list[dict]] = []

    def save(self, directory: Path, state: dict):
        if len(self.records) == len(self.pages):
            return
        complete = state["completed"]
        covered = {n for lot in complete for n in lot["targets"]}
        for index in range(len(self.records), len(self.pages)):
            part_pages = self.pages[index]
            if not covered.issuperset(part_pages):
                break
            records = [record for lot in complete for record in lot["result"]["registros"]
                       if int(record["id"].split("-")[1][1:]) in part_pages]
            path = directory / f"parte-{index + 1}.md"
            content = _markdown(index + 1, part_pages, records)
            if not path.is_file() or path.read_bytes() != content:
                analysis_checkpoint.write_atomically(path, content)
            self.records.append(records)

    def consolidate(self, validated: list[dict]) -> list[dict]:
        if len(self.records) != len(self.pages):
            raise analysis_checkpoint.CheckpointStorageError("Partes do relatório ausentes na consolidação.")
        merged = incremental._merge(*self.records)
        records_by_id = {record["id"]: record for record in merged}
        if len(merged) != len(validated) or records_by_id != {record["id"]: record for record in validated}:
            raise analysis_checkpoint.CheckpointStorageError("Partes do relatório divergentes da análise validada.")
        return [records_by_id[record["id"]] for record in validated]
