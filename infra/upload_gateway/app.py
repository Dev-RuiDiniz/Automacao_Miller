from __future__ import annotations

import base64
import binascii
import re
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
from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from email.utils import parseaddr
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from infra.upload_gateway.storage import original_key, resolve_storage_key, storage_root

MAX_PDF_BYTES = 100 * 1024 * 1024
STATUSES = {"recebido", "processando", "aguardando_revisao", "aguardando_envio", "concluido", "erro"}
ARTIFACT_TYPES = {"original_pdf", "markdown", "analysis_json", "report_pdf"}
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
MAX_RECIPIENTS = 50
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
    def list_documents(self, query: str = "", status: str | None = None, page: int = 1, page_size: int = 25, date_from: str | None = None, date_to: str | None = None) -> tuple[list[Submission], int]: ...


class InMemoryStore:
    def __init__(self) -> None:
        self.items: dict[str, Submission] = {}
        self.artifacts: dict[str, list[dict[str, Any]]] = {}
        self.attempts: dict[str, list[dict[str, Any]]] = {}
        self.errors: dict[str, list[dict[str, Any]]] = {}
        self.reviews: dict[str, list[dict[str, Any]]] = {}
        self.recipients: dict[int, dict[str, Any]] = {}
        self.document_recipients: dict[str, list[str]] = {}
        self.deliveries: dict[int, dict[str, Any]] = {}
        self.next_id = 1

    def initialize(self) -> None:
        return None

    def create(self, submission: Submission) -> Submission | None:
        if self.find_by_hash(submission.sha256):
            return None
        self.items[submission.submission_id] = submission
        self.artifacts[submission.submission_id] = [{
            "artifact_id": self.next_id,
            "artifact_type": "original_pdf",
            "version": 1,
            "storage_key": submission.source_key,
            "sha256": submission.sha256,
            "size_bytes": submission.size_bytes,
            "mime_type": "application/pdf",
            "created_at": submission.created_at,
        }]
        self.next_id += 1
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

    def list_documents(self, query: str = "", status: str | None = None, page: int = 1, page_size: int = 25, date_from: str | None = None, date_to: str | None = None) -> tuple[list[Submission], int]:
        values = list(self.items.values())
        if query:
            needle = query.lower()
            values = [item for item in values if needle in item.submission_id.lower() or needle in item.filename.lower()]
        if status:
            values = [item for item in values if item.status == status]
        if date_from:
            values = [item for item in values if item.created_at[:10] >= date_from]
        if date_to:
            values = [item for item in values if item.created_at[:10] <= date_to]
        values.sort(key=lambda item: item.updated_at, reverse=True)
        total = len(values)
        start = (page - 1) * page_size
        return values[start:start + page_size], total

    def detail(self, submission_id: str) -> dict[str, Any]:
        item = self.get(submission_id)
        if item is None:
            raise KeyError(submission_id)
        return {
            "submission": item,
            "artifacts": self.artifacts.get(submission_id, []),
            "attempts": self.attempts.get(submission_id, []),
            "errors": self.errors.get(submission_id, []),
            "reviews": self.reviews.get(submission_id, []),
            "deliveries": [value for value in self.deliveries.values() if value["submission_id"] == submission_id],
        }

    def list_recipients(self) -> list[dict[str, Any]]:
        return sorted(self.recipients.values(), key=lambda value: (not value["active"], value["email"]))

    def replace_recipients(self, recipients: list[dict[str, Any]], actor: str) -> list[dict[str, Any]]:
        self.recipients = {}
        for recipient in recipients:
            recipient_id = self.next_id
            self.next_id += 1
            self.recipients[recipient_id] = {"recipient_id": recipient_id, **recipient, "created_by": actor, "updated_by": actor, "updated_at": now()}
        return self.list_recipients()

    def set_document_recipients(self, submission_id: str, emails: list[str], actor: str) -> None:
        self.document_recipients[submission_id] = emails

    def get_document_recipients(self, submission_id: str) -> list[str]:
        return self.document_recipients.get(submission_id, [])

    def get_active_recipient_emails(self) -> list[str]:
        return [value["email"] for value in self.list_recipients() if value["active"]]

    def create_delivery(self, submission_id: str, emails: list[str], actor: str, retry: bool = False) -> dict[str, Any]:
        if any(value["submission_id"] == submission_id and value["status"] in {"solicitado", "enviando"} for value in self.deliveries.values()):
            raise ValueError("envio_em_andamento")
        item = self.get(submission_id)
        if item is None:
            raise KeyError(submission_id)
        if item.status not in ({"erro"} if retry else {"aguardando_envio"}):
            raise ValueError("status_invalido")
        delivery_id = self.next_id
        self.next_id += 1
        delivery = {"delivery_id": delivery_id, "submission_id": submission_id, "recipient_emails": emails, "status": "solicitado", "attempt_count": 0, "requested_by": actor, "requested_at": now(), "sent_at": None, "error_message": None}
        self.deliveries[delivery_id] = delivery
        return delivery

    def update_delivery(self, delivery_id: int, **changes: Any) -> dict[str, Any] | None:
        delivery = self.deliveries.get(delivery_id)
        if delivery:
            delivery.update(changes)
        return delivery

    def add_review(self, submission_id: str, decision: str, notes: str, actor: str) -> dict[str, Any]:
        review = {"review_id": self.next_id, "submission_id": submission_id, "reason": "revisão operacional", "decision": decision, "reviewer": actor, "notes": notes, "requested_at": now(), "reviewed_at": now()}
        self.next_id += 1
        self.reviews.setdefault(submission_id, []).append(review)
        item = self.get(submission_id)
        if item:
            item.status = "aguardando_envio" if decision == "aprovado" else "recebido"
            item.message = None
            item.updated_at = now()
        return review


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
                    status TEXT NOT NULL CHECK (status IN ('recebido', 'em_processamento', 'processando', 'aguardando_revisao', 'aguardando_envio', 'concluido', 'erro')),
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
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS automacao_miller.report_recipients (
                    recipient_id BIGSERIAL PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    label TEXT,
                    active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_by TEXT NOT NULL,
                    updated_by TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS automacao_miller.document_recipients (
                    submission_id TEXT NOT NULL REFERENCES automacao_miller.documents(submission_id) ON DELETE CASCADE,
                    email TEXT NOT NULL,
                    position INTEGER NOT NULL CHECK (position > 0),
                    created_by TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (submission_id, email)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS automacao_miller.email_deliveries (
                    delivery_id BIGSERIAL PRIMARY KEY,
                    submission_id TEXT NOT NULL REFERENCES automacao_miller.documents(submission_id),
                    recipient_emails JSONB NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('solicitado', 'enviando', 'enviado', 'falhou')),
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    execution_id TEXT,
                    requested_by TEXT NOT NULL,
                    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    sent_at TIMESTAMPTZ,
                    error_message TEXT
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

    def list_documents(self, query: str = "", status: str | None = None, page: int = 1, page_size: int = 25, date_from: str | None = None, date_to: str | None = None) -> tuple[list[Submission], int]:
        conditions = ["TRUE"]
        params: list[Any] = []
        if query:
            conditions.append("(submission_id ILIKE %s OR source_filename ILIKE %s)")
            params.extend([f"%{query}%", f"%{query}%"])
        if status:
            conditions.append("status = %s")
            params.append(status)
        if date_from:
            conditions.append("created_at >= %s::timestamptz")
            params.append(date_from)
        if date_to:
            conditions.append("created_at < (%s::date + INTERVAL '1 day')")
            params.append(date_to)
        offset = (page - 1) * page_size
        params.extend([page_size, offset])
        sql = f"""
            SELECT submission_id, source_filename, source_sha256, size_bytes, status,
                   source_storage_key, report_storage_key, message, created_at, updated_at,
                   COUNT(*) OVER() AS total_count
            FROM automacao_miller.documents
            WHERE {' AND '.join(conditions)}
            ORDER BY updated_at DESC
            LIMIT %s OFFSET %s
        """
        with psycopg.connect(self.database_url) as connection:
            rows = connection.execute(sql, params).fetchall()
        total = int(rows[0][10]) if rows else 0
        return [self._row(row[:10]) for row in rows if self._row(row[:10])], total

    def detail(self, submission_id: str) -> dict[str, Any]:
        item = self.get(submission_id)
        if item is None:
            raise KeyError(submission_id)
        with psycopg.connect(self.database_url) as connection:
            artifacts = connection.execute(
                "SELECT artifact_id, artifact_type, version, storage_key, sha256, size_bytes, mime_type, created_at FROM automacao_miller.artifacts WHERE submission_id = %s ORDER BY artifact_type, version DESC",
                (submission_id,),
            ).fetchall()
            attempts = connection.execute(
                "SELECT attempt_id, attempt_number, execution_id, current_stage, status, error_category, error_message, started_at, finished_at FROM automacao_miller.processing_attempts WHERE submission_id = %s ORDER BY attempt_number DESC",
                (submission_id,),
            ).fetchall()
            errors = connection.execute(
                "SELECT id, current_stage, error_category, error_message, execution_id, created_at FROM automacao_miller.workflow_errors WHERE submission_id = %s ORDER BY created_at DESC",
                (submission_id,),
            ).fetchall()
            reviews = connection.execute(
                "SELECT review_id, reason, decision, reviewer, notes, requested_at, reviewed_at FROM automacao_miller.human_reviews WHERE submission_id = %s ORDER BY requested_at DESC",
                (submission_id,),
            ).fetchall()
            deliveries = connection.execute(
                "SELECT delivery_id, recipient_emails, status, attempt_count, execution_id, requested_by, requested_at, sent_at, error_message FROM automacao_miller.email_deliveries WHERE submission_id = %s ORDER BY requested_at DESC",
                (submission_id,),
            ).fetchall()
        iso = lambda value: value.isoformat() if isinstance(value, datetime) else value
        return {
            "submission": item,
            "artifacts": [dict(zip(("artifact_id", "artifact_type", "version", "storage_key", "sha256", "size_bytes", "mime_type", "created_at"), [*row[:7], iso(row[7])])) for row in artifacts],
            "attempts": [dict(zip(("attempt_id", "attempt_number", "execution_id", "current_stage", "status", "error_category", "error_message", "started_at", "finished_at"), [*row[:7], iso(row[7]), iso(row[8])])) for row in attempts],
            "errors": [dict(zip(("error_id", "current_stage", "error_category", "error_message", "execution_id", "created_at"), [*row[:5], iso(row[5])])) for row in errors],
            "reviews": [dict(zip(("review_id", "reason", "decision", "reviewer", "notes", "requested_at", "reviewed_at"), [*row[:5], iso(row[5]), iso(row[6])])) for row in reviews],
            "deliveries": [dict(zip(("delivery_id", "recipient_emails", "status", "attempt_count", "execution_id", "requested_by", "requested_at", "sent_at", "error_message"), [row[0], row[1], row[2], row[3], row[4], row[5], iso(row[6]), iso(row[7]), row[8]])) for row in deliveries],
        }

    def list_recipients(self) -> list[dict[str, Any]]:
        with psycopg.connect(self.database_url) as connection:
            rows = connection.execute(
                "SELECT recipient_id, email, label, active, created_by, updated_by, created_at, updated_at FROM automacao_miller.report_recipients ORDER BY active DESC, email"
            ).fetchall()
        return [dict(zip(("recipient_id", "email", "label", "active", "created_by", "updated_by", "created_at", "updated_at"), [*row[:6], row[6].isoformat(), row[7].isoformat()])) for row in rows]

    def replace_recipients(self, recipients: list[dict[str, Any]], actor: str) -> list[dict[str, Any]]:
        emails = [item["email"] for item in recipients]
        with psycopg.connect(self.database_url) as connection:
            for item in recipients:
                connection.execute(
                    "INSERT INTO automacao_miller.report_recipients (email, label, active, created_by, updated_by) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (email) DO UPDATE SET label = EXCLUDED.label, active = EXCLUDED.active, updated_by = EXCLUDED.updated_by, updated_at = NOW()",
                    (item["email"], item.get("label"), item.get("active", True), actor, actor),
                )
            connection.execute("UPDATE automacao_miller.report_recipients SET active = FALSE, updated_by = %s, updated_at = NOW() WHERE NOT (email = ANY(%s))", (actor, emails))
        return self.list_recipients()

    def set_document_recipients(self, submission_id: str, emails: list[str], actor: str) -> None:
        with psycopg.connect(self.database_url) as connection:
            connection.execute("DELETE FROM automacao_miller.document_recipients WHERE submission_id = %s", (submission_id,))
            for position, email in enumerate(emails, start=1):
                connection.execute("INSERT INTO automacao_miller.document_recipients (submission_id, email, position, created_by) VALUES (%s, %s, %s, %s)", (submission_id, email, position, actor))

    def get_document_recipients(self, submission_id: str) -> list[str]:
        with psycopg.connect(self.database_url) as connection:
            rows = connection.execute("SELECT email FROM automacao_miller.document_recipients WHERE submission_id = %s ORDER BY position", (submission_id,)).fetchall()
        return [row[0] for row in rows]

    def get_active_recipient_emails(self) -> list[str]:
        with psycopg.connect(self.database_url) as connection:
            rows = connection.execute("SELECT email FROM automacao_miller.report_recipients WHERE active = TRUE ORDER BY email").fetchall()
        return [row[0] for row in rows]

    def create_delivery(self, submission_id: str, emails: list[str], actor: str, retry: bool = False) -> dict[str, Any]:
        with psycopg.connect(self.database_url) as connection:
            document = connection.execute("SELECT status FROM automacao_miller.documents WHERE submission_id = %s FOR UPDATE", (submission_id,)).fetchone()
            if document is None:
                raise KeyError(submission_id)
            allowed = {"erro"} if retry else {"aguardando_envio"}
            if document[0] not in allowed:
                raise ValueError("status_invalido")
            pending = connection.execute("SELECT 1 FROM automacao_miller.email_deliveries WHERE submission_id = %s AND status IN ('solicitado', 'enviando') LIMIT 1", (submission_id,)).fetchone()
            if pending:
                raise ValueError("envio_em_andamento")
            row = connection.execute(
                "INSERT INTO automacao_miller.email_deliveries (submission_id, recipient_emails, status, requested_by) VALUES (%s, %s::jsonb, 'solicitado', %s) RETURNING delivery_id, submission_id, recipient_emails, status, attempt_count, requested_by, requested_at",
                (submission_id, json.dumps(emails), actor),
            ).fetchone()
        return dict(zip(("delivery_id", "submission_id", "recipient_emails", "status", "attempt_count", "requested_by", "requested_at"), [row[0], row[1], row[2], row[3], row[4], row[5], row[6].isoformat()]))

    def update_delivery(self, delivery_id: int, **changes: Any) -> dict[str, Any] | None:
        allowed = {"status", "attempt_count", "execution_id", "sent_at", "error_message"}
        changes = {key: value for key, value in changes.items() if key in allowed}
        if not changes:
            return None
        assignments = ", ".join(f"{key} = %s" for key in changes)
        with psycopg.connect(self.database_url) as connection:
            row = connection.execute(f"UPDATE automacao_miller.email_deliveries SET {assignments} WHERE delivery_id = %s RETURNING delivery_id, submission_id, recipient_emails, status, attempt_count, execution_id, requested_by, requested_at, sent_at, error_message", [*changes.values(), delivery_id]).fetchone()
        if row is None:
            return None
        return dict(zip(("delivery_id", "submission_id", "recipient_emails", "status", "attempt_count", "execution_id", "requested_by", "requested_at", "sent_at", "error_message"), [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7].isoformat(), row[8].isoformat() if row[8] else None, row[9]]))

    def add_review(self, submission_id: str, decision: str, notes: str, actor: str) -> dict[str, Any]:
        status = "aguardando_envio" if decision == "aprovado" else "recebido"
        stage = "revisao_liberada" if decision == "aprovado" else "reprocessamento_autorizado"
        with psycopg.connect(self.database_url) as connection:
            document = connection.execute("SELECT status FROM automacao_miller.documents WHERE submission_id = %s FOR UPDATE", (submission_id,)).fetchone()
            if document is None:
                raise KeyError(submission_id)
            row = connection.execute(
                "INSERT INTO automacao_miller.human_reviews (submission_id, reason, decision, reviewer, notes, reviewed_at) VALUES (%s, %s, %s, %s, %s, NOW()) RETURNING review_id, reason, decision, reviewer, notes, requested_at, reviewed_at",
                (submission_id, "revisão operacional", decision, actor, notes),
            ).fetchone()
            connection.execute("UPDATE automacao_miller.documents SET status = %s, current_stage = %s, message = NULL, updated_at = NOW() WHERE submission_id = %s", (status, stage, submission_id))
        return dict(zip(("review_id", "reason", "decision", "reviewer", "notes", "requested_at", "reviewed_at"), [row[0], row[1], row[2], row[3], row[4], row[5].isoformat(), row[6].isoformat()]))

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
        "n8n_email_webhook_url": os.getenv("N8N_REPORT_EMAIL_WEBHOOK_URL", "http://n8n:5678/webhook/automacao-regulatoria-send-report"),
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
        return FileResponse(STATIC_DIR / "dashboard.html")
    if _session_username(request):
        return RedirectResponse(url="/upload", status_code=303)
    return FileResponse(STATIC_DIR / "login.html")


@app.get("/upload", dependencies=[Depends(require_landing_access)])
def landing() -> FileResponse:
    return FileResponse(STATIC_DIR / "dashboard.html")


@app.get("/new", dependencies=[Depends(require_landing_access)])
def new_submission() -> FileResponse:
    return FileResponse(STATIC_DIR / "upload.html")


@app.get("/submissions/{submission_id}/view", dependencies=[Depends(require_landing_access)])
def submission_view(submission_id: str) -> FileResponse:
    if store.get(submission_id) is None:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado.")
    return FileResponse(STATIC_DIR / "submission.html")


@app.get("/settings/recipients", dependencies=[Depends(require_landing_access)])
def recipient_settings() -> FileResponse:
    return FileResponse(STATIC_DIR / "recipients.html")


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
        "sha256": item.sha256,
        "size_bytes": item.size_bytes,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "message": item.message,
    }


def actor_for(request: Request) -> str:
    return _session_username(request) or "token-user"


def serialize_detail(detail: dict[str, Any]) -> dict[str, Any]:
    return {
        "submission": public_submission(detail["submission"]),
        "artifacts": detail["artifacts"],
        "attempts": detail["attempts"],
        "errors": detail["errors"],
        "reviews": detail["reviews"],
        "deliveries": detail["deliveries"],
    }


def normalized_recipients(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw = payload.get("recipients", [])
    if not isinstance(raw, list) or len(raw) > MAX_RECIPIENTS:
        raise HTTPException(status_code=422, detail=f"Informe até {MAX_RECIPIENTS} destinatários.")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for value in raw:
        if isinstance(value, str):
            email = value.strip().lower()
            label = None
            active = True
        elif isinstance(value, dict):
            email = str(value.get("email", "")).strip().lower()
            label = str(value.get("label", "")).strip() or None
            active = bool(value.get("active", True))
        else:
            raise HTTPException(status_code=422, detail="Destinatário inválido.")
        parsed = parseaddr(email)[1]
        if not parsed or parsed != email or not EMAIL_RE.fullmatch(email):
            raise HTTPException(status_code=422, detail=f"E-mail inválido: {email or 'vazio'}.")
        if email in seen:
            continue
        seen.add(email)
        normalized.append({"email": email, "label": label, "active": active})
    return normalized


def artifact_for(detail: dict[str, Any], artifact_type: str) -> dict[str, Any]:
    if artifact_type not in ARTIFACT_TYPES:
        raise HTTPException(status_code=404, detail="Artefato não encontrado.")
    artifact = next((item for item in detail["artifacts"] if item["artifact_type"] == artifact_type), None)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artefato não encontrado.")
    return artifact


def dispatch_webhook(url: str, payload: dict[str, Any]) -> None:
    if not url:
        return
    try:
        response = httpx.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="Não foi possível despachar a operação ao n8n.") from exc


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


@app.get("/api/v1/submissions", dependencies=[Depends(require_landing_access)])
def list_submissions(q: str = "", status: str | None = None, page: int = 1, page_size: int = 25, date_from: str | None = None, date_to: str | None = None) -> dict[str, Any]:
    if status is not None and status not in STATUSES:
        raise HTTPException(status_code=422, detail="Status inválido.")
    page = max(1, min(page, 10_000))
    page_size = max(1, min(page_size, 100))
    items, total = store.list_documents(q, status, page, page_size, date_from, date_to)
    return {"items": [public_submission(item) for item in items], "total": total, "page": page, "page_size": page_size}


@app.get("/api/v1/submissions/{submission_id}", dependencies=[Depends(require_landing_access)])
def get_submission(submission_id: str) -> dict[str, Any]:
    item = store.get(submission_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado.")
    return {**public_submission(item), **serialize_detail(store.detail(submission_id))}


@app.get("/api/v1/submissions/{submission_id}/artifacts", dependencies=[Depends(require_landing_access)])
def list_artifacts(submission_id: str) -> dict[str, Any]:
    item = store.get(submission_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado.")
    return {"items": store.detail(submission_id)["artifacts"]}


@app.get("/api/v1/submissions/{submission_id}/artifacts/{artifact_type}", dependencies=[Depends(require_landing_access)])
def view_artifact(submission_id: str, artifact_type: str, disposition: str = "inline") -> Response:
    if disposition not in {"inline", "download"}:
        raise HTTPException(status_code=422, detail="Disposição de arquivo inválida.")
    if store.get(submission_id) is None:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado.")
    detail = store.detail(submission_id)
    artifact = artifact_for(detail, artifact_type)
    try:
        path = resolve_storage_key(artifact["storage_key"])
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Artefato não encontrado.") from exc
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Artefato não encontrado.")
    filename = Path(artifact["storage_key"]).name
    content_disposition = "attachment" if disposition == "download" else "inline"
    if artifact_type in {"original_pdf", "report_pdf"}:
        return Response(path.read_bytes(), media_type="application/pdf", headers={"Content-Disposition": f'{content_disposition}; filename="{filename}"'})
    if artifact_type == "analysis_json":
        try:
            content = json.dumps(json.loads(path.read_text(encoding="utf-8")), ensure_ascii=False, indent=2)
        except (OSError, ValueError) as exc:
            raise HTTPException(status_code=422, detail="JSON da análise inválido.") from exc
        return Response(content, media_type="application/json", headers={"Content-Disposition": f'{content_disposition}; filename="{filename}"'})
    return Response(path.read_text(encoding="utf-8"), media_type="text/markdown", headers={"Content-Disposition": f'{content_disposition}; filename="{filename}"'})


@app.get("/api/v1/settings/report-recipients", dependencies=[Depends(require_landing_access)])
def get_report_recipients() -> dict[str, Any]:
    return {"items": store.list_recipients()}


@app.put("/api/v1/settings/report-recipients", dependencies=[Depends(require_landing_access)])
def replace_report_recipients(payload: dict[str, Any], request: Request) -> dict[str, Any]:
    recipients = normalized_recipients(payload)
    return {"items": store.replace_recipients(recipients, actor_for(request))}


def _requested_emails(submission_id: str, payload: dict[str, Any]) -> list[str]:
    if "recipients" in payload:
        emails = [item["email"] for item in normalized_recipients(payload) if item["active"]]
        return emails
    document_emails = store.get_document_recipients(submission_id)
    return document_emails or store.get_active_recipient_emails()


def _request_report_send(submission_id: str, payload: dict[str, Any], request: Request, retry: bool = False) -> JSONResponse:
    item = store.get(submission_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado.")
    emails = _requested_emails(submission_id, payload)
    if not emails:
        raise HTTPException(status_code=422, detail="Cadastre ou informe ao menos um destinatário ativo.")
    if "recipients" in payload:
        store.set_document_recipients(submission_id, emails, actor_for(request))
    try:
        delivery = store.create_delivery(submission_id, emails, actor_for(request), retry=retry)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado.") from exc
    except ValueError as exc:
        detail = "Já existe um envio em andamento." if str(exc) == "envio_em_andamento" else "O documento não está pronto para envio."
        raise HTTPException(status_code=409, detail=detail) from exc
    try:
        dispatch_webhook(settings()["n8n_email_webhook_url"], {"submission_id": submission_id, "delivery_id": delivery["delivery_id"]})
    except HTTPException:
        store.update_delivery(delivery["delivery_id"], status="falhou", error_message="Não foi possível despachar o envio ao n8n.")
        store.update(submission_id, status="erro", message="Falha ao iniciar o envio do relatório.")
        raise
    return JSONResponse(status_code=202, content={"delivery": delivery, "submission": public_submission(store.get(submission_id) or item)})


@app.post("/api/v1/submissions/{submission_id}/send-report", dependencies=[Depends(require_landing_access)])
def send_report(submission_id: str, payload: dict[str, Any], request: Request) -> JSONResponse:
    return _request_report_send(submission_id, payload, request)


@app.post("/api/v1/submissions/{submission_id}/retry-email", dependencies=[Depends(require_landing_access)])
def retry_email(submission_id: str, payload: dict[str, Any], request: Request) -> JSONResponse:
    return _request_report_send(submission_id, payload, request, retry=True)


@app.post("/api/v1/submissions/{submission_id}/review", dependencies=[Depends(require_landing_access)])
def review_submission(submission_id: str, payload: dict[str, Any], request: Request) -> dict[str, Any]:
    item = store.get(submission_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado.")
    if item.status != "aguardando_revisao":
        raise HTTPException(status_code=409, detail="O documento não está aguardando revisão.")
    decision = payload.get("decision")
    notes = str(payload.get("notes", "")).strip()
    if decision not in {"liberar_envio", "reprocessar"}:
        raise HTTPException(status_code=422, detail="Decisão de revisão inválida.")
    if not notes:
        raise HTTPException(status_code=422, detail="Informe uma observação para registrar a revisão.")
    stored_decision = "aprovado" if decision == "liberar_envio" else "reprocessamento_autorizado"
    review = store.add_review(submission_id, stored_decision, notes, actor_for(request))
    if decision == "reprocessar":
        try:
            dispatch_webhook(settings()["n8n_webhook_url"], {"submission_id": submission_id, "source": "human_review"})
        except HTTPException:
            store.update(submission_id, message="Reprocessamento autorizado; aguardando despacho para o n8n.")
            raise
    return {"review": review, "submission": public_submission(store.get(submission_id) or item)}


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
