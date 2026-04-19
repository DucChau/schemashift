"""
Schema detection: infers field names and types from JSON and CSV files.
"""

import csv
import json
from pathlib import Path
from typing import Any


SchemaMap = dict[str, str]  # field_name -> inferred_type


def infer_type(value: Any) -> str:
    if value is None or value == "":
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    # Try coercing strings
    s = str(value).strip()
    if s.lower() in ("true", "false"):
        return "bool"
    try:
        int(s)
        return "int"
    except ValueError:
        pass
    try:
        float(s)
        return "float"
    except ValueError:
        pass
    return "string"


def extract_schema_json(path: Path, sample_rows: int = 50) -> SchemaMap:
    """Extract schema from a JSON file (array of objects or single object)."""
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        rows = [data]
    elif isinstance(data, list):
        rows = data[:sample_rows]
    else:
        return {}

    schema: SchemaMap = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        for k, v in row.items():
            t = infer_type(v)
            if k not in schema or schema[k] == "null":
                schema[k] = t
    return schema


def extract_schema_csv(path: Path, sample_rows: int = 50) -> SchemaMap:
    """Extract schema from a CSV file."""
    schema: SchemaMap = {}
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return {}
        # Initialize all fields
        for field in reader.fieldnames:
            schema[field] = "null"
        for i, row in enumerate(reader):
            if i >= sample_rows:
                break
            for k, v in row.items():
                if k is None:
                    continue
                t = infer_type(v)
                if schema.get(k) == "null" and t != "null":
                    schema[k] = t
    return schema


def extract_schema(path: Path) -> SchemaMap:
    """Auto-detect format and extract schema."""
    suffix = path.suffix.lower()
    if suffix == ".json":
        return extract_schema_json(path)
    elif suffix == ".csv":
        return extract_schema_csv(path)
    else:
        return {}
