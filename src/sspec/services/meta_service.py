"""Read/write sspec project metadata (.meta.json)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

META_FILE = '.meta.json'

# Independent schema version for .meta.json structure.
# Increment when the meta.json field layout changes (NOT tied to AGENTS.md schema).
META_SCHEMA_VERSION = '1'


def get_meta_with_defaults(meta: dict[str, Any]) -> dict[str, Any]:
    """Return meta with missing fields filled by defaults (non-destructive).

    Merges caller-supplied meta on top of defaults so existing values are preserved.
    """
    defaults: dict[str, Any] = {
        'meta_schema_version': META_SCHEMA_VERSION,
        'schema_version': '',
        'sspec_version': '',
        'created_at': '',
        'updated_at': '',
        'file_hashes': {},
        'managed_skills': [],
        'skill_locations': [],
        'skill_install_strategies': {},
    }
    return {**defaults, **meta}


def load_meta(sspec_root: Path) -> dict[str, Any]:
    """Load metadata from .meta.json.

    Returns an empty dict on missing/corrupt files (CLI should handle defaults).
    """
    meta_path = sspec_root / META_FILE
    if not meta_path.exists():
        return {}

    try:
        data = json.loads(meta_path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return {}

    if isinstance(data, dict):
        return data

    return {}


def save_meta(sspec_root: Path, meta: dict[str, Any]) -> None:
    """Save metadata to .meta.json."""
    meta_path = sspec_root / META_FILE
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8')
