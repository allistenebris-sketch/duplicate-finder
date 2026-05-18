from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass(slots=True)
class VideoFingerprint:
    path: Path
    keyframe_count: int
    audio_fingerprint: str | None


def keyframe_count(path: Path) -> int:
    """Lightweight ffprobe-based keyframe estimate (MVP placeholder)."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-skip_frame",
        "nokey",
        "-select_streams",
        "v:0",
        "-show_entries",
        "frame=pict_type",
        "-of",
        "csv=p=0",
        str(path),
    ]
    try:
        out = subprocess.check_output(cmd, text=True)
    except Exception:
        return 0
    return sum(1 for line in out.splitlines() if line.strip())


def build_video_fingerprint(path: Path) -> VideoFingerprint:
    # audio fingerprint reserved for next iteration (chromaprint/librosa etc.)
    return VideoFingerprint(path=path, keyframe_count=keyframe_count(path), audio_fingerprint=None)
