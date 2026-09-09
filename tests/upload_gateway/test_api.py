import os
from pathlib import Path

from fastapi.testclient import TestClient

from infra.upload_gateway import app as gateway


def make_client(tmp_path: Path) -> TestClient:
    gateway.store = gateway.InMemoryStore()
    gateway.store.initialize()
    gateway.os.environ["LANDING_ACCESS_TOKEN"] = "landing-test"
    gateway.os.environ["INTERNAL_API_TOKEN"] = "internal-test"
    gateway.os.environ["LANDING_USERNAME"] = "operador"
    gateway.os.environ["LANDING_PASSWORD_HASH"] = gateway.hash_password("senha-teste")
    gateway.os.environ["AUTH_SESSION_SECRET"] = "session-secret-test"
    gateway.os.environ["AUTH_SESSION_TTL_SECONDS"] = "3600"
    gateway.os.environ["SESSION_COOKIE_SECURE"] = "false"
    gateway.os.environ.pop("N8N_SUBMISSION_WEBHOOK_URL", None)
    gateway.os.environ["ARTIFACT_STORAGE_DIR"] = str(tmp_path)
    return TestClient(gateway.app)


def test_landing_requires_private_token(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    assert client.get("/").status_code == 200
    assert client.get("/upload").status_code == 403
    response = client.post("/api/v1/submissions", files={"file": ("a.pdf", b"%PDF-1.7 test", "application/pdf")})
    assert response.status_code == 403


def test_login_creates_session_and_unlocks_upload(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    invalid = client.post("/auth/login", json={"username": "operador", "password": "errada"})
    assert invalid.status_code == 401
    login = client.post("/auth/login", json={"username": "operador", "password": "senha-teste"})
    assert login.status_code == 200
    assert login.json() == {"ok": True, "redirect": "/upload"}
    assert "HttpOnly" in login.headers["set-cookie"]
    assert "SameSite=lax" in login.headers["set-cookie"]
    assert client.get("/upload").status_code == 200


def test_login_reports_missing_configuration(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    monkeypatch.delenv("LANDING_PASSWORD_HASH")
    response = client.post("/auth/login", json={"username": "operador", "password": "senha-teste"})
    assert response.status_code == 503


def test_logout_removes_session(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    client.post("/auth/login", json={"username": "operador", "password": "senha-teste"})
    assert client.get("/upload").status_code == 200
    assert client.post("/auth/logout").status_code == 200
    assert client.get("/upload").status_code == 403


def test_expired_session_is_rejected(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    client.post("/auth/login", json={"username": "operador", "password": "senha-teste"})
    original_time = gateway.time.time
    monkeypatch.setattr(gateway.time, "time", lambda: original_time() + gateway.session_ttl_seconds() + 1)
    assert client.get("/upload").status_code == 403


def test_legacy_token_still_unlocks_upload(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    assert client.get("/?token=landing-test").status_code == 200
    assert client.get("/upload?token=landing-test").status_code == 200


def test_upload_returns_protocol_and_status(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    response = client.post(
        "/api/v1/submissions",
        headers={"X-Landing-Token": "landing-test"},
        files={"file": ("referencia.pdf", b"%PDF-1.7 test", "application/pdf")},
    )
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "recebido"
    assert body["filename"] == "referencia.pdf"
    status = client.get(f"/api/v1/submissions/{body['submission_id']}", headers={"X-Landing-Token": "landing-test"})
    assert status.status_code == 200
    assert status.json()["submission_id"] == body["submission_id"]


def test_upload_rejects_non_pdf_and_oversized_pdf(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    headers = {"X-Landing-Token": "landing-test"}
    non_pdf = client.post("/api/v1/submissions", headers=headers, files={"file": ("arquivo.txt", b"%PDF-", "text/plain")})
    assert non_pdf.status_code == 415
    monkeypatch.setattr(gateway, "MAX_PDF_BYTES", 4)
    oversized = client.post("/api/v1/submissions", headers=headers, files={"file": ("arquivo.pdf", b"%PDF-", "application/pdf")})
    assert oversized.status_code == 413


def test_duplicate_hash_returns_existing_protocol(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    headers = {"X-Landing-Token": "landing-test"}
    payload = {"file": ("a.pdf", b"%PDF-1.7 same", "application/pdf")}
    first = client.post("/api/v1/submissions", headers=headers, files=payload)
    second = client.post("/api/v1/submissions", headers=headers, files=payload)
    assert first.status_code == 202
    assert second.status_code == 200
    assert second.json()["submission_id"] == first.json()["submission_id"]


def test_report_is_only_available_after_completion(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    headers = {"X-Landing-Token": "landing-test"}
    created = client.post("/api/v1/submissions", headers=headers, files={"file": ("a.pdf", b"%PDF-1.7", "application/pdf")}).json()
    unavailable = client.get(f"/api/v1/submissions/{created['submission_id']}/report", headers=headers)
    assert unavailable.status_code == 409
    report = tmp_path / "objects" / "aa" / "bb" / "report" / "report-v1.pdf"
    report.parent.mkdir(parents=True)
    report.write_bytes(b"%PDF-1.7 report")
    report_key = str(report.relative_to(tmp_path)).replace("\\", "/")
    updated = client.post(
        f"/internal/submissions/{created['submission_id']}/status",
        headers={"X-Internal-Token": "internal-test"},
        json={"status": "concluido", "report_key": report_key},
    )
    assert updated.status_code == 200
    downloaded = client.get(f"/api/v1/submissions/{created['submission_id']}/report", headers=headers)
    assert downloaded.status_code == 200
    assert downloaded.content == b"%PDF-1.7 report"


def test_upload_uses_hash_based_private_storage(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    headers = {"X-Landing-Token": "landing-test"}
    response = client.post(
        "/api/v1/submissions",
        headers=headers,
        files={"file": ("referencia.pdf", b"%PDF-1.7 hash-layout", "application/pdf")},
    )
    assert response.status_code == 202
    source_files = list((tmp_path / "objects").rglob("original.pdf"))
    assert len(source_files) == 1
    if os.name != "nt":
        assert source_files[0].stat().st_mode & 0o777 == 0o660


def test_report_rejects_absolute_storage_path(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    headers = {"X-Landing-Token": "landing-test"}
    created = client.post(
        "/api/v1/submissions",
        headers=headers,
        files={"file": ("a.pdf", b"%PDF-1.7", "application/pdf")},
    ).json()
    response = client.post(
        f"/internal/submissions/{created['submission_id']}/status",
        headers={"X-Internal-Token": "internal-test"},
        json={"status": "concluido", "report_key": str(tmp_path / "report.pdf")},
    )
    assert response.status_code == 422


def test_internal_status_rejects_invalid_token_and_status(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    denied = client.post("/internal/submissions/id/status", json={"status": "erro"})
    assert denied.status_code == 403
    invalid = client.post(
        "/internal/submissions/id/status",
        headers={"X-Internal-Token": "internal-test"},
        json={"status": "desconhecido"},
    )
    assert invalid.status_code == 422
