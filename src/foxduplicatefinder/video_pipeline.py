from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import subprocess


@dataclass(slots=True)
class VideoFingerprint:
    path: Path
    keyframe_count: int
    audio_fingerprint: str | None


def keyframe_count(path: Path) -> int:
    cmd = [
        "ffprobe", "-v", "error", "-skip_frame", "nokey", "-select_streams", "v:0",
        "-show_entries", "frame=pict_type", "-of", "csv=p=0", str(path),
    ]
    try:
        out = subprocess.check_output(cmd, text=True)
    except Exception:
        return 0
    return sum(1 for line in out.splitlines() if line.strip())


def audio_fingerprint(path: Path, sample_rate: int = 8000, seconds: int = 120) -> str | None:
    """Raw PCM hash as a lightweight audio fingerprint."""
    cmd = [
        "ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0", "-t", str(seconds),
        "-ac", "1", "-ar", str(sample_rate), "-f", "s16le", "-",
    ]
    try:
        pcm = subprocess.check_output(cmd)
    except Exception:
        return None
    if not pcm:
        return None
    return hashlib.blake2b(pcm, digest_size=16).hexdigest()


def build_video_fingerprint(path: Path) -> VideoFingerprint:
    return VideoFingerprint(
        path=path,
        keyframe_count=keyframe_count(path),
        audio_fingerprint=audio_fingerprint(path),
    )
