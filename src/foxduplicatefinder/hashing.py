from __future__ import annotations

import hashlib
from pathlib import Path

try:
    import blake3 as _blake3
except Exception:  # pragma: no cover
    _blake3 = None


CHUNK_SIZE = 1024 * 1024


def hash_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            h.update(chunk)
    return h.hexdigest()


def hash_blake3(path: Path) -> str | None:
    if _blake3 is None:
        return None
    h = _blake3.blake3()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            h.update(chunk)
    return h.hexdigest()


def combined_content_hash(path: Path) -> str:
    """Stable combined hash pipeline.

    Format:
      blake3:<hex> if blake3 is available
      sha256:<hex> fallback otherwise
    """
    b3 = hash_blake3(path)
    if b3:
        return f"blake3:{b3}"
    return f"sha256:{hash_sha256(path)}"
