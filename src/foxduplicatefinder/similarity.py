from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import imagehash
from PIL import Image

try:
    import cv2
    import numpy as np
except Exception:  # optional runtime dependency
    cv2 = None
    np = None


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


def ssim_score(path_a: Path, path_b: Path, size: int = 256) -> float:
    """Compute SSIM score in [0..1] using OpenCV primitives.

    Returns 0.0 if OpenCV/numpy are unavailable or images cannot be decoded.
    """
    if cv2 is None or np is None:
        return 0.0

    img_a = cv2.imread(str(path_a), cv2.IMREAD_GRAYSCALE)
    img_b = cv2.imread(str(path_b), cv2.IMREAD_GRAYSCALE)
    if img_a is None or img_b is None:
        return 0.0

    img_a = cv2.resize(img_a, (size, size), interpolation=cv2.INTER_AREA)
    img_b = cv2.resize(img_b, (size, size), interpolation=cv2.INTER_AREA)

    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2

    img_a = img_a.astype(np.float64)
    img_b = img_b.astype(np.float64)

    kernel = cv2.getGaussianKernel(11, 1.5)
    window = kernel @ kernel.T

    mu1 = cv2.filter2D(img_a, -1, window)
    mu2 = cv2.filter2D(img_b, -1, window)

    mu1_sq = mu1 * mu1
    mu2_sq = mu2 * mu2
    mu1_mu2 = mu1 * mu2

    sigma1_sq = cv2.filter2D(img_a * img_a, -1, window) - mu1_sq
    sigma2_sq = cv2.filter2D(img_b * img_b, -1, window) - mu2_sq
    sigma12 = cv2.filter2D(img_a * img_b, -1, window) - mu1_mu2

    num = (2 * mu1_mu2 + c1) * (2 * sigma12 + c2)
    den = (mu1_sq + mu2_sq + c1) * (sigma1_sq + sigma2_sq + c2)
    ssim_map = num / (den + 1e-12)
    return float(np.clip(ssim_map.mean(), 0.0, 1.0))
