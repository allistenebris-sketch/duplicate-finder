from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

try:
    import onnxruntime as ort
except Exception:
    ort = None


@dataclass(slots=True)
class NsfwResult:
    path: Path
    nsfw_score: float
    violence_score: float
    anime_nsfw_score: float


class OnnxSafetyClassifier:
    """ONNX classifier with normalized outputs for content categories."""

    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path
        self.session = None
        self.input_name = None
        if model_path is not None and ort is not None and model_path.exists():
            self.session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
            self.input_name = self.session.get_inputs()[0].name

    @staticmethod
    def _preprocess(path: Path, size: int = 224) -> np.ndarray:
        with Image.open(path).convert("RGB") as img:
            img = img.resize((size, size), Image.Resampling.BILINEAR)
            arr = np.asarray(img, dtype=np.float32) / 255.0
        arr = (arr - 0.5) / 0.5
        arr = np.transpose(arr, (2, 0, 1))[None, ...]
        return arr.astype(np.float32)

    @staticmethod
    def _sigmoid(x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-x))

    def classify_image(self, path: Path) -> NsfwResult:
        if self.session is None or self.input_name is None:
            return NsfwResult(path=path, nsfw_score=0.0, violence_score=0.0, anime_nsfw_score=0.0)

        tensor = self._preprocess(path)
        output = self.session.run(None, {self.input_name: tensor})[0]
        scores = np.asarray(output).reshape(-1)
        probs = self._sigmoid(scores)
        nsfw = float(probs[0]) if probs.size > 0 else 0.0
        violence = float(probs[1]) if probs.size > 1 else nsfw
        anime = float(probs[2]) if probs.size > 2 else nsfw
        return NsfwResult(path=path, nsfw_score=nsfw, violence_score=violence, anime_nsfw_score=anime)
