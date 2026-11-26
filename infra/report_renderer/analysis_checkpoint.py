"""Estado privado da análise V8, com troca atômica e exclusão entre execuções."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import tempfile
from pathlib import Path

CHECKPOINTS_DIR = Path("/data/diagnostics/checkpoints")
MAX_BYTES = 128 * 1024 * 1024


class CheckpointStorageError(OSError):
    pass


class CheckpointBusyError(Exception):
    pass


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def write_atomically(path: Path, data: bytes):
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.stem}-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        try:
            Path(temporary).unlink(missing_ok=True)
        except OSError:
            pass


class AnalysisCheckpoint:
    def __init__(self, identity: dict, scope: str, *, save_parts=None):
        self.identity = {**identity, "scope": scope}
        self.key = hashlib.sha256(encode({"identity": identity, "scope": scope})).hexdigest()
        self.directory = CHECKPOINTS_DIR / self.key
        self.path = self.directory / "state.json"
        self.lock = None
        self.save_parts = save_parts

    def __enter__(self):
        try:
            self.directory.mkdir(parents=True, mode=0o700, exist_ok=True)
            CHECKPOINTS_DIR.chmod(0o700)
            self.directory.chmod(0o700)
            self.lock = os.open(self.directory / "lock", os.O_CREAT | os.O_RDWR, 0o600)
            try:
                fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise CheckpointBusyError("Já existe uma análise desta fonte em execução.") from None
            return self
        except (OSError, CheckpointBusyError) as exc:
            self.__exit__(None, None, None)
            if isinstance(exc, CheckpointBusyError):
                raise
            raise CheckpointStorageError("Não foi possível abrir o checkpoint privado.") from None

    def __exit__(self, *_):
        if self.lock is not None:
            os.close(self.lock)
            self.lock = None

    def load(self):
        try:
            if self.lock is None:
                raise ValueError
            if not self.path.exists():
                if os.fstat(self.lock).st_size:
                    raise ValueError
                return None
            if self.path.stat().st_size > MAX_BYTES:
                raise ValueError
            data = json.loads(self.path.read_bytes())
            if (data["identity"] != self.identity
                    or data["sha256"] != hashlib.sha256(encode(data["state"])).hexdigest()):
                raise ValueError
            return data["state"]
        except (OSError, ValueError, KeyError, TypeError, RecursionError):
            raise CheckpointStorageError("Checkpoint privado ausente, inválido ou divergente.") from None

    def save(self, state):
        try:
            if self.lock is None:
                raise ValueError
            data = encode({"identity": self.identity, "state": state,
                           "sha256": hashlib.sha256(encode(state)).hexdigest()})
            if len(data) > MAX_BYTES:
                raise ValueError
            write_atomically(self.path, data)
            # Marca que já houve estado persistido; sua remoção não é um início novo.
            os.pwrite(self.lock, b"1", 0)
            os.fsync(self.lock)
            if self.save_parts is not None:
                self.save_parts(self.directory, state)
        except (OSError, ValueError, TypeError, RecursionError):
            raise CheckpointStorageError("Não foi possível preservar o checkpoint privado.") from None
