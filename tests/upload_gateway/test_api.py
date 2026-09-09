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


def test_operational_pages_require_session_or_private_token(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    for path in ("/upload", "/new", "/settings/recipients"):
        assert client.get(path).status_code == 403
    headers = {"X-Landing-Token": "landing-test"}
    for path in ("/upload", "/new", "/settings/recipients"):
        assert client.get(path, headers=headers).status_code == 200


def test_queue_detail_and_internal_artifact_viewers(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    headers = {"X-Landing-Token": "landing-test"}
    created = client.post("/api/v1/submissions", headers=headers, files={"file": ("a.pdf", b"%PDF-1.7", "application/pdf")}).json()
    submission_id = created["submission_id"]
    markdown = tmp_path / "objects" / "aa" / "bb" / "markdown-v1.md"
    analysis = tmp_path / "objects" / "aa" / "bb" / "analysis-v1.json"
    markdown.parent.mkdir(parents=True)
    markdown.write_text("# Evidência", encoding="utf-8")
    analysis.write_text('{"confidence": 0.91}', encoding="utf-8")
    gateway.store.artifacts[submission_id].extend([
        {"artifact_id": 2, "artifact_type": "markdown", "version": 1, "storage_key": str(markdown.relative_to(tmp_path)).replace("\\", "/"), "sha256": "a" * 64, "size_bytes": markdown.stat().st_size, "mime_type": "text/markdown", "created_at": gateway.now()},
        {"artifact_id": 3, "artifact_type": "analysis_json", "version": 1, "storage_key": str(analysis.relative_to(tmp_path)).replace("\\", "/"), "sha256": "b" * 64, "size_bytes": analysis.stat().st_size, "mime_type": "application/json", "created_at": gateway.now()},
    ])
    queue = client.get("/api/v1/submissions", headers=headers)
    assert queue.status_code == 200 and queue.json()["total"] == 1
    detail = client.get(f"/api/v1/submissions/{submission_id}", headers=headers)
    assert detail.status_code == 200 and len(detail.json()["artifacts"]) == 3
    assert client.get(f"/api/v1/submissions/{submission_id}/artifacts/markdown", headers=headers).text == "# Evidência"
    assert client.get(f"/api/v1/submissions/{submission_id}/artifacts/analysis_json", headers=headers).json()["confidence"] == 0.91
    assert client.get(f"/submissions/{submission_id}/view", headers=headers).status_code == 200


def test_recipients_are_validated_deduplicated_and_used_for_manual_send(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    headers = {"X-Landing-Token": "landing-test"}
    saved = client.put("/api/v1/settings/report-recipients", headers=headers, json={"recipients": ["OPS@EXAMPLE.COM", "ops@example.com", {"email": "review@example.com", "label": "Revisão"}]})
    assert saved.status_code == 200
    assert [item["email"] for item in saved.json()["items"]] == ["ops@example.com", "review@example.com"]
    assert client.put("/api/v1/settings/report-recipients", headers=headers, json={"recipients": ["invalid"]}).status_code == 422
    created = client.post("/api/v1/submissions", headers=headers, files={"file": ("a.pdf", b"%PDF-1.7", "application/pdf")}).json()
    submission_id = created["submission_id"]
    gateway.store.update(submission_id, status="aguardando_envio")
    monkeypatch.setattr(gateway, "dispatch_webhook", lambda *_args, **_kwargs: None)
    sent = client.post(f"/api/v1/submissions/{submission_id}/send-report", headers=headers, json={"recipients": ["custom@example.com", "CUSTOM@example.com"]})
    assert sent.status_code == 202
    assert sent.json()["delivery"]["recipient_emails"] == ["custom@example.com"]
    assert client.post(f"/api/v1/submissions/{submission_id}/send-report", headers=headers, json={"recipients": ["custom@example.com"]}).status_code == 409


def test_human_review_can_release_or_request_reprocessing(tmp_path: Path, monkeypatch) -> None:
    client = make_client(tmp_path)
    headers = {"X-Landing-Token": "landing-test"}
    created = client.post("/api/v1/submissions", headers=headers, files={"file": ("a.pdf", b"%PDF-1.7", "application/pdf")}).json()
    submission_id = created["submission_id"]
    gateway.store.update(submission_id, status="aguardando_revisao")
    monkeypatch.setattr(gateway, "dispatch_webhook", lambda *_args, **_kwargs: None)
    response = client.post(f"/api/v1/submissions/{submission_id}/review", headers=headers, json={"decision": "liberar_envio", "notes": "Evidências conferidas."})
    assert response.status_code == 200
    assert response.json()["submission"]["status"] == "aguardando_envio"
    assert client.post(f"/api/v1/submissions/{submission_id}/review", headers=headers, json={"decision": "reprocessar", "notes": ""}).status_code == 409
