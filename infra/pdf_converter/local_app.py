"""Interface de conversão local isolada: não chama IA nem o workflow operacional."""
from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from starlette.concurrency import run_in_threadpool
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .converter import ConversionError, convert_pdf_bytes

MAX_PDF_BYTES = 100 * 1024 * 1024
EXPORTER_VERSION = "0.1.0"
STATIC_DIR = Path(__file__).parent / "static"
SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": (
        "default-src 'none'; script-src 'self'; style-src 'self'; "
        "connect-src 'self'; img-src 'self'; base-uri 'none'; "
        "frame-ancestors 'none'; form-action 'self'"
    ),
}

app = FastAPI(title="Miller - Markdown local", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
app.state.conversion_guard = threading.BoundedSemaphore(1)


def _error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


@app.middleware("http")
async def local_security(request: Request, call_next):
    # O header força preflight em outro site; não há CORS no modo local.
    origin = request.headers.get("origin")
    expected_origin = f"{request.url.scheme}://{request.headers.get('host', '')}"
    if request.method == "POST" and (
        request.headers.get("x-miller-local") != "1"
        or (origin is not None and origin != expected_origin)
    ):
        response = _error(403, "LOCAL_REQUEST_REQUIRED", "Use a interface local para enviar o PDF.")
    else:
        response = await call_next(request)
    response.headers.update(SECURITY_HEADERS)
    return response


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "local.html", media_type="text/html")


@app.get("/static/{filename}")
def asset(filename: str) -> FileResponse:
    media_types = {"local.js": "text/javascript", "local.css": "text/css"}
    if filename not in media_types:
        raise HTTPException(status_code=404)
    return FileResponse(STATIC_DIR / filename, media_type=media_types[filename])


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "markdown-local"}


def _basename(filename: str | None) -> str:
    return (filename or "documento.pdf").replace("\\", "/").rsplit("/", 1)[-1] or "documento.pdf"


def prepare_export(result: dict[str, Any], filename: str) -> dict[str, Any]:
    # O conversor recebe um nome neutro; nomes fornecidos pelo usuário nunca
    # participam da delimitação do frontmatter original ou dos marcadores.
    raw = result["markdown"]
    _, separator, body = raw.partition("\n---\n")
    if not raw.startswith("---\n") or not separator:
        raise ValueError("Formato intermediário de Markdown inesperado")
    metadata = {**result["metadata"], "source_filename": filename,
                "exporter_version": EXPORTER_VERSION}
    notes = [
        "# Notas da conversão local (não pertencem ao PDF)",
        "Este arquivo contém texto-fonte convertido, não um relatório de IA.",
        "OCR não foi executado. Página sem texto extraível não comprova ausência de informação.",
        "A contagem de páginas não comprova leitura visual, integridade de tabelas ou análise regulatória.",
    ]
    warnings = list(result["warnings"])
    if any(ord(character) < 32 and character not in "\r\n\t" for character in body):
        warnings.append(
            "O texto convertido contém caracteres de controle inesperados. "
            "Confira a extração no PDF original; o texto foi preservado."
        )
    if warnings:
        notes.append("## Avisos da conversão local")
        notes.extend("- " + warning for warning in warnings)
    else:
        notes.append("O conversor não emitiu avisos; isso não garante fidelidade visual ao PDF.")
    # JSON scalars são YAML seguro, inclusive para LF, aspas e caracteres Unicode.
    header = ["---"]
    for key in ["converter_version", "exporter_version", "source_filename", "source_sha256", "page_count"]:
        header.append(f"{key}: {json.dumps(metadata[key], ensure_ascii=True)}")
    header.append("---")
    markdown = "\n".join(header) + "\n\n" + "\n\n".join(notes) + "\n\n" + body
    metadata["markdown_sha256"] = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
    return {"status": "converted", "markdown": markdown, "metadata": metadata, "warnings": warnings}


@app.post("/api/convert")
async def convert_local(request: Request, file: UploadFile = File(...)) -> JSONResponse:
    guard = request.app.state.conversion_guard
    acquired = False
    try:
        filename = _basename(file.filename)
        if not filename.lower().endswith(".pdf"):
            return _error(415, "UNSUPPORTED_MEDIA_TYPE", "Selecione um arquivo com extensão .pdf.")
        acquired = guard.acquire(blocking=False)
        if not acquired:
            return _error(429, "CONVERSION_BUSY", "Há outra conversão em andamento. Aguarde e tente novamente.")
        content = bytearray()
        while chunk := await file.read(1024 * 1024):
            if len(content) + len(chunk) > MAX_PDF_BYTES:
                return _error(413, "PDF_TOO_LARGE", "O PDF excede o limite de 100 MiB.")
            content.extend(chunk)
        # Não usar o nome arbitrário no frontmatter não escapado do conversor legado.
        result = await run_in_threadpool(convert_pdf_bytes, bytes(content), "documento.pdf", None)
        exported = prepare_export(result, filename)
        return JSONResponse(content=exported)
    except ConversionError as error:
        return _error(422, error.code, error.message)
    except Exception:
        return _error(500, "CONVERSION_FAILED", "Não foi possível concluir a conversão local. Tente novamente.")
    finally:
        if acquired:
            guard.release()
        await file.close()
