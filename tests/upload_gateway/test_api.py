from pathlib import Path

from fastapi.testclient import TestClient

from infra.upload_gateway import app as gateway


def make_client(tmp_path: Path) -> TestClient:
    gateway.store = gateway.InMemoryStore()
    gateway.store.initialize()
    gateway.os.environ["LANDING_ACCESS_TOKEN"] = "landing-test"
    gateway.os.environ["INTERNAL_API_TOKEN"] = "internal-test"
    gateway.os.environ.pop("N8N_SUBMISSION_WEBHOOK_URL", None)
    gateway.os.environ["UPLOAD_STORAGE_DIR"] = str(tmp_path)
    return TestClient(gateway.app)


def test_landing_requires_private_token(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    assert client.get("/").status_code == 403
    response = client.post("/api/v1/submissions", files={"file": ("a.pdf", b"%PDF-1.7 test", "application/pdf")})
    assert response.status_code == 403


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
    report = tmp_path / "report.pdf"
    report.write_bytes(b"%PDF-1.7 report")
    updated = client.post(
        f"/internal/submissions/{created['submission_id']}/status",
        headers={"X-Internal-Token": "internal-test"},
        json={"status": "concluido", "report_path": str(report)},
    )
    assert updated.status_code == 200
    downloaded = client.get(f"/api/v1/submissions/{created['submission_id']}/report", headers=headers)
    assert downloaded.status_code == 200
    assert downloaded.content == b"%PDF-1.7 report"


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
