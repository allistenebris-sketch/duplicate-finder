from __future__ import annotations

import shutil
from pathlib import Path


def move_to_quarantine(path: Path, quarantine_dir: Path) -> Path:
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    target = quarantine_dir / path.name
    if target.exists():
        stem, suffix = path.stem, path.suffix
        idx = 1
        while target.exists():
            target = quarantine_dir / f"{stem}_{idx}{suffix}"
            idx += 1
    shutil.move(str(path), str(target))
    return target
