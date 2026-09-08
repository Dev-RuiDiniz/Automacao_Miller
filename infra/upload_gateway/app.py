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
    status: str
    source_path: str
    report_path: str | None
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
            setattr(item, key, value)
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
                CREATE TABLE IF NOT EXISTS automacao_miller.submissions (
                    submission_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    sha256 CHAR(64) NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    report_path TEXT,
                    message TEXT,
                    created_at TIMESTAMPTZ NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL
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
                    INSERT INTO automacao_miller.submissions
                    (submission_id, filename, sha256, status, source_path, report_path, message, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (sha256) DO NOTHING
                    RETURNING submission_id, filename, sha256, status, source_path, report_path, message, created_at, updated_at
                    """,
                    tuple(vars(submission).values()),
                ).fetchone()
                return self._row(row)
        except psycopg.Error:
            raise

    def get(self, submission_id: str) -> Submission | None:
        with psycopg.connect(self.database_url) as connection:
            row = connection.execute(
                "SELECT submission_id, filename, sha256, status, source_path, report_path, message, created_at, updated_at FROM automacao_miller.submissions WHERE submission_id = %s",
                (submission_id,),
            ).fetchone()
        return self._row(row)

    def find_by_hash(self, sha256: str) -> Submission | None:
        with psycopg.connect(self.database_url) as connection:
            row = connection.execute(
                "SELECT submission_id, filename, sha256, status, source_path, report_path, message, created_at, updated_at FROM automacao_miller.submissions WHERE sha256 = %s",
                (sha256,),
            ).fetchone()
        return self._row(row)

    def update(self, submission_id: str, **changes: Any) -> Submission | None:
        allowed = {"status", "message", "report_path", "source_path", "filename"}
        changes = {key: value for key, value in changes.items() if key in allowed}
        changes["updated_at"] = datetime.now(timezone.utc)
        assignments = ", ".join(f"{key} = %s" for key in changes)
        values = [*changes.values(), submission_id]
        with psycopg.connect(self.database_url) as connection:
            row = connection.execute(
                f"UPDATE automacao_miller.submissions SET {assignments} WHERE submission_id = %s RETURNING submission_id, filename, sha256, status, source_path, report_path, message, created_at, updated_at",
                values,
            ).fetchone()
        return self._row(row)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def settings() -> dict[str, str]:
    return {
        "storage_dir": os.getenv("UPLOAD_STORAGE_DIR", "/data/submissions"),
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
    Path(settings()["storage_dir"]).mkdir(parents=True, exist_ok=True)
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

    storage_dir = Path(settings()["storage_dir"])
    submission_id = str(uuid.uuid4())
    source_path = storage_dir / f"{submission_id}.pdf"
    digest = hashlib.sha256()
    total = 0
    first_chunk = b""
    try:
        with source_path.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                if not first_chunk:
                    first_chunk = chunk[:5]
                total += len(chunk)
                if total > MAX_PDF_BYTES:
                    raise HTTPException(status_code=413, detail="O PDF excede o limite de 100 MB.")
                digest.update(chunk)
                output.write(chunk)
    except HTTPException:
        source_path.unlink(missing_ok=True)
        raise
    except OSError as exc:
        source_path.unlink(missing_ok=True)
        raise HTTPException(status_code=507, detail="Não foi possível persistir o upload.") from exc

    if first_chunk != b"%PDF-":
        source_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="O conteúdo enviado não é um PDF válido.")

    timestamp = now()
    item = Submission(submission_id, filename, digest.hexdigest(), "recebido", str(source_path), None, None, timestamp, timestamp)
    created = store.create(item)
    if created is None:
        source_path.unlink(missing_ok=True)
        existing = store.find_by_hash(item.sha256)
        return JSONResponse(status_code=200, content=public_submission(existing) if existing else {"submission_id": submission_id, "status": "recebido"})

    webhook = settings()["n8n_webhook_url"]
    if webhook:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(webhook, json={"submission_id": submission_id, "filename": filename})
                response.raise_for_status()
            store.update(submission_id, status="processando")
        except httpx.HTTPError:
            store.update(submission_id, status="erro", message="Não foi possível iniciar o processamento no n8n.")

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
    if item.status != "concluido" or not item.report_path:
        raise HTTPException(status_code=409, detail="O relatório ainda não está disponível.")
    report = Path(item.report_path).resolve()
    storage = Path(settings()["storage_dir"]).resolve()
    if storage not in report.parents or not report.is_file():
        raise HTTPException(status_code=404, detail="Relatório não encontrado.")
    return FileResponse(report, media_type="application/pdf", filename=f"relatorio-{submission_id}.pdf")


@app.get("/internal/submissions/{submission_id}/file", dependencies=[Depends(require_internal_access)])
def get_source_file(submission_id: str) -> FileResponse:
    item = store.get(submission_id)
    if item is None or not Path(item.source_path).is_file():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    return FileResponse(item.source_path, media_type="application/pdf", filename=item.filename)


@app.post("/internal/submissions/{submission_id}/status", dependencies=[Depends(require_internal_access)])
def update_submission_status(submission_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    status = payload.get("status")
    if status not in STATUSES:
        raise HTTPException(status_code=422, detail="Status inválido.")
    changes: dict[str, Any] = {"status": status}
    if "message" in payload:
        changes["message"] = payload["message"]
    if "report_path" in payload:
        changes["report_path"] = payload["report_path"]
    item = store.update(submission_id, **changes)
    if item is None:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado.")
    return public_submission(item)
