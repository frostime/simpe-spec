"""Read/write sspec project metadata (.meta.json)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

META_FILE = ".meta.json"


def load_meta(sspec_root: Path) -> dict[str, Any]:
    """Load metadata from .meta.json.

    Returns an empty dict on missing/corrupt files (CLI should handle defaults).
    """
    meta_path = sspec_root / META_FILE
    if not meta_path.exists():
        return {}

    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    if isinstance(data, dict):
        return data

    return {}


def save_meta(sspec_root: Path, meta: dict[str, Any]) -> None:
    """Save metadata to .meta.json."""
    meta_path = sspec_root / META_FILE
    meta_path.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
