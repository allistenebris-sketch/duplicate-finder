from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from .cache import ScanCache
from .models import DuplicateGroup, FileRecord

MEDIA_EXT = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff", ".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"
}


def iter_files(root: Path, deep: bool = True) -> list[Path]:
    globber = root.rglob("*") if deep else root.glob("*")
    return [p for p in globber if p.is_file() and p.suffix.lower() in MEDIA_EXT]


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def find_exact_duplicates(paths: list[Path], cache: ScanCache) -> list[DuplicateGroup]:
    by_size: dict[int, list[FileRecord]] = defaultdict(list)
    for p in paths:
        stat = p.stat()
        cached = cache.get(p, stat.st_size, stat.st_mtime_ns)
        rec = cached or FileRecord(path=p, size=stat.st_size, mtime_ns=stat.st_mtime_ns)
        by_size[rec.size].append(rec)

    groups: list[DuplicateGroup] = []
    for size, recs in by_size.items():
        if len(recs) < 2:
            continue
        by_hash: dict[str, list[FileRecord]] = defaultdict(list)
        for rec in recs:
            if rec.sha256 is None:
                rec.sha256 = sha256_file(rec.path)
            cache.upsert(rec)
            by_hash[rec.sha256].append(rec)
        for h, items in by_hash.items():
            if len(items) > 1:
                groups.append(DuplicateGroup(key=f"sha256:{h}", files=[r.path for r in items], total_size=size * len(items)))
    cache.commit()
    return groups


def export_json(groups: list[DuplicateGroup], out_path: Path) -> None:
    payload = [
        {"group": g.key, "file_count": len(g.files), "total_size": g.total_size, "files": [str(p) for p in g.files]}
        for g in groups
    ]
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def export_csv(groups: list[DuplicateGroup], out_path: Path) -> None:
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["group", "file_count", "total_size", "file_path"])
        for g in groups:
            for path in g.files:
                writer.writerow([g.key, len(g.files), g.total_size, str(path)])
