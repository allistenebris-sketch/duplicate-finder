from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class NsfwResult:
    path: Path
    nsfw_score: float
    violence_score: float
    anime_nsfw_score: float


class OnnxSafetyClassifier:
    """ONNX runtime integration point.

    Current MVP keeps interface stable and returns neutral scores when model is not configured.
    """

    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path

    def classify_image(self, path: Path) -> NsfwResult:
        # Real inference to be connected with onnxruntime + model preprocessing.
        return NsfwResult(path=path, nsfw_score=0.0, violence_score=0.0, anime_nsfw_score=0.0)
