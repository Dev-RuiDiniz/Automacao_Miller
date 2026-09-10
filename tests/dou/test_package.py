import json
import zipfile
from pathlib import Path

from infra.dou.package import batch_name, build_consolidated_markdown, create_package


def test_batch_windows_are_weekly_from_collection_start() -> None:
    assert batch_name("2026-08-12", "2026-08-12") == "lote-01"
    assert batch_name("2026-08-19", "2026-08-12") == "lote-02"
    assert batch_name("2026-09-10", "2026-08-12") == "lote-05"


def test_consolidated_report_keeps_source_pages_and_hashes() -> None:
    manifest = {"period": {"start": "2026-08-12", "end": "2026-09-10"}, "items": [{"publication_date": "2026-08-12", "kind": "pdf", "section": "do1", "status": "downloaded", "filename": "dou.pdf", "submission_id": "dou-2026-08-12-do1", "sha256": "a" * 64}]}
    analyses = {"dou-2026-08-12-do1": {"analysis": {"outros_atos": [{"paginas_origem": [71], "evidencia": "Ato publicado", "status": "outro"}], "avisos": [], "revisao_humana": {"necessaria": False}}}}
    report = build_consolidated_markdown(manifest, analyses)
    assert "p. 71" in report
    assert "a" * 64 in report


def test_package_contains_only_reports_manifest_and_checksums(tmp_path: Path) -> None:
    staging = tmp_path / "staging"
    (staging / "analyses").mkdir(parents=True)
    manifest = {"schema_version": "dou-corpus-v1", "source": "INLABS", "period": {"start": "2026-08-12", "end": "2026-09-10"}, "items": [{"publication_date": "2026-08-12", "kind": "pdf", "section": "do1", "status": "downloaded", "filename": "dou.pdf", "submission_id": "dou-2026-08-12-do1", "sha256": "a" * 64}]}
    (staging / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    output = tmp_path / "package"
    zip_path = create_package(staging, output)
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
    assert "relatorio-consolidado.md" in names
    assert "manifest.json" in names
    assert "checksums.sha256" in names
    assert all(not name.endswith(".pdf") or name.startswith("relatorios-pdf/") for name in names)
