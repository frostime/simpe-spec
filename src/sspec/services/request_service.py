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
from sspec.libs.md_yaml import parse_frontmatter, update_frontmatter


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


def extract_request_name_from_filename(filename: str) -> str:
    """Extract pure request name from filename (remove timestamp prefix).

    Supports both formats:
    - Old: <yyMMddHHmmss>-<name>
    - New: <yy-MM-ddTHH-mm>_<name>
    """
    # Try new format first: <yy-MM-ddTHH-mm>_<name>
    if '_' in filename:
        parts = filename.split('_')
        if len(parts) > 1:
            # Join all parts after the first underscore
            return '_'.join(parts[1:])

    # Try old format: <yyMMddHHmmss>-<name>
    if '-' in filename:
        parts = filename.split('-')
        if len(parts) > 1:
            # Check if first part looks like a timestamp (12-14 digits)
            first_part = parts[0]
            if len(first_part) >= 12 and len(first_part) <= 14 and first_part.isdigit():
                # Join all parts after the timestamp
                return '-'.join(parts[1:])

    # If no timestamp pattern found, return original
    return filename


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

    # New naming format: <yy-MM-ddTHH-mm>_<name>
    timeprefix = dt.strftime('%y-%m-%dT%H-%M')
    request_path = requests_dir / f'{timeprefix}_{normalized}.md'

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
    from sspec.libs.md_yaml import parse_frontmatter

    try:
        content = path.read_text(encoding='utf-8')
    except OSError:
        return None

    filename_stem = path.stem
    meta, body = parse_frontmatter(content)
    if not meta:
        return None

    # Try to get name from frontmatter first
    request_name = meta.get('name')
    if request_name:
        request_name = str(request_name)
    else:
        # Extract pure name from filename (remove timestamp)
        request_name = extract_request_name_from_filename(filename_stem)
    raw_status = str(meta.get('status', RequestStatus.OPEN.value))
    status = normalize_status(raw_status, RequestStatus)

    tldr = str(meta.get('tldr', '') or '')
    if not tldr:
        tldr = extract_summary(body)

    attach_change = meta.get('attach-change')
    attach_change_str = str(attach_change) if attach_change else None

    return RequestInfo(
        name=request_name,
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
    """Find request file candidates by exact or fuzzy match.

    Supports both old format (<yyMMddHHmmss>-<name>) and new format (<yy-MM-ddTHH-mm>_<name>).
    """
    exact_path = requests_dir / f'{name}.md'
    if exact_path.exists():
        return [exact_path]

    # Try new format: *_<name>.md
    matches = list(requests_dir.glob(f'*_{name}.md'))
    if matches:
        return sorted(matches)

    # Try old format: *-<name>.md (backward compatibility)
    matches = list(requests_dir.glob(f'*-{name}.md'))
    if matches:
        return sorted(matches)

    # Fallback: contains match
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
    """Link a request to a change (bidirectional).

    Updates:
    1. Request frontmatter: attach-change, status=DOING
    2. Change spec.md: adds reference entry
    """
    from sspec.libs.md_yaml import parse_frontmatter, update_frontmatter

    change_path = sspec_root / 'changes' / change_name
    if not change_path.exists():
        raise FileNotFoundError(f"Change '{change_name}' not found")

    # Update request file - store spec.md path instead of dir name
    request_content = request_file.read_text(encoding='utf-8')
    spec_relative = (change_path / 'spec.md').relative_to(sspec_root).as_posix()
    request_content = update_frontmatter(request_content, {
        'attach-change': spec_relative,  # Store path like "changes/<name>/spec.md"
        'status': RequestStatus.DOING.value
    })
    request_file.write_text(request_content, encoding='utf-8')

    # Update change spec.md with reference
    spec_file = change_path / 'spec.md'
    if spec_file.exists():
        spec_content = spec_file.read_text(encoding='utf-8')
        meta, body = parse_frontmatter(spec_content)

        # Get or create reference array
        reference = meta.get('reference') or []
        if not isinstance(reference, list):
            reference = []

        # Add request reference (relative to .sspec/)
        request_relative = request_file.relative_to(sspec_root).as_posix()
        new_ref = {
            'source': request_relative,
            'type': 'request',
            'note': f'Linked from request'
        }

        # Avoid duplicates
        if not any(ref.get('source') == request_relative for ref in reference):
            reference.append(new_ref)

        spec_content = update_frontmatter(spec_content, {'reference': reference})
        spec_file.write_text(spec_content, encoding='utf-8')


def archive_request_file(
    *, sspec_root: Path, requests_dir: Path, request_file: Path
) -> Path:
    """Move a request file into requests/archive and add archived timestamp to frontmatter.

    Updates change.spec.md reference if request was linked to a change.
    Returns destination path.
    """
    from sspec.libs.md_yaml import parse_frontmatter, update_frontmatter

    content = request_file.read_text(encoding='utf-8')
    meta, body = parse_frontmatter(content)
    attach_change = meta.get('attach-change')

    archived_time = datetime.now().isoformat(timespec='seconds')
    updated_content = update_frontmatter(content, {'archived': archived_time})
    request_file.write_text(updated_content, encoding='utf-8')

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

    # Update cross-references in change if this request was linked
    _update_change_after_request_archive(
        sspec_root, request_file.relative_to(sspec_root).as_posix(),
        dest_path.relative_to(sspec_root).as_posix(), attach_change
    )

    return dest_path


def _update_change_after_request_archive(
    sspec_root: Path,
    old_request_relative: str,
    new_request_relative: str,
    attach_change: str | None,
) -> None:
    """Update change.spec.md reference after archiving a request.

    When request is moved to archive/, the change's reference.source should point to new location.
    """
    if not attach_change:
        return

    # Resolve change spec path from attach_change
    if 'spec.md' in attach_change:
        spec_path = sspec_root / attach_change
    else:
        # Old format: just the dir name
        spec_path = sspec_root / 'changes' / attach_change / 'spec.md'

    # Also check archive directory
    if not spec_path.exists():
        archive_spec = sspec_root / 'changes' / 'archive' / attach_change / 'spec.md'
        if archive_spec.exists():
            spec_path = archive_spec
        else:
            return  # Change not found, skip

    content = spec_path.read_text(encoding='utf-8')
    meta, body = parse_frontmatter(content)
    reference = meta.get('reference') or []
    if not isinstance(reference, list):
        return

    updated = False
    for ref in reference:
        if ref.get('source') == old_request_relative:
            ref['source'] = new_request_relative
            ref['note'] = 'Archived request'
            updated = True

    if updated:
        content = update_frontmatter(content, {'reference': reference})
        spec_path.write_text(content, encoding='utf-8')
