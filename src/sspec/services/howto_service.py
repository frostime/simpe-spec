"""HOWTO management services."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from sspec.core import get_builtin_howto_dir, get_project_howto_dir
from sspec.libs.md_yaml import parse_frontmatter

HowtoSource = Literal['builtin', 'project']


@dataclass(frozen=True, slots=True)
class HowtoInfo:
    """Structured HOWTO document information."""

    name: str
    lookup_key: str
    description: str
    path: Path
    source: HowtoSource
    file: str
    type: str | None = None


@dataclass(frozen=True, slots=True)
class HowtoCatalog:
    """Collected HOWTO documents plus non-fatal registry warnings."""

    items: tuple[HowtoInfo, ...]
    warnings: tuple[str, ...]


def normalize_howto_name(name: str) -> str:
    """Normalize HOWTO names into a stable lookup key."""

    normalized = re.sub(r'[\s_]+', '-', name.strip().lower())
    normalized = re.sub(r'[^a-z0-9-]+', '', normalized)
    normalized = re.sub(r'-{2,}', '-', normalized).strip('-')
    return normalized


def parse_howto_metadata(howto_path: Path) -> dict[str, Any]:
    """Parse YAML frontmatter from a HOWTO markdown file."""

    if not howto_path.exists():
        return {}

    content = howto_path.read_text(encoding='utf-8')
    meta, _body = parse_frontmatter(content)
    return meta if isinstance(meta, dict) else {}


def _build_howto_info(
    howto_path: Path,
    *,
    source: HowtoSource,
    root_dir: Path,
) -> HowtoInfo | None:
    """Build a `HowtoInfo` object for a HOWTO file."""

    meta = parse_howto_metadata(howto_path)
    raw_name = str(meta.get('name') or howto_path.stem).strip()
    name = raw_name or howto_path.stem
    lookup_key = normalize_howto_name(name)
    if not lookup_key:
        return None

    description = str(meta.get('desc') or meta.get('description') or '').strip()
    howto_type_raw = meta.get('type')
    howto_type = str(howto_type_raw).strip() if howto_type_raw else None
    try:
        relative_file = howto_path.relative_to(root_dir).as_posix()
    except ValueError:
        relative_file = howto_path.name

    return HowtoInfo(
        name=name,
        lookup_key=lookup_key,
        description=description,
        path=howto_path,
        source=source,
        file=relative_file,
        type=howto_type,
    )


def collect_howtos(sspec_root: Path | None) -> HowtoCatalog:
    """Collect builtin and project HOWTOs with deterministic duplicate handling.

    When sspec_root is None, only builtin HOWTOs are collected.
    """

    items: list[HowtoInfo] = []
    warnings: list[str] = []
    seen: dict[str, HowtoInfo] = {}

    sources_list: list[tuple[HowtoSource, Path]] = [
        ('builtin', get_builtin_howto_dir()),
    ]
    if sspec_root is not None:
        sources_list.append(('project', get_project_howto_dir(sspec_root)))

    sources: tuple[tuple[HowtoSource, Path], ...] = tuple(sources_list)

    for source, howto_dir in sources:
        if not howto_dir.exists():
            continue

        for howto_path in sorted(howto_dir.glob('*.md')):
            info = _build_howto_info(howto_path, source=source, root_dir=howto_dir)
            if info is None:
                continue

            existing = seen.get(info.lookup_key)
            if existing is not None:
                warnings.append(
                    'Skipped duplicate HOWTO '
                    f"'{info.name}' from {howto_path.as_posix()}; already registered by "
                    f'{existing.path.as_posix()}.'
                )
                continue

            seen[info.lookup_key] = info
            items.append(info)

    return HowtoCatalog(
        items=tuple(sorted(items, key=lambda item: item.name.lower())),
        warnings=tuple(warnings),
    )


def resolve_howto(
    sspec_root: Path | None,
    name: str,
) -> tuple[HowtoInfo | None, tuple[str, ...]]:
    """Resolve a HOWTO name to one collected HOWTO entry."""

    catalog = collect_howtos(sspec_root)
    lookup_key = normalize_howto_name(name)
    if not lookup_key:
        return None, catalog.warnings

    match = next((item for item in catalog.items if item.lookup_key == lookup_key), None)
    return match, catalog.warnings


def read_howto_body(howto_path: Path) -> str:
    """Read HOWTO markdown body without frontmatter."""

    content = howto_path.read_text(encoding='utf-8')
    _meta, body = parse_frontmatter(content)
    return body.strip()


def create_project_howto(sspec_root: Path, name: str, description: str = '') -> Path:
    """Create a new HOWTO markdown file under `.sspec/howto/`."""

    if not isinstance(name, str) or not name.strip():
        raise ValueError('HOWTO name must be a non-empty string')
    if name != name.strip():
        raise ValueError('HOWTO name must not contain leading/trailing whitespace')

    lookup_key = normalize_howto_name(name)
    if not lookup_key:
        raise ValueError(f'Invalid HOWTO name: {name!r}')

    howto_dir = get_project_howto_dir(sspec_root)
    howto_dir.mkdir(parents=True, exist_ok=True)
    howto_path = howto_dir / f'{lookup_key}.md'
    if howto_path.exists():
        raise FileExistsError(f"HOWTO '{lookup_key}' already exists in {howto_dir.as_posix()}")

    template = (
        f'---\nname: {lookup_key}\ndesc: {description}\n---\n\n'
        '<!-- Add a short, focused operational guide here. -->\n'
    )
    howto_path.write_text(template, encoding='utf-8')
    return howto_path
