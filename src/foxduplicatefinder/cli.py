from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

app = typer.Typer(help="FoxDuplicateFinder CLI")
console = Console()


@app.command()
def scan(
    target: Annotated[Path, typer.Argument(help="Path to scan")],
    deep: Annotated[bool, typer.Option("--deep", help="Recursive deep scan")] = False,
    nsfw: Annotated[bool, typer.Option("--nsfw", help="Enable NSFW analysis")] = False,
    similarity: Annotated[int, typer.Option("--similarity", min=50, max=100)] = 90,
) -> None:
    """Run a scan (MVP stub)."""
    if not target.exists():
        raise typer.BadParameter(f"Path does not exist: {target}")

    console.print("[bold green]FoxDuplicateFinder[/bold green] scan started")
    console.print(f"Target: {target}")
    console.print(f"Deep scan: {deep}")
    console.print(f"NSFW analysis: {nsfw}")
    console.print(f"Similarity threshold: {similarity}%")
    console.print("\n[yellow]MVP scaffold only:[/yellow] deduplication engines are not wired yet.")


if __name__ == "__main__":
    app()
