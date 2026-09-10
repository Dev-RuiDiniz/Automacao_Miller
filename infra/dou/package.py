from __future__ import annotations

import hashlib
import json
import zipfile
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from infra.report_renderer.app import build_report_pdf


FINDING_FIELDS = ("medicamentos_deferidos", "medicamentos_indeferidos", "suplementos_deferidos", "suplementos_indeferidos", "estudos_clinicos_deferidos", "estudos_clinicos_indeferidos", "outros_atos", "exigencias", "pendencias")


def batch_name(publication_date: str, start: str) -> str:
    offset = (date.fromisoformat(publication_date) - date.fromisoformat(start)).days
    return f"lote-{max(1, offset // 7 + 1):02d}"


def _empty_analysis() -> dict[str, Any]:
    return {field: [] for field in FINDING_FIELDS} | {"documento": {}, "categorias_nao_localizadas": [], "evidencias_insuficientes": [], "contradicoes": [], "avisos": [], "controle_confianca": {"status": "baixa_confianca", "motivos": []}, "revisao_humana": {"necessaria": True, "motivos": []}}


def _analysis_items(item: dict[str, Any], analysis_record: dict[str, Any] | None) -> tuple[list[dict[str, Any]], list[str]]:
    if not analysis_record:
        return [], ["Análise ainda não gerada ou aguardando revisão humana."]
    analysis = analysis_record.get("analysis") or {}
    findings: list[dict[str, Any]] = []
    for field in FINDING_FIELDS:
        for finding in analysis.get(field, []) if isinstance(analysis.get(field), list) else []:
            if isinstance(finding, dict):
                findings.append({**finding, "categoria": field, "documento_origem": item.get("filename"), "documento_id": item.get("submission_id"), "data_publicacao": item.get("publication_date"), "secao": item.get("section")})
    warnings = [str(value) for value in analysis.get("avisos", []) if value]
    if analysis.get("revisao_humana", {}).get("necessaria"):
        warnings.append("Revisão humana necessária.")
    quality = analysis_record.get("quality") or {}
    warnings.extend(str(value.get("message", value)) if isinstance(value, dict) else str(value) for value in quality.get("violations", []))
    return findings, warnings


def build_consolidated_markdown(manifest: dict[str, Any], analyses: dict[str, dict[str, Any]], dataset_manifest: dict[str, Any] | None = None) -> str:
    items = manifest.get("items", [])
    lines = ["# Relatório consolidado — corpus DOU", "", f"Período: **{manifest['period']['start']} a {manifest['period']['end']}**", "", "## Resumo da coleta", "", f"- Itens planejados: {len(items)}", f"- Itens baixados: {sum(item.get('status') == 'downloaded' for item in items)}", f"- Itens ausentes: {sum(item.get('status') == 'missing' for item in items)}", f"- Itens com erro: {sum(item.get('status') == 'error' for item in items)}", "- Fonte: INLABS / Imprensa Nacional", "", "## Edições e situações", ""]
    for item in items:
        lines.append(f"- `{item['publication_date']} / {item['section']}` — {item['kind']} — **{item['status']}** — SHA-256 `{item.get('sha256', 'não disponível')}`")
    all_findings: list[dict[str, Any]] = []
    all_warnings: list[str] = []
    for item in items:
        findings, warnings = _analysis_items(item, analyses.get(str(item.get("submission_id", ""))))
        all_findings.extend(findings)
        all_warnings.extend(warnings)
    lines.extend(["", "## Achados por documento", ""])
    if not all_findings:
        lines.append("Nenhum achado analisado foi disponibilizado. Os documentos permanecem na fila de revisão.")
    for finding in all_findings:
        pages = ", ".join(f"p. {page}" for page in finding.get("paginas_origem", [])) or "página não informada"
        lines.extend([f"### {finding.get('documento_origem', 'Documento')} — {finding.get('categoria', 'ato')}", f"- Publicação: {finding.get('data_publicacao')} | Seção: {finding.get('secao')} | Protocolo: {finding.get('documento_id')}", f"- Páginas de origem: {pages}", f"- Status: {finding.get('status', 'não informado')}", f"- Evidência: {finding.get('evidencia', 'não informada')}", ""])
    lines.extend(["## Alertas e evidências insuficientes", ""])
    for warning in sorted(set(all_warnings)):
        lines.append(f"- {warning}")
    if not all_warnings:
        lines.append("Nenhum alerta adicional registrado.")
    lines.extend(["", "## Dataset de treinamento", ""])
    if dataset_manifest:
        lines.extend([f"- Versão: `{dataset_manifest.get('dataset_version', 'não informada')}`", f"- Treino: {dataset_manifest.get('counts', {}).get('train', 0)}", f"- Validação: {dataset_manifest.get('counts', {}).get('validation', 0)}", f"- Pronto para fine-tuning: **{'sim' if dataset_manifest.get('ready') else 'não'}**"])
    else:
        lines.append("Nenhum dataset revisado foi incluído; documentos brutos não são exemplos de treinamento aprovados.")
    lines.extend(["", "## Modelos e integridade", "", "- Modelo de análise: `qwen2.5:3b`", "- Modelo de embedding: `nomic-embed-text`", "- Citações: página e trecho literal obrigatórios", "- Os hashes dos arquivos processados estão no manifesto da coleta.", ""])
    return "\n".join(lines)


def _aggregate_analysis(items: list[dict[str, Any]], analyses: dict[str, dict[str, Any]]) -> dict[str, Any]:
    result = _empty_analysis()
    result["documento"] = {"nome": f"Lote DOU ({len(items)} edições)"}
    result["controle_confianca"] = {"status": "baixa_confianca", "motivos": ["corpus aguardando revisão humana"]}
    pages: list[int] = []
    for item in items:
        findings, warnings = _analysis_items(item, analyses.get(str(item.get("submission_id", ""))))
        result["outros_atos"].extend(findings)
        result["avisos"].extend(warnings)
        record = analyses.get(str(item.get("submission_id", ""))) or {}
        pages.extend(record.get("pages", []))
    result["revisao_humana"] = {"necessaria": True, "motivos": ["relatório de lote para conferência"]}
    return result


def create_package(staging_dir: Path, output_dir: Path, dataset_manifest_path: Path | None = None) -> Path:
    manifest = json.loads((staging_dir / "manifest.json").read_text(encoding="utf-8"))
    analyses_dir = staging_dir / "analyses"
    analyses = {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in analyses_dir.glob("*.json")} if analyses_dir.exists() else {}
    dataset_manifest = json.loads(dataset_manifest_path.read_text(encoding="utf-8")) if dataset_manifest_path and dataset_manifest_path.exists() else None
    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir = output_dir / "relatorios-pdf"
    reports_dir.mkdir(exist_ok=True)
    consolidated = build_consolidated_markdown(manifest, analyses, dataset_manifest)
    (output_dir / "relatorio-consolidado.md").write_text(consolidated, encoding="utf-8")
    start = manifest["period"]["start"]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in manifest.get("items", []):
        grouped[batch_name(item["publication_date"], start)].append(item)
    for name, batch_items in sorted(grouped.items()):
        pdf = build_report_pdf({"source_filename": f"Corpus DOU {name}", "page_count": len(batch_items), "analysis_scope": {"pages": []}}, _aggregate_analysis(batch_items, analyses))
        PdfReader(__import__("io").BytesIO(pdf))
        (reports_dir / f"{name}.pdf").write_bytes(pdf)
    public_manifest = {key: value for key, value in manifest.items() if key != "items"}
    public_manifest["items"] = [{key: value for key, value in item.items() if key not in {"path", "url"}} for item in manifest.get("items", [])]
    (output_dir / "manifest.json").write_text(json.dumps(public_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    files = [path for path in output_dir.rglob("*") if path.is_file() and path.name != "checksums.sha256" and path.name != "pacote-dou.zip"]
    checksums = "\n".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(output_dir).as_posix()}" for path in sorted(files)) + "\n"
    (output_dir / "checksums.sha256").write_text(checksums, encoding="utf-8")
    zip_path = output_dir / "pacote-dou.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files + [output_dir / "checksums.sha256"]):
            archive.write(path, path.relative_to(output_dir).as_posix())
    return zip_path
