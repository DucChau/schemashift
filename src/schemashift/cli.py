"""
CLI entrypoint for schemashift.
"""

import click
from pathlib import Path
from .watcher import scan_directory, watch_loop
from .store import STORE_FILE


@click.group()
@click.version_option("1.0.0", prog_name="schemashift")
def cli():
    """schemashift — detect schema drift in JSON and CSV data files."""
    pass


@cli.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--store", default=None, help="Path to snapshot store file")
@click.option("--all", "show_unchanged", is_flag=True, default=False, help="Show unchanged fields too")
def scan(directory: str, store: str | None, show_unchanged: bool):
    """Scan a directory once and show schema drift since last run."""
    watch_dir = Path(directory).resolve()
    store_path = Path(store) if store else watch_dir / STORE_FILE
    scan_directory(watch_dir, store_path, show_unchanged)


@cli.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--interval", default=10, show_default=True, help="Polling interval in seconds")
@click.option("--store", default=None, help="Path to snapshot store file")
@click.option("--all", "show_unchanged", is_flag=True, default=False, help="Show unchanged fields too")
def watch(directory: str, interval: int, store: str | None, show_unchanged: bool):
    """Watch a directory continuously for schema changes."""
    watch_dir = Path(directory).resolve()
    store_path = Path(store) if store else watch_dir / STORE_FILE
    watch_loop(watch_dir, store_path, interval, show_unchanged)


@cli.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option("--store", default=None, help="Path to snapshot store file")
def reset(directory: str, store: str | None):
    """Clear the stored schema snapshots for a directory."""
    watch_dir = Path(directory).resolve()
    store_path = Path(store) if store else watch_dir / STORE_FILE
    if store_path.exists():
        store_path.unlink()
        click.echo(f"✓ Snapshots cleared: {store_path}")
    else:
        click.echo("No snapshot store found — nothing to clear.")


def main():
    cli()


if __name__ == "__main__":
    main()
