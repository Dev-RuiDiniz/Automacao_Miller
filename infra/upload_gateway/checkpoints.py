"""Recuperação de etapas a partir de artefatos registrados no volume privado."""

from __future__ import annotations

import base64
import hashlib
import io
import json
import re
import zipfile
from typing import Any

from .storage import object_prefix, resolve_storage_key

LABELS = {
    "conversion": "conversão do PDF",
    "analysis": "análise do Markdown salvo",
    "report": "finalização do relatório salvo",
}
MAX_CHECKPOINT_BYTES = 128 * 1024 * 1024


class CheckpointError(ValueError):
    pass


def _read(artifact: dict[str, Any], source_hash: str) -> bytes:
    try:
        key = artifact["storage_key"]
        if not key.startswith(object_prefix(source_hash) + "/"):
            raise ValueError
        path = resolve_storage_key(key)
        size = path.stat().st_size
        if size > MAX_CHECKPOINT_BYTES or size != artifact.get("size_bytes"):
            raise ValueError
        content = path.read_bytes()
        if artifact.get("sha256") and hashlib.sha256(content).hexdigest() != artifact["sha256"]:
            raise ValueError
        return content
    except (OSError, ValueError, KeyError):
        raise CheckpointError("O artefato salvo está ausente ou divergente. Confira o armazenamento antes de retomar.") from None


def _latest(artifacts: list[dict], kind: str) -> dict | None:
    return max((a for a in artifacts if a["artifact_type"] == kind),
               key=lambda a: int(a["version"]), default=None)


def load_checkpoint(submission: Any, artifacts: list[dict]) -> dict:
    """O cliente não escolhe caminhos, versões nem a etapa a reutilizar."""
    context = {"resume_stage": "conversion", "submission_id": submission.submission_id,
               "source_document_id": submission.submission_id, "source_filename": submission.filename,
               "source_sha256": submission.sha256}
    source = _latest(artifacts, "markdown")
    if source is None:
        original = _latest(artifacts, "original_pdf")
        if original is None or hashlib.sha256(_read(original, submission.sha256)).hexdigest() != submission.sha256:
            raise CheckpointError("O PDF original não está íntegro para retomar a conversão.")
        return context
    if not source.get("sha256"):
        raise CheckpointError("O Markdown salvo não possui hash para conferir a integridade.")
    try:
        content = _read(source, submission.sha256)
        markdown = content.decode("utf-8")
        header = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", markdown, re.S)
        if header is None:
            raise ValueError
        fields = {}
        for line in header[1].splitlines():
            if ": " in line:
                key, value = line.split(": ", 1)
                if key in fields:
                    raise ValueError
                fields[key] = value
        pages = [int(n) for n in re.findall(r"(?m)^## Página ([1-9][0-9]*)[ \t]*\r?$", markdown)]
        count = int(fields["page_count"])
        if (fields["source_sha256"] != submission.sha256 or count < 1
                or pages != list(range(1, count + 1))
                or fields.get("source_document_id", submission.submission_id) != submission.submission_id):
            raise ValueError
        metadata = {"source_filename": submission.filename, "source_sha256": submission.sha256,
                    "markdown_sha256": source["sha256"], "page_count": count,
                    "converter_version": fields["converter_version"]}
    except CheckpointError:
        raise
    except (ValueError, KeyError, UnicodeError):
        raise CheckpointError("O Markdown salvo não corresponde ao documento ou às páginas registradas.") from None
    saved_metadata = source.get("metadata") or {}
    warnings = saved_metadata.get("warnings")
    if warnings is None:
        warnings = ["Retomada de Markdown anterior sem lista estruturada de avisos; confira também as notas presentes na fonte."]
    if not isinstance(warnings, list) or any(not isinstance(w, str) for w in warnings):
        raise CheckpointError("Os avisos registrados para o Markdown são inválidos.")
    context.update(resume_stage="analysis", status="converted", markdown=markdown,
                   metadata=metadata, warnings=warnings, markdown_storage_key=source["storage_key"],
                   reused_markdown_artifact_id=source["artifact_id"])
    report = _latest(artifacts, "report_markdown")
    report_metadata = (report or {}).get("metadata") or {}
    # Relatórios antigos sem vínculo/hash verificável não são checkpoints seguros.
    if (report is None or report["version"] < source["version"] or not report.get("sha256")
            or report_metadata.get("source_markdown_sha256") != source["sha256"]):
        return context
    try:
        report_text = _read(report, submission.sha256).decode("utf-8")
        if not report_text.strip():
            raise ValueError
    except CheckpointError:
        raise
    except (ValueError, UnicodeError):
        raise CheckpointError("O relatório Markdown salvo está inválido.") from None
    resume_report = {"report_markdown": report_text,
                     "prompt_version": report_metadata.get("prompt_version"),
                     "report_context": report_metadata.get("report_context") or {}}
    if resume_report["prompt_version"] == "V8-autossuficiente":
        info = resume_report["report_context"]
        bundle_key = info.get("verification_bundle_storage_key")
        bundle_hash = info.get("verification_bundle_sha256")
        if not bundle_key or not bundle_hash:
            return context
        try:
            path = resolve_storage_key(bundle_key)
            if not bundle_key.startswith(object_prefix(submission.sha256) + "/") or path.stat().st_size > MAX_CHECKPOINT_BYTES:
                raise ValueError
            bundle = path.read_bytes()
            if hashlib.sha256(bundle).hexdigest() != bundle_hash:
                raise ValueError
            with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
                entries = archive.infolist()
                if len(entries) != 4 or sum(e.file_size for e in entries) > MAX_CHECKPOINT_BYTES:
                    raise ValueError
                coverage = json.loads(archive.read("cobertura_anvisa_v8.json"))
                pdf = archive.read("relatorio_anvisa_v8.pdf")
                expected = coverage["artefatos_finais_pdf_jsonl"]["relatorio_anvisa_v8.pdf"]
                if (coverage["fonte"]["sha256"] != source["sha256"]
                        or coverage.get("situacao_da_entrega") != "COMPLETA"
                        or coverage.get("pendencias_integridade")
                        or hashlib.sha256(pdf).hexdigest() != expected["sha256"]
                        or len(pdf) != expected["bytes"] or not pdf.startswith(b"%PDF-")):
                    raise ValueError
            resume_report["prepared_pdf_base64"] = base64.b64encode(pdf).decode("ascii")
            resume_report["prepared_pdf_sha256"] = hashlib.sha256(pdf).hexdigest()
        except (OSError, ValueError, KeyError, zipfile.BadZipFile):
            raise CheckpointError("O pacote V8 salvo está ausente ou divergente. Confira o armazenamento antes de retomar.") from None
    else:
        pdf = _latest(artifacts, "report_pdf")
        if (pdf and pdf.get("sha256") and pdf["version"] == report["version"]
                and (pdf.get("metadata") or {}).get("source_report_sha256") == report["sha256"]):
            content = _read(pdf, submission.sha256)
            if not content.startswith(b"%PDF-"):
                raise CheckpointError("O PDF do relatório salvo está inválido.")
            resume_report["prepared_pdf_base64"] = base64.b64encode(content).decode("ascii")
            resume_report["prepared_pdf_sha256"] = hashlib.sha256(content).hexdigest()
    context.update(resume_stage="report", resume_report=resume_report)
    return context
