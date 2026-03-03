"""Read/write sspec project metadata (.meta.json).

`.meta.json` is treated as a versioned config:
- `meta_schema` is the schema marker for the meta file itself.
- `sspec_schema` records the sspec protocol schema used by templates (AGENTS.md).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict, cast

META_FILE = '.meta.json'

# Schema marker for `.meta.json` structure.
# Bump when the meta.json field layout changes (NOT tied to AGENTS.md schema).
META_SCHEMA = '2.0'


class MetaModel(TypedDict, total=False):
    """On-disk `.meta.json` model (latest known schema).

    `.meta.json` is extensible; unknown keys are allowed and preserved.
    """

    meta_schema: str
    sspec_schema: str

    sspec_version: str
    created_at: str
    updated_at: str

    file_hashes: dict[str, str]
    managed_skills: list[str]
    skill_locations: list[str]
    skill_install_strategies: dict[str, str]


@dataclass(frozen=True, slots=True)
class MetaUpgradeResult:
    meta: MetaModel
    changed: bool
    from_schema: str
    to_schema: str


def get_meta_with_defaults(meta: Mapping[str, Any]) -> MetaModel:
    """Return meta with missing fields filled by defaults (non-destructive).

    Merges caller-supplied meta on top of defaults so existing values are preserved.
    """
    defaults: MetaModel = {
        'meta_schema': META_SCHEMA,
        'sspec_schema': '',
        'sspec_version': '',
        'created_at': '',
        'updated_at': '',
        'file_hashes': {},
        'managed_skills': [],
        'skill_locations': [],
        'skill_install_strategies': {},
    }
    # Preserve unknown keys by merging caller data on top.
    return cast(MetaModel, {**defaults, **dict(meta)})


def _normalize_schema_str(value: Any) -> str | None:
    """Normalize schema marker into a comparable string.

    Returns None when the value is missing/blank/invalid type.
    """

    if value is None:
        return None
    if isinstance(value, (int, float)):
        value = str(value)
    if not isinstance(value, str):
        return None

    v = value.strip()
    if not v:
        return None
    # Accept legacy major-only strings like "1".
    if '.' not in v and v.isdigit():
        return f'{v}.0'
    return v


def _parse_schema(v: str) -> tuple[int, ...] | None:
    parts = v.split('.')
    out: list[int] = []
    for p in parts:
        if p == '' or not p.isdigit():
            return None
        out.append(int(p))
    return tuple(out) if out else None


def _require_parseable_schema(value: Any, *, key_name: str) -> str:
    """Return a normalized schema string or raise ValueError.

    Policy:
    - Missing marker key -> caller decides (often treated as 0.0).
    - Marker key present but value is blank/unparseable -> error (no silent coercion).
    """

    norm = _normalize_schema_str(value)
    if norm is None:
        raise ValueError(f'Invalid {key_name}: {value!r}')
    if _parse_schema(norm) is None:
        raise ValueError(f'Invalid {key_name}: {value!r}')
    return norm


def _compare_schema(v1: str, v2: str) -> int:
    a_norm = _normalize_schema_str(v1)
    b_norm = _normalize_schema_str(v2)
    if a_norm is None or b_norm is None:
        raise ValueError(f'Unparseable schema comparison: {v1!r} vs {v2!r}')

    a = _parse_schema(a_norm)
    b = _parse_schema(b_norm)
    if a is None or b is None:
        raise ValueError(f'Unparseable schema comparison: {v1!r} vs {v2!r}')

    length = max(len(a), len(b))
    a2 = a + (0,) * (length - len(a))
    b2 = b + (0,) * (length - len(b))
    if a2 < b2:
        return -1
    if a2 > b2:
        return 1
    return 0


def _declared_meta_schema(data: Mapping[str, Any]) -> str:
    # v2+ uses `meta_schema`; v1 used `meta_schema_version`.
    if 'meta_schema' in data:
        return _require_parseable_schema(data.get('meta_schema'), key_name='meta_schema')
    if 'meta_schema_version' in data:
        return _require_parseable_schema(
            data.get('meta_schema_version'), key_name='meta_schema_version'
        )
    return '0.0'


def _migrate_to_1_0(data: dict[str, Any]) -> dict[str, Any]:
    # Introduce explicit version marker for very old meta files.
    out = dict(data)
    out.setdefault('meta_schema_version', '1')
    return out


def _migrate_to_2_0(data: dict[str, Any]) -> dict[str, Any]:
    # 1.0 -> 2.0: rename schema markers.
    out = dict(data)

    # schema_version (AGENTS) -> sspec_schema
    if 'sspec_schema' not in out:
        if 'schema_version' in out:
            out['sspec_schema'] = str(out.get('schema_version') or '')
        else:
            out['sspec_schema'] = ''
    out.pop('schema_version', None)

    # meta_schema_version -> meta_schema (new key), but schema value becomes 2.0.
    out.pop('meta_schema_version', None)
    out['meta_schema'] = META_SCHEMA
    return out


def upgrade_meta(meta: Mapping[str, Any]) -> MetaUpgradeResult:
    """Upgrade a raw meta dict to the latest meta_schema.

    - Uses ONLY the declared schema fields (`meta_schema` / legacy `meta_schema_version`).
    - Missing schema is treated as "0.0".
    - Future schema versions raise ValueError to avoid data loss.
    """

    raw: dict[str, Any] = dict(meta)
    from_schema = _declared_meta_schema(raw)

    if _compare_schema(from_schema, META_SCHEMA) > 0:
        raise ValueError(f'Unsupported future meta_schema: {from_schema} (current {META_SCHEMA})')

    result: dict[str, Any] = raw
    current = from_schema

    if _compare_schema(current, '1.0') < 0:
        result = _migrate_to_1_0(result)
        current = '1.0'

    if _compare_schema(current, '2.0') < 0:
        result = _migrate_to_2_0(result)
        current = '2.0'

    # Always enforce latest schema marker (idempotent).
    result['meta_schema'] = META_SCHEMA
    result.pop('meta_schema_version', None)

    upgraded = get_meta_with_defaults(result)

    # Normalize known path-like fields to keep keys stable across platforms.
    locs = upgraded.get('skill_locations', []) or []
    if isinstance(locs, list):
        normalized: set[str] = set()
        for loc in locs:
            if not isinstance(loc, str):
                continue
            s = loc.replace('\\', '/').rstrip('/')
            if s:
                normalized.add(s)
        upgraded['skill_locations'] = sorted(normalized)

    changed = upgraded != raw

    return MetaUpgradeResult(
        meta=upgraded,
        changed=changed,
        from_schema=from_schema,
        to_schema=META_SCHEMA,
    )


def load_meta(sspec_root: Path) -> dict[str, Any]:
    """Load metadata from .meta.json.

    Returns an empty dict on missing/corrupt files.
    """
    meta_path = sspec_root / META_FILE
    if not meta_path.exists():
        return {}

    try:
        data = json.loads(meta_path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return {}

    if not isinstance(data, dict):
        return {}

    # Load is migration-aware so callers can treat meta keys as stable.
    return cast(dict[str, Any], upgrade_meta(data).meta)


def load_meta_raw(sspec_root: Path) -> dict[str, Any]:
    """Load raw metadata without migrations.

    This is used when callers need to decide whether to persist an automatic
    migration.
    """

    meta_path = sspec_root / META_FILE
    if not meta_path.exists():
        return {}

    try:
        data = json.loads(meta_path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return {}

    return data if isinstance(data, dict) else {}


def load_meta_latest(sspec_root: Path) -> MetaUpgradeResult:
    """Load meta and return migration/change info.

    This is primarily for commands that need to decide whether to persist an
    automatic migration (e.g. `sspec project update`).
    """

    meta_path = sspec_root / META_FILE
    if not meta_path.exists():
        res = upgrade_meta({})
        return MetaUpgradeResult(
            meta=res.meta,
            changed=True,
            from_schema=res.from_schema,
            to_schema=res.to_schema,
        )

    raw = load_meta_raw(sspec_root)
    return upgrade_meta(raw)


def save_meta(sspec_root: Path, meta: dict[str, Any]) -> None:
    """Save metadata to .meta.json."""
    meta_path = sspec_root / META_FILE
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8')
