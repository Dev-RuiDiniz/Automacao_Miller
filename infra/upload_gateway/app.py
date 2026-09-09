from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import os
import secrets
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

import httpx
import psycopg
from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from infra.upload_gateway.storage import original_key, resolve_storage_key, storage_root

MAX_PDF_BYTES = 100 * 1024 * 1024
STATUSES = {"recebido", "processando", "aguardando_revisao", "concluido", "erro"}
STATIC_DIR = Path(__file__).with_name("static")
SESSION_COOKIE_NAME = "landing_session"
PASSWORD_HASH_SCHEME = "pbkdf2_sha256"
PASSWORD_HASH_ITERATIONS = 310_000
DEFAULT_SESSION_TTL_SECONDS = 8 * 60 * 60


@dataclass
class Submission:
    submission_id: str
    filename: str
    sha256: str
    size_bytes: int
    status: str
    source_key: str
    report_key: str | None
    message: str | None
    created_at: str
    updated_at: str


class SubmissionStore(Protocol):
    def initialize(self) -> None: ...
    def create(self, submission: Submission) -> Submission | None: ...
    def get(self, submission_id: str) -> Submission | None: ...
    def find_by_hash(self, sha256: str) -> Submission | None: ...
    def update(self, submission_id: str, **changes: Any) -> Submission | None: ...


class InMemoryStore:
    def __init__(self) -> None:
        self.items: dict[str, Submission] = {}

    def initialize(self) -> None:
        return None

    def create(self, submission: Submission) -> Submission | None:
        if self.find_by_hash(submission.sha256):
            return None
        self.items[submission.submission_id] = submission
        return submission

    def get(self, submission_id: str) -> Submission | None:
        return self.items.get(submission_id)

    def find_by_hash(self, sha256: str) -> Submission | None:
        return next((item for item in self.items.values() if item.sha256 == sha256), None)

    def update(self, submission_id: str, **changes: Any) -> Submission | None:
        item = self.get(submission_id)
        if item is None:
            return None
        for key, value in changes.items():
            setattr(item, "report_key" if key == "report_storage_key" else key, value)
        item.updated_at = now()
        return item


class PostgresStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def initialize(self) -> None:
        with psycopg.connect(self.database_url) as connection:
            connection.execute("CREATE SCHEMA IF NOT EXISTS automacao_miller")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS automacao_miller.documents (
                    submission_id TEXT PRIMARY KEY,
                    source TEXT NOT NULL DEFAULT 'landing',
                    source_document_id TEXT,
                    source_filename TEXT NOT NULL,
                    source_sha256 CHAR(64) NOT NULL UNIQUE,
                    mime_type TEXT NOT NULL DEFAULT 'application/pdf',
                    size_bytes BIGINT NOT NULL CHECK (size_bytes > 0),
                    source_storage_key TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('recebido', 'em_processamento', 'processando', 'aguardando_revisao', 'concluido', 'erro')),
                    current_stage TEXT NOT NULL DEFAULT 'recebido',
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    started_at TIMESTAMPTZ,
                    completed_at TIMESTAMPTZ,
                    report_storage_key TEXT,
                    message TEXT,
                    created_at TIMESTAMPTZ NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS automacao_miller.artifacts (
                    artifact_id BIGSERIAL PRIMARY KEY,
                    submission_id TEXT NOT NULL REFERENCES automacao_miller.documents(submission_id),
                    artifact_type TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    storage_key TEXT NOT NULL UNIQUE,
                    sha256 CHAR(64),
                    size_bytes BIGINT,
                    mime_type TEXT NOT NULL,
                    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (submission_id, artifact_type, version)
                )
                """
            )

    @staticmethod
    def _row(row: tuple[Any, ...] | None) -> Submission | None:
        if row is None:
            return None
        return Submission(*[value.isoformat() if isinstance(value, datetime) else value for value in row])

    def create(self, submission: Submission) -> Submission | None:
        try:
            with psycopg.connect(self.database_url) as connection:
                row = connection.execute(
                    """
                    INSERT INTO automacao_miller.documents
                    (submission_id, source_filename, source_sha256, size_bytes, source_storage_key,
                     status, current_stage, message, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_sha256) DO NOTHING
                    RETURNING submission_id, source_filename, source_sha256, size_bytes, status, source_storage_key,
                              report_storage_key, message, created_at, updated_at
                    """,
                    (
                        submission.submission_id,
                        submission.filename,
                        submission.sha256,
                        submission.size_bytes,
                        submission.source_key,
                        submission.status,
                        "recebido",
                        submission.message,
                        submission.created_at,
                        submission.updated_at,
                    ),
                ).fetchone()
                if row:
                    connection.execute(
                        """
                        INSERT INTO automacao_miller.artifacts
                        (submission_id, artifact_type, version, storage_key, sha256, size_bytes, mime_type)
                        VALUES (%s, 'original_pdf', 1, %s, %s, %s, 'application/pdf')
                        ON CONFLICT (storage_key) DO NOTHING
                        """,
                        (submission.submission_id, submission.source_key, submission.sha256, submission.size_bytes),
                    )
                return self._row(row)
        except psycopg.Error:
            raise

    def get(self, submission_id: str) -> Submission | None:
        with psycopg.connect(self.database_url) as connection:
            row = connection.execute(
                "SELECT submission_id, source_filename, source_sha256, size_bytes, status, source_storage_key, report_storage_key, message, created_at, updated_at FROM automacao_miller.documents WHERE submission_id = %s",
                (submission_id,),
            ).fetchone()
        return self._row(row)

    def find_by_hash(self, sha256: str) -> Submission | None:
        with psycopg.connect(self.database_url) as connection:
            row = connection.execute(
                "SELECT submission_id, source_filename, source_sha256, size_bytes, status, source_storage_key, report_storage_key, message, created_at, updated_at FROM automacao_miller.documents WHERE source_sha256 = %s",
                (sha256,),
            ).fetchone()
        return self._row(row)

    def update(self, submission_id: str, **changes: Any) -> Submission | None:
        allowed = {"status", "message", "report_storage_key", "source_storage_key", "source_filename", "current_stage"}
        changes = {key: value for key, value in changes.items() if key in allowed}
        changes["updated_at"] = datetime.now(timezone.utc)
        assignments = ", ".join(f"{key} = %s" for key in changes)
        values = [*changes.values(), submission_id]
        with psycopg.connect(self.database_url) as connection:
            row = connection.execute(
                f"UPDATE automacao_miller.documents SET {assignments} WHERE submission_id = %s RETURNING submission_id, source_filename, source_sha256, size_bytes, status, source_storage_key, report_storage_key, message, created_at, updated_at",
                values,
            ).fetchone()
        return self._row(row)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def settings() -> dict[str, str]:
    return {
        "storage_dir": os.getenv("ARTIFACT_STORAGE_DIR", "/data/artifacts"),
        "landing_token": os.getenv("LANDING_ACCESS_TOKEN", ""),
        "internal_token": os.getenv("INTERNAL_API_TOKEN", ""),
        "landing_username": os.getenv("LANDING_USERNAME", ""),
        "landing_password_hash": os.getenv("LANDING_PASSWORD_HASH", ""),
        "session_secret": os.getenv("AUTH_SESSION_SECRET", ""),
        "session_ttl_seconds": os.getenv("AUTH_SESSION_TTL_SECONDS", str(DEFAULT_SESSION_TTL_SECONDS)),
        "session_cookie_secure": os.getenv("SESSION_COOKIE_SECURE", "true"),
        "n8n_webhook_url": os.getenv("N8N_SUBMISSION_WEBHOOK_URL", ""),
    }


def build_store() -> SubmissionStore:
    database_url = os.getenv("DATABASE_URL", "")
    return PostgresStore(database_url) if database_url else InMemoryStore()


store = build_store()
app = FastAPI(title="Regulatory Upload Gateway", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def hash_password(password: str, *, salt: bytes | None = None, iterations: int = PASSWORD_HASH_ITERATIONS) -> str:
    password_bytes = password.encode("utf-8")
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password_bytes, salt, iterations)
    return f"{PASSWORD_HASH_SCHEME}${iterations}${_b64encode(salt)}${_b64encode(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, raw_iterations, raw_salt, raw_digest = encoded.split("$", 3)
        if scheme != PASSWORD_HASH_SCHEME:
            return False
        iterations = int(raw_iterations)
        if iterations < 100_000 or iterations > 2_000_000:
            return False
        salt = _b64decode(raw_salt)
        expected = _b64decode(raw_digest)
    except (TypeError, ValueError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return secrets.compare_digest(actual, expected)


def session_ttl_seconds() -> int:
    try:
        return max(300, min(int(settings()["session_ttl_seconds"]), 7 * 24 * 60 * 60))
    except ValueError:
        return DEFAULT_SESSION_TTL_SECONDS


def session_cookie_secure() -> bool:
    return settings()["session_cookie_secure"].strip().lower() in {"1", "true", "yes", "on"}


def _create_session(username: str) -> str:
    secret = settings()["session_secret"]
    issued_at = int(time.time())
    payload = {"sub": username, "exp": issued_at + session_ttl_seconds()}
    encoded_payload = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(secret.encode("utf-8"), encoded_payload.encode("ascii"), hashlib.sha256).digest()
    return f"{encoded_payload}.{_b64encode(signature)}"


def _session_username(request: Request) -> str | None:
    secret = settings()["session_secret"]
    raw_session = request.cookies.get(SESSION_COOKIE_NAME, "")
    if not secret or "." not in raw_session:
        return None
    encoded_payload, supplied_signature = raw_session.split(".", 1)
    expected_signature = hmac.new(secret.encode("utf-8"), encoded_payload.encode("ascii"), hashlib.sha256).digest()
    try:
        valid_signature = secrets.compare_digest(_b64decode(supplied_signature), expected_signature)
        payload = json.loads(_b64decode(encoded_payload))
    except (ValueError, TypeError, binascii.Error, json.JSONDecodeError):
        return None
    if not valid_signature or not isinstance(payload, dict):
        return None
    if not isinstance(payload.get("sub"), str) or not isinstance(payload.get("exp"), int):
        return None
    if payload["exp"] <= int(time.time()):
        return None
    return payload["sub"]


def _valid_landing_token(supplied: str | None) -> bool:
    expected = settings()["landing_token"]
    return bool(expected and supplied and secrets.compare_digest(supplied, expected))


@app.on_event("startup")
def startup() -> None:
    root = storage_root()
    root.joinpath("incoming").mkdir(parents=True, exist_ok=True)
    root.joinpath("objects").mkdir(parents=True, exist_ok=True)
    store.initialize()


def require_landing_access(
    request: Request,
    x_landing_token: str | None = Header(default=None),
    token: str | None = None,
) -> None:
    if _valid_landing_token(x_landing_token or token) or _session_username(request):
        return
    raise HTTPException(status_code=403, detail="Acesso privado inválido.")


def _auth_is_configured() -> bool:
    config = settings()
    return bool(config["landing_username"] and config["landing_password_hash"] and config["session_secret"])


def _login_error(message: str, status_code: int = 401) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": message})


@app.post("/auth/login")
def login(payload: dict[str, Any], response: Response) -> dict[str, Any]:
    if not _auth_is_configured():
        return _login_error("O acesso por usuário e senha ainda não foi configurado.", 503)
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))
    configured_username = settings()["landing_username"]
    username_matches = secrets.compare_digest(username, configured_username)
    password_matches = verify_password(password, settings()["landing_password_hash"])
    if not username_matches or not password_matches:
        return _login_error("Usuário ou senha inválidos.")
    response.set_cookie(
        SESSION_COOKIE_NAME,
        _create_session(configured_username),
        max_age=session_ttl_seconds(),
        httponly=True,
        secure=session_cookie_secure(),
        samesite="lax",
        path="/",
    )
    return {"ok": True, "redirect": "/upload"}


@app.post("/auth/logout")
def logout(response: Response) -> dict[str, bool]:
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return {"ok": True}


@app.get("/")
def landing_entry(request: Request) -> Response:
    legacy_token = request.headers.get("X-Landing-Token") or request.query_params.get("token")
    if _valid_landing_token(legacy_token):
        return FileResponse(STATIC_DIR / "index.html")
    if _session_username(request):
        return RedirectResponse(url="/upload", status_code=303)
    return FileResponse(STATIC_DIR / "login.html")


@app.get("/upload", dependencies=[Depends(require_landing_access)])
def landing() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "upload-gateway"}


def require_internal_access(x_internal_token: str | None = Header(default=None)) -> None:
    expected = settings()["internal_token"]
    if not expected or not secrets.compare_digest(x_internal_token or "", expected):
        raise HTTPException(status_code=403, detail="Acesso interno inválido.")


def public_submission(item: Submission) -> dict[str, Any]:
    return {
        "submission_id": item.submission_id,
        "status": item.status,
        "filename": item.filename,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "message": item.message,
    }


@app.post("/api/v1/submissions", status_code=202, dependencies=[Depends(require_landing_access)])
async def create_submission(file: UploadFile = File(...)) -> JSONResponse:
    filename = Path(file.filename or "document.pdf").name
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Envie um arquivo PDF.")

    storage_dir = storage_root()
    submission_id = str(uuid.uuid4())
    incoming_dir = storage_dir / "incoming"
    incoming_dir.mkdir(parents=True, exist_ok=True)
    temporary_path = incoming_dir / f"{submission_id}.upload"
    digest = hashlib.sha256()
    total = 0
    first_chunk = b""
    try:
        with temporary_path.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                if not first_chunk:
                    first_chunk = chunk[:5]
                total += len(chunk)
                if total > MAX_PDF_BYTES:
                    raise HTTPException(status_code=413, detail="O PDF excede o limite de 100 MB.")
                digest.update(chunk)
                output.write(chunk)
    except HTTPException:
        temporary_path.unlink(missing_ok=True)
        raise
    except OSError as exc:
        temporary_path.unlink(missing_ok=True)
        raise HTTPException(status_code=507, detail="Não foi possível persistir o upload.") from exc

    if first_chunk != b"%PDF-":
        temporary_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="O conteúdo enviado não é um PDF válido.")

    source_key = original_key(digest.hexdigest())
    source_path = resolve_storage_key(source_key)
    target_existed = source_path.exists()
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.parent.chmod(0o770)
    os.replace(temporary_path, source_path)
    source_path.chmod(0o660)
    timestamp = now()
    item = Submission(submission_id, filename, digest.hexdigest(), total, "recebido", source_key, None, None, timestamp, timestamp)
    try:
        created = store.create(item)
    except psycopg.Error as exc:
        if not target_existed:
            source_path.unlink(missing_ok=True)
        raise HTTPException(status_code=503, detail="Não foi possível registrar o documento.") from exc
    if created is None:
        existing = store.find_by_hash(item.sha256)
        if existing and existing.source_key != source_key:
            source_path.unlink(missing_ok=True)
        return JSONResponse(status_code=200, content=public_submission(existing) if existing else {"submission_id": submission_id, "status": "recebido"})

    webhook = settings()["n8n_webhook_url"]
    if webhook:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(webhook, json={"submission_id": submission_id, "filename": filename})
                response.raise_for_status()
            store.update(submission_id, status="recebido")
        except httpx.HTTPError:
            store.update(submission_id, status="recebido", message="Aguardando despacho para o n8n.")

    return JSONResponse(status_code=202, content=public_submission(store.get(submission_id) or item))


@app.get("/api/v1/submissions/{submission_id}", dependencies=[Depends(require_landing_access)])
def get_submission(submission_id: str) -> dict[str, Any]:
    item = store.get(submission_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado.")
    return public_submission(item)


@app.get("/api/v1/submissions/{submission_id}/report", dependencies=[Depends(require_landing_access)])
def download_report(submission_id: str) -> FileResponse:
    item = store.get(submission_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado.")
    if item.status != "concluido" or not item.report_key:
        raise HTTPException(status_code=409, detail="O relatório ainda não está disponível.")
    try:
        report = resolve_storage_key(item.report_key)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Relatório não encontrado.") from exc
    storage = storage_root()
    if storage not in report.parents or not report.is_file():
        raise HTTPException(status_code=404, detail="Relatório não encontrado.")
    return FileResponse(report, media_type="application/pdf", filename=f"relatorio-{submission_id}.pdf")


@app.get("/internal/submissions/{submission_id}/file", dependencies=[Depends(require_internal_access)])
def get_source_file(submission_id: str) -> FileResponse:
    item = store.get(submission_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    try:
        source = resolve_storage_key(item.source_key)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.") from exc
    if not source.is_file():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    return FileResponse(source, media_type="application/pdf", filename=item.filename)


@app.post("/internal/submissions/{submission_id}/status", dependencies=[Depends(require_internal_access)])
def update_submission_status(submission_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    status = payload.get("status")
    if status not in STATUSES:
        raise HTTPException(status_code=422, detail="Status inválido.")
    changes: dict[str, Any] = {"status": status}
    if "message" in payload:
        changes["message"] = payload["message"]
    report_key = payload.get("report_key", payload.get("report_path"))
    if report_key is not None:
        try:
            resolve_storage_key(str(report_key))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Chave de relatório inválida.") from exc
        changes["report_storage_key"] = str(report_key).replace("\\", "/")
    if status == "concluido" and not (report_key or (item := store.get(submission_id)) and item.report_key):
        raise HTTPException(status_code=422, detail="Conclusão exige relatório interno persistido.")
    item = store.update(submission_id, **changes)
    if item is None:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado.")
    return public_submission(item)
