from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image
import imagehash


@dataclass(slots=True)
class ImageSignature:
    path: Path
    phash: str
    dhash: str


def image_signature(path: Path) -> ImageSignature:
    with Image.open(path) as img:
        return ImageSignature(
            path=path,
            phash=str(imagehash.phash(img)),
            dhash=str(imagehash.dhash(img)),
        )


def hamming(hex_a: str, hex_b: str) -> int:
    a = imagehash.hex_to_hash(hex_a)
    b = imagehash.hex_to_hash(hex_b)
    return a - b
