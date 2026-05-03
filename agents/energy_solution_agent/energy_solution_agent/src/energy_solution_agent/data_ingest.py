from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SERIES_FIELDS = [
    ("load_data", "load_series_kw"),
    ("load_data", "cooling_load_series_kw"),
    ("load_data", "heating_load_series_kw"),
    ("resource_data.solar", "hourly_generation_profile_kw"),
    ("resource_data.wind", "hourly_generation_profile_kw"),
    ("resource_data.wind", "wind_speed_series_mps"),
    ("charging_data", "arrival_profile"),
]


def ingest_external_series(data: dict[str, Any], base_dir: Path | None = None) -> dict[str, Any]:
    base = base_dir or Path.cwd()
    for section_path, field in SERIES_FIELDS:
        node = _get_node(data, section_path)
        if not isinstance(node, dict):
            continue
        path_key = f"{field}_path"
        if node.get(path_key):
            node[field] = _load_numeric_series(base / str(node[path_key]))
    return data


def _get_node(data: dict[str, Any], dotted: str) -> Any:
    current: Any = data
    for part in dotted.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _load_numeric_series(path: Path) -> list[float]:
    if not path.exists():
        raise FileNotFoundError(f"Series file not found: {path}")
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [float(v) for v in payload]
        if isinstance(payload, dict):
            for key in ("values", "series", "data"):
                if key in payload and isinstance(payload[key], list):
                    return [float(v) for v in payload[key]]
        raise ValueError(f"Unsupported JSON series shape: {path}")
    if path.suffix.lower() in {".csv", ".txt"}:
        values: list[float] = []
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.reader(fh)
            for row in reader:
                for item in row:
                    item = item.strip()
                    if not item:
                        continue
                    try:
                        values.append(float(item))
                    except ValueError:
                        continue
        return values
    raise ValueError(f"Unsupported series file type: {path.suffix}")
