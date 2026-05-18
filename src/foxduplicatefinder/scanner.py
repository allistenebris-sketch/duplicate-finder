from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from .cache import ScanCache
from .clustering import NearDuplicateRule, cluster_near_duplicates
from .hashing import combined_content_hash
from .models import DuplicateGroup, FileRecord
from .similarity import image_signature, ssim_score

MEDIA_EXT = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff", ".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"
}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff"}


def iter_files(root: Path, deep: bool = True) -> list[Path]:
    globber = root.rglob("*") if deep else root.glob("*")
    return [p for p in globber if p.is_file() and p.suffix.lower() in MEDIA_EXT]


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
                rec.sha256 = combined_content_hash(rec.path)
            cache.upsert(rec)
            by_hash[rec.sha256].append(rec)
        for h, items in by_hash.items():
            if len(items) > 1:
                groups.append(DuplicateGroup(key=f"content:{h}", files=[r.path for r in items], total_size=size * len(items)))
    cache.commit()
    return groups


def find_near_duplicate_images(paths: list[Path], similarity_percent: int = 90) -> list[list[Path]]:
    image_paths = [p for p in paths if p.suffix.lower() in IMAGE_EXT]
    signatures = [image_signature(p) for p in image_paths]
    max_dist = max(2, int((100 - similarity_percent) / 2) + 4)
    phash_clusters = cluster_near_duplicates(
        signatures,
        NearDuplicateRule(max_phash_distance=max_dist, max_dhash_distance=max_dist + 2),
    )

    min_ssim = max(0.7, similarity_percent / 100.0 - 0.06)
    refined: list[list[Path]] = []
    for cluster in phash_clusters:
        if len(cluster) <= 1:
            continue
        accepted: list[Path] = [cluster[0]]
        for candidate in cluster[1:]:
            if any(ssim_score(candidate, existing) >= min_ssim for existing in accepted):
                accepted.append(candidate)
        if len(accepted) > 1:
            refined.append(accepted)

    return refined


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
