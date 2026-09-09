from __future__ import annotations

import os
from pathlib import Path


def storage_root() -> Path:
    return Path(os.getenv("ARTIFACT_STORAGE_DIR", "/data/artifacts")).resolve()


def object_prefix(sha256: str) -> str:
    normalized = sha256.strip().lower()
    if len(normalized) != 64 or any(char not in "0123456789abcdef" for char in normalized):
        raise ValueError("SHA-256 inválido")
    return f"objects/{normalized[:2]}/{normalized[2:4]}/{normalized}"


def original_key(sha256: str) -> str:
    return f"{object_prefix(sha256)}/original.pdf"


def resolve_storage_key(key: str) -> Path:
    raw = str(key or "").replace("\\", "/")
    candidate = Path(raw)
    if not raw or candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("chave de armazenamento inválida")
    root = storage_root()
    resolved = (root / candidate).resolve()
    if root != resolved and root not in resolved.parents:
        raise ValueError("chave fora do volume de artefatos")
    return resolved
