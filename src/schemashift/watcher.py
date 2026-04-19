"""
File watcher: monitors a directory for changes and triggers schema diffing.
"""

import time
from pathlib import Path
from rich.console import Console
from .detector import extract_schema
from .differ import diff_schemas
from .store import load_store, save_store, STORE_FILE
from .renderer import render_diff, render_summary

console = Console()

SUPPORTED = {".json", ".csv"}


def scan_directory(watch_dir: Path, store_path: Path, show_unchanged: bool = False) -> None:
    store = load_store(store_path)
    diffs = []
    updated_store = dict(store)

    files = sorted([f for f in watch_dir.rglob("*") if f.suffix.lower() in SUPPORTED])

    if not files:
        console.print(f"[yellow]No JSON or CSV files found in {watch_dir}[/yellow]")
        return

    for file in files:
        rel = str(file.relative_to(watch_dir))
        new_schema = extract_schema(file)
        old_schema = store.get(rel, {})
        diff = diff_schemas(rel, old_schema, new_schema)
        diffs.append(diff)
        updated_store[rel] = new_schema

    save_store(store_path, updated_store)
    render_summary(diffs)

    for diff in diffs:
        render_diff(diff, show_unchanged=show_unchanged)


def watch_loop(watch_dir: Path, store_path: Path, interval: int, show_unchanged: bool) -> None:
    console.print(f"[bold cyan]⟳ schemashift[/bold cyan] watching [bold]{watch_dir}[/bold] every [bold]{interval}s[/bold]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")
    try:
        while True:
            scan_directory(watch_dir, store_path, show_unchanged)
            time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[dim]stopped.[/dim]")
