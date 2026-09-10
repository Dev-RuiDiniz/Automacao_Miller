from __future__ import annotations

import hashlib
import json
import os
import random
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


DEFAULT_LOGIN_URL = "https://inlabs.in.gov.br/logar.php"
DEFAULT_DOWNLOAD_URL = "https://inlabs.in.gov.br/index.php?p="
DEFAULT_PDF_TYPES = ("do1", "do2", "do3")
DEFAULT_XML_TYPES = ("DO1", "DO2", "DO3", "DO1E", "DO2E", "DO3E")


class DouCollectorError(RuntimeError):
    pass


@dataclass(frozen=True)
class DouRequest:
    publication_date: str
    kind: str
    section: str
    filename: str
    url: str


def date_range(start: date, end: date) -> list[date]:
    if end < start:
        raise ValueError("a data final não pode ser anterior à inicial")
    return [start + timedelta(days=offset) for offset in range((end - start).days + 1)]


def build_requests(start: date, end: date, pdf_types: Iterable[str] = DEFAULT_PDF_TYPES, xml_types: Iterable[str] = DEFAULT_XML_TYPES, download_url: str = DEFAULT_DOWNLOAD_URL) -> list[DouRequest]:
    requests: list[DouRequest] = []
    for current in date_range(start, end):
        iso_date = current.isoformat()
        compact = current.strftime("%Y_%m_%d")
        for section in pdf_types:
            name = f"{compact}_ASSINADO_{section}.pdf"
            url = f"{download_url}{iso_date}&dl={urllib.parse.quote(name)}"
            requests.append(DouRequest(iso_date, "pdf", section, name, url))
        for section in xml_types:
            name = f"{iso_date}-{section}.zip"
            url = f"{download_url}{iso_date}&dl={urllib.parse.quote(name)}"
            requests.append(DouRequest(iso_date, "xml", section, name, url))
    return requests


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _valid_download(path: Path, kind: str) -> bool:
    if not path.is_file() or path.stat().st_size == 0:
        return False
    with path.open("rb") as handle:
        header = handle.read(4)
    return header == (b"%PDF" if kind == "pdf" else b"PK\x03\x04")


class DouCollector:
    def __init__(self, output_dir: Path, email: str | None = None, password: str | None = None, login_url: str = DEFAULT_LOGIN_URL, download_url: str = DEFAULT_DOWNLOAD_URL, timeout: int = 60, retries: int = 3, delay_seconds: float = 1.0) -> None:
        self.output_dir = output_dir
        self.email = email or os.getenv("DOU_INLABS_EMAIL")
        self.password = password or os.getenv("DOU_INLABS_PASSWORD")
        self.login_url = login_url
        self.download_url = download_url
        self.timeout = timeout
        self.retries = retries
        self.delay_seconds = delay_seconds
        self.cookie_jar = urllib.request.HTTPCookieProcessor()
        self.opener = urllib.request.build_opener(self.cookie_jar)

    def _login(self) -> None:
        if not self.email or not self.password:
            raise DouCollectorError("Configure DOU_INLABS_EMAIL e DOU_INLABS_PASSWORD no ambiente protegido.")
        payload = urllib.parse.urlencode({"email": self.email, "password": self.password}).encode()
        request = urllib.request.Request(self.login_url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "text/html,application/xhtml+xml"})
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                response.read(1024)
        except urllib.error.URLError as exc:
            raise DouCollectorError("Não foi possível autenticar no INLABS.") from exc
        if not any(cookie.name == "inlabs_session_cookie" for cookie in self.cookie_jar.cookiejar):
            raise DouCollectorError("O INLABS não retornou uma sessão; verifique as credenciais.")

    def _download_one(self, request_info: DouRequest, manifest_item: dict[str, Any]) -> dict[str, Any]:
        target = self.output_dir / "raw" / request_info.publication_date / request_info.kind / request_info.filename
        target.parent.mkdir(parents=True, exist_ok=True)
        if _valid_download(target, request_info.kind):
            manifest_item.update({"status": "downloaded", "path": str(target.relative_to(self.output_dir)).replace("\\", "/"), "size_bytes": target.stat().st_size, "sha256": sha256_file(target)})
            return manifest_item
        temp = target.with_suffix(target.suffix + ".part")
        last_error = "indisponibilidade não especificada"
        headers = {"origem": "736372697074", "Accept": "application/octet-stream"}
        for attempt in range(1, self.retries + 1):
            try:
                req = urllib.request.Request(request_info.url, headers=headers)
                with self.opener.open(req, timeout=self.timeout) as response, temp.open("wb") as handle:
                    while True:
                        block = response.read(1024 * 1024)
                        if not block:
                            break
                        handle.write(block)
                if not _valid_download(temp, request_info.kind):
                    raise DouCollectorError("resposta não é um PDF/ZIP válido")
                temp.replace(target)
                manifest_item.update({"status": "downloaded", "path": str(target.relative_to(self.output_dir)).replace("\\", "/"), "size_bytes": target.stat().st_size, "sha256": sha256_file(target), "attempts": attempt})
                return manifest_item
            except urllib.error.HTTPError as exc:
                last_error = f"HTTP {exc.code}"
                if exc.code == 404:
                    manifest_item.update({"status": "missing", "http_status": exc.code, "error": "edição não disponibilizada para esta data/seção"})
                    return manifest_item
                if exc.code not in {429, 500, 502, 503, 504}:
                    break
            except (urllib.error.URLError, OSError, DouCollectorError) as exc:
                last_error = str(exc)
            if temp.exists():
                temp.unlink()
            time.sleep(self.delay_seconds * attempt + random.random() * 0.25)
        manifest_item.update({"status": "error", "error": last_error, "attempts": self.retries})
        return manifest_item

    def collect(self, start: date, end: date, pdf_types: Iterable[str] = DEFAULT_PDF_TYPES, xml_types: Iterable[str] = DEFAULT_XML_TYPES, dry_run: bool = False) -> dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        requests = build_requests(start, end, pdf_types, xml_types, self.download_url)
        items = [{**asdict(item), "status": "planned"} for item in requests]
        if not dry_run:
            self._login()
            for item, request_info in zip(items, requests):
                self._download_one(request_info, item)
                time.sleep(self.delay_seconds)
        manifest = {"schema_version": "dou-corpus-v1", "source": "INLABS / Imprensa Nacional", "period": {"start": start.isoformat(), "end": end.isoformat()}, "generated_at": datetime.now(timezone.utc).isoformat(), "items": items}
        manifest["counts"] = {status: sum(1 for item in items if item["status"] == status) for status in {item["status"] for item in items}}
        manifest_path = self.output_dir / "manifest.json"
        temp_manifest = manifest_path.with_suffix(".json.part")
        temp_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temp_manifest.replace(manifest_path)
        return manifest
