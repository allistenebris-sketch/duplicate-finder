from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from .cache import ScanCache
from .scanner import export_csv, export_json, find_exact_duplicates, iter_files

app = typer.Typer(help="FoxDuplicateFinder CLI")
console = Console()


@app.command()
def scan(
    target: Annotated[Path, typer.Argument(help="Path to scan")],
    deep: Annotated[bool, typer.Option("--deep", help="Recursive deep scan")] = False,
    nsfw: Annotated[bool, typer.Option("--nsfw", help="Enable NSFW analysis (planned)")] = False,
    similarity: Annotated[int, typer.Option("--similarity", min=50, max=100)] = 90,
    cache_db: Annotated[Path, typer.Option("--cache-db", help="SQLite cache path")] = Path(".foxdup/cache.sqlite3"),
    export: Annotated[Path | None, typer.Option("--export", help="Export results to JSON/CSV")] = None,
) -> None:
    if not target.exists():
        raise typer.BadParameter(f"Path does not exist: {target}")

    console.print("[bold green]FoxDuplicateFinder[/bold green] scan started")
    console.print(f"Target: {target}")
    console.print(f"Deep scan: {deep}")
    console.print(f"NSFW analysis: {nsfw} (planned)")
    console.print(f"Similarity threshold: {similarity}% (for future similar matching)")

    files = iter_files(target, deep=deep)
    console.print(f"Indexed media files: {len(files)}")

    cache = ScanCache(cache_db)
    try:
        groups = find_exact_duplicates(files, cache)
    finally:
        cache.close()

    dup_files = sum(len(g.files) for g in groups)
    console.print(f"Exact duplicate groups: {len(groups)}")
    console.print(f"Files in duplicate groups: {dup_files}")

    if export:
        export.parent.mkdir(parents=True, exist_ok=True)
        if export.suffix.lower() == ".json":
            export_json(groups, export)
        elif export.suffix.lower() == ".csv":
            export_csv(groups, export)
        else:
            raise typer.BadParameter("--export supports only .json or .csv")
        console.print(f"Exported: {export}")


if __name__ == "__main__":
    app()
