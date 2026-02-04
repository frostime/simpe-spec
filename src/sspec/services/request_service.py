"""Request-related domain logic (no click/rich/questionary).

Commands are responsible for user interaction and output; this module contains
filesystem and parsing logic for requests.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from sspec.core import RequestStatus, normalize_status


@dataclass(frozen=True, slots=True)
class RequestInfo:
    name: str
    status: str
    created: str
    attach_change: str | None
    tldr: str
    path: Path


class RequestNotFoundError(RuntimeError):
    pass


class MultipleRequestsFoundError(RuntimeError):
    def __init__(self, name: str, matches: list[Path]):
        self.name = name
        self.matches = matches
        super().__init__(f"Multiple matches for '{name}'")


def normalize_request_name(name: str) -> str:
    """Normalize a request name to kebab-case."""
    normalized = re.sub(r'\s+', '-', name.strip().lower())
    normalized = re.sub(r'[^a-z0-9\-]', '', normalized)
    return normalized


def extract_summary(body: str) -> str:
    """Extract a short summary from the body as a fallback."""
    for line in body.split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('<!--'):
            return stripped[:50] + ('...' if len(stripped) > 50 else '')
    return ''


def _split_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}, parts[2]

    if not isinstance(meta, dict):
        meta = {}

    body = parts[2].lstrip('\n')
    return meta, body


def create_request(
    *,
    sspec_root: Path,
    name: str,
    template_path: Path | None,
    now: datetime | None = None,
) -> Path:
    """Create a new request markdown file and return its path."""
    requests_dir = sspec_root / 'requests'
    requests_dir.mkdir(parents=True, exist_ok=True)

    normalized = normalize_request_name(name)
    if not normalized:
        raise ValueError('Invalid request name')

    dt = now or datetime.now()
    timestamp = dt.isoformat(timespec='seconds')
    timeprefix = dt.strftime('%y%m%d%H%M%S')
    request_path = requests_dir / f'{timeprefix}-{normalized}.md'

    if request_path.exists():
        raise FileExistsError(f"Request '{normalized}' already exists")

    if template_path and template_path.exists():
        # Lazy import to keep this service independent from other domains.
        from sspec.core import render_template

        template_content = template_path.read_text(encoding='utf-8')
        content = render_template(template_content, {'TIME': timestamp, 'NAME': normalized})
    else:
        content = (
            '---\n'
            f'created: {timestamp}\n'
            f'status: {RequestStatus.OPEN.value}\n'
            'attach-change: null\n'
            "tldr: ''\n"
            '---\n\n'
            f'# Request: {normalized}\n\n'
            '## What I Want\n\n'
            '<!-- Describe what you want to accomplish -->\n\n'
            '## Why\n\n'
            '<!-- Why is this needed? What problem does it solve? -->\n\n'
            '## Additional Context\n\n'
            '<!-- Any constraints, preferences, references -->\n\n'
        )

    request_path.write_text(content, encoding='utf-8')
    return request_path


def parse_request_file(path: Path) -> RequestInfo | None:
    """Parse request file into RequestInfo, or None if unreadable."""
    try:
        content = path.read_text(encoding='utf-8')
    except OSError:
        return None

    meta, body = _split_frontmatter(content)
    if not meta:
        return None

    raw_status = str(meta.get('status', RequestStatus.OPEN.value))
    status = normalize_status(raw_status, RequestStatus)

    tldr = str(meta.get('tldr', '') or '')
    if not tldr:
        tldr = extract_summary(body)

    attach_change = meta.get('attach-change')
    attach_change_str = str(attach_change) if attach_change else None

    return RequestInfo(
        name=path.stem,
        status=status,
        created=str(meta.get('created', '') or ''),
        attach_change=attach_change_str,
        tldr=tldr,
        path=path,
    )


def list_requests(requests_dir: Path) -> list[RequestInfo]:
    """List all request files in a directory."""
    items: list[RequestInfo] = []
    for file_path in requests_dir.glob('*.md'):
        info = parse_request_file(file_path)
        if info:
            items.append(info)
    return items


def find_request_matches(requests_dir: Path, name: str) -> list[Path]:
    """Find request file candidates by exact or fuzzy match."""
    exact_path = requests_dir / f'{name}.md'
    if exact_path.exists():
        return [exact_path]

    matches = list(requests_dir.glob(f'*-{name}.md'))
    if matches:
        return sorted(matches)

    contains = [p for p in requests_dir.glob('*.md') if name in p.stem]
    if contains:
        return sorted(contains)

    return []


def link_request_to_change(
    *,
    sspec_root: Path,
    requests_dir: Path,
    request_file: Path,
    change_name: str,
) -> None:
    """Link a request to a change and set status to DOING."""
    change_path = sspec_root / 'changes' / change_name
    if not change_path.exists():
        raise FileNotFoundError(f"Change '{change_name}' not found")

    content = request_file.read_text(encoding='utf-8')
    if not content.startswith('---'):
        raise ValueError('Request file missing front yaml')

    parts = content.split('---', 2)
    if len(parts) < 3:
        raise ValueError('Invalid request file format')

    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        raise ValueError(f'Invalid yaml: {e}') from e

    if not isinstance(meta, dict):
        meta = {}

    meta['attach-change'] = change_name
    meta['status'] = RequestStatus.DOING.value

    new_yaml = yaml.dump(meta, default_flow_style=False, allow_unicode=True)
    new_content = f'---\n{new_yaml}---{parts[2]}'
    request_file.write_text(new_content, encoding='utf-8')


def archive_request_file(*, requests_dir: Path, request_file: Path) -> Path:
    """Move a request file into requests/archive and return destination path."""
    archive_dir = requests_dir / 'archive'
    archive_dir.mkdir(parents=True, exist_ok=True)

    dest_path = archive_dir / request_file.name
    if dest_path.exists():
        counter = 1
        stem = dest_path.stem
        while dest_path.exists():
            dest_path = archive_dir / f'{stem}_{counter}.md'
            counter += 1

    shutil.move(str(request_file), str(dest_path))
    return dest_path
