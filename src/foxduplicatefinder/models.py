from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class FileRecord:
    path: Path
    size: int
    mtime_ns: int
    sha256: str | None = None


@dataclass(slots=True)
class DuplicateGroup:
    key: str
    files: list[Path]
    total_size: int
