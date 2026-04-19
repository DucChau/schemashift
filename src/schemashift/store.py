"""
Snapshot store: persists schema snapshots to a local JSON file for comparison.
"""

import json
from pathlib import Path
from .detector import SchemaMap


STORE_FILE = ".schemashift_snapshots.json"


def load_store(store_path: Path) -> dict[str, SchemaMap]:
    if not store_path.exists():
        return {}
    with store_path.open(encoding="utf-8") as f:
        return json.load(f)


def save_store(store_path: Path, store: dict[str, SchemaMap]) -> None:
    with store_path.open("w", encoding="utf-8") as f:
        json.dump(store, f, indent=2)
