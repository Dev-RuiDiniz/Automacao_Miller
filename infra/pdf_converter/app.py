from __future__ import annotations

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from .converter import ConversionError, convert_pdf_bytes

MAX_PDF_BYTES = 100 * 1024 * 1024

app = FastAPI(
    title="PDF to Markdown Converter",
    version="0.3.0",
    description="Conversor interno e determinístico de PDF para Markdown.",
)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "pdf-converter"}


@app.post("/v1/convert")
async def convert_endpoint(
    file: UploadFile = File(...),
    source_document_id: str | None = Form(default=None),
) -> JSONResponse:
    filename = file.filename or "document.pdf"
    if not filename.lower().endswith(".pdf"):
        return JSONResponse(
            status_code=415,
            content={"error": {"code": "UNSUPPORTED_MEDIA_TYPE", "message": "O arquivo deve ter extensão .pdf."}},
        )

    content = await file.read()
    if len(content) > MAX_PDF_BYTES:
        return JSONResponse(
            status_code=413,
            content={"error": {"code": "PDF_TOO_LARGE", "message": "O PDF excede o limite de 100 MB."}},
        )

    try:
        result = convert_pdf_bytes(content, filename, source_document_id)
    except ConversionError as error:
        return JSONResponse(
            status_code=422,
            content={"error": {"code": error.code, "message": error.message}},
        )

    return JSONResponse(status_code=200, content=result)
