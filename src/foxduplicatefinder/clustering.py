from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .similarity import ImageSignature, hamming


@dataclass(slots=True)
class NearDuplicateRule:
    max_phash_distance: int = 8
    max_dhash_distance: int = 10


def cluster_near_duplicates(signatures: list[ImageSignature], rule: NearDuplicateRule) -> list[list[Path]]:
    clusters: list[list[ImageSignature]] = []
    for sig in signatures:
        placed = False
        for cluster in clusters:
            pivot = cluster[0]
            if hamming(sig.phash, pivot.phash) <= rule.max_phash_distance and hamming(
                sig.dhash, pivot.dhash
            ) <= rule.max_dhash_distance:
                cluster.append(sig)
                placed = True
                break
        if not placed:
            clusters.append([sig])
    return [[s.path for s in cluster] for cluster in clusters if len(cluster) > 1]
