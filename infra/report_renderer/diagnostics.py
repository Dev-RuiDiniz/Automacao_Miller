"""Diagnósticos documentais privados, separados de logs e relatórios finais."""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

DIAGNOSTICS_DIR = Path("/data/diagnostics")


class DiagnosticStorageError(OSError):
    pass


def diagnostic_context(value) -> dict:
    if value is None:
        return {}
    if (not isinstance(value, dict)
            or set(value) != {"submission_id", "attempt_number", "execution_id"}
            or type(value["attempt_number"]) is not int or value["attempt_number"] < 1
            or any(not isinstance(value[key], str)
                   or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value[key])
                   for key in ("submission_id", "execution_id"))):
        raise ValueError("Contexto de diagnóstico inválido.")
    return dict(value)


class DiagnosticWriter:
    def __init__(self, source_sha256: str, context: dict):
        self.context = diagnostic_context(context) if context else {}
        self.source_sha256 = source_sha256
        self.run_id = uuid.uuid4().hex
        if not re.fullmatch(r"[a-f0-9]{64}", source_sha256):
            raise ValueError("Hash da fonte de diagnóstico inválido.")
        attempt = self.context.get("attempt_number", "avulsa")
        self.directory = DIAGNOSTICS_DIR / source_sha256 / f"tentativa-{attempt}" / self.run_id
        try:
            self.directory.mkdir(parents=True, mode=0o700)
            # Os diretórios intermediários também contêm material documental privado.
            for directory in (self.directory.parent, self.directory.parent.parent, DIAGNOSTICS_DIR):
                directory.chmod(0o700)
        except OSError:
            raise DiagnosticStorageError("Não foi possível preparar o diagnóstico privado.") from None

    def __call__(self, diagnostic: dict) -> str:
        reference = "ANV8D-" + uuid.uuid4().hex
        path = self.directory / (reference + ".json")
        document = {
            **diagnostic,
            "schema_version": 1, "diagnostic_id": reference, "run_id": self.run_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source_markdown_sha256": self.source_sha256,
            "context": self.context,
        }
        try:
            raw = json.dumps(document, ensure_ascii=False, allow_nan=False, indent=2).encode("utf-8")
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
        except (OSError, ValueError, TypeError):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
            raise DiagnosticStorageError("Não foi possível preservar o diagnóstico privado.") from None
        return reference
