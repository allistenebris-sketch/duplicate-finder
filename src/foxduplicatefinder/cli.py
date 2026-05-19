from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from .cache import ScanCache
from .gui import run_gui
from .nsfw import OnnxSafetyClassifier
from .scanner import export_csv, export_json, find_exact_duplicates, find_near_duplicate_images, iter_files
from .video_pipeline import build_video_fingerprint

app = typer.Typer(help="FoxDuplicateFinder CLI")
console = Console()


@app.command()
def scan(
    target: Annotated[Path, typer.Argument(help="Path to scan")],
    deep: Annotated[bool, typer.Option("--deep", help="Recursive deep scan")] = False,
    nsfw: Annotated[bool, typer.Option("--nsfw", help="Enable NSFW analysis")] = False,
    nsfw_model: Annotated[Path | None, typer.Option("--nsfw-model", help="ONNX model path")] = None,
    similarity: Annotated[int, typer.Option("--similarity", min=50, max=100)] = 90,
    cache_db: Annotated[Path, typer.Option("--cache-db", help="SQLite cache path")] = Path(".foxdup/cache.sqlite3"),
    export: Annotated[Path | None, typer.Option("--export", help="Export exact duplicate results to JSON/CSV")] = None,
) -> None:
    if not target.exists():
        raise typer.BadParameter(f"Path does not exist: {target}")

    files = iter_files(target, deep=deep)
    console.print(f"Indexed media files: {len(files)}")

    cache = ScanCache(cache_db)
    try:
        exact_groups = find_exact_duplicates(files, cache)
    finally:
        cache.close()

    near_groups = find_near_duplicate_images(files, similarity_percent=similarity)

    console.print(f"Exact duplicate groups: {len(exact_groups)}")
    console.print(f"Near-duplicate image groups: {len(near_groups)}")

    video_files = [p for p in files if p.suffix.lower() in {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}]
    if video_files:
        sample_fp = build_video_fingerprint(video_files[0])
        console.print(f"Video fingerprint sample: keyframes={sample_fp.keyframe_count}, audio={sample_fp.audio_fingerprint or 'n/a'}")

    if nsfw:
        model = OnnxSafetyClassifier(nsfw_model)
        image_files = [p for p in files if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff"}]
        if image_files:
            res = model.classify_image(image_files[0])
            console.print(
                f"NSFW sample for {image_files[0].name}: nsfw={res.nsfw_score:.3f}, "
                f"violence={res.violence_score:.3f}, anime={res.anime_nsfw_score:.3f}"
            )

    if export:
        export.parent.mkdir(parents=True, exist_ok=True)
        if export.suffix.lower() == ".json":
            export_json(exact_groups, export)
        elif export.suffix.lower() == ".csv":
            export_csv(exact_groups, export)
        else:
            raise typer.BadParameter("--export supports only .json or .csv")
        console.print(f"Exported: {export}")


@app.command("gui")
def gui_command() -> None:
    run_gui()


if __name__ == "__main__":
    app()
