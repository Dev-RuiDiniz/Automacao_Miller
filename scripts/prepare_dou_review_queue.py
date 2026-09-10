from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parents[1]))

from infra.dou.collector import sha256_file
from infra.rag.chunker import split_markdown_by_page
from infra.regulatory_analysis.quality import validate_analysis
from infra.pdf_converter.converter import ConversionError, convert_pdf_bytes


def _submission_id(item: dict[str, Any]) -> str:
    return f"dou-{item['publication_date']}-{item['section'].lower()}"


def _context(markdown: str, limit: int = 24000) -> str:
    chunks = split_markdown_by_page(markdown, 1200, 150)
    terms = ("anvisa", "medicamento", "suplemento", "ensaio clínico", "deferido", "indeferido", "cancelado", "resolução", "exigência")
    ranked = sorted(chunks, key=lambda chunk: sum(chunk.content.casefold().count(term) for term in terms), reverse=True)
    text = "\n\n".join(chunk.content for chunk in ranked)
    return text if len(text) <= limit else text[:limit]


def _ollama_candidate(markdown: str, submission_id: str) -> dict[str, Any]:
    schema_path = Path(__file__).parents[1] / "prompts" / "regulatory-extraction.schema.json"
    payload = {
        "model": os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
        "stream": False,
        "format": json.loads(schema_path.read_text(encoding="utf-8")),
        "options": {"temperature": 0, "num_predict": 4096},
        "prompt": "Você é um extrator documental regulatório. Retorne somente JSON válido conforme o schema. Use exclusivamente o contexto RAG deste documento, não invente dados e não use conhecimento externo. Todo achado positivo deve conter paginas_origem e evidencia literal curta. Status permitidos: deferido, indeferido, cancelado e outro. Preserve cancelado separado de indeferido e não classifique dispositivo como medicamento ou suplemento. Protocolo: " + submission_id + "\n\nCONTEXTO RAG:\n" + _context(markdown),
    }
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    request = urllib.request.Request(base_url + "/api/generate", data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "300"))) as response:
        raw = json.loads(response.read().decode("utf-8")).get("response", "")
    analysis = json.loads(raw)
    quality = validate_analysis(analysis, markdown, submission_id)
    return {"submission_id": submission_id, "analysis": analysis, "quality": quality.as_dict(), "candidate": True}


def main() -> int:
    parser = argparse.ArgumentParser(description="Converte PDFs do DOU e prepara fila de revisão humana")
    parser.add_argument("--staging", type=Path, required=True)
    parser.add_argument("--generate-candidates", action="store_true")
    args = parser.parse_args()
    manifest_path = args.staging / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    markdown_dir = args.staging / "markdown"
    analyses_dir = args.staging / "analyses"
    markdown_dir.mkdir(parents=True, exist_ok=True)
    analyses_dir.mkdir(parents=True, exist_ok=True)
    queue: list[dict[str, Any]] = []
    for item in manifest.get("items", []):
        if item.get("kind") != "pdf" or item.get("status") != "downloaded":
            continue
        source = args.staging / item["path"]
        submission_id = _submission_id(item)
        try:
            pdf_bytes = source.read_bytes()
            converted = convert_pdf_bytes(pdf_bytes, item["filename"], submission_id)
        except (OSError, ConversionError) as exc:
            queue.append({"submission_id": submission_id, "status": "erro", "stage": "conversao", "error": str(exc), "source_sha256": item.get("sha256")})
            continue
        markdown_path = markdown_dir / f"{submission_id}.md"
        markdown_path.write_text(converted["markdown"], encoding="utf-8")
        record = {"submission_id": submission_id, "source": "dou_inlabs", "filename": item["filename"], "publication_date": item["publication_date"], "section": item["section"], "source_sha256": sha256_file(source), "markdown_sha256": hashlib.sha256(converted["markdown"].encode("utf-8")).hexdigest(), "page_count": converted["metadata"]["page_count"], "status": "aguardando_revisao", "warnings": converted["warnings"], "markdown_path": str(markdown_path.relative_to(args.staging)).replace("\\", "/")}
        if args.generate_candidates:
            try:
                candidate = _ollama_candidate(converted["markdown"], submission_id)
                record.update(candidate)
            except Exception as exc:
                record.update({"candidate": False, "candidate_error": f"Falha técnica no candidato: {type(exc).__name__}"})
        (analyses_dir / f"{submission_id}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        queue.append(record)
    (args.staging / "review_queue.jsonl").write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in queue), encoding="utf-8")
    print(f"Documentos preparados: {len(queue)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
