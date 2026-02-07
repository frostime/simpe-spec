"""Change-related domain logic (no click/rich/questionary dependencies)."""

from __future__ import annotations

import re
import shutil
from datetime import datetime
from pathlib import Path

from sspec.core import (
    ARCHIVE_DIR,
    CHANGE_ROOT_TEMPLATE_FILES,
    CHANGE_TEMPLATE_FILES,
    CHANGES_DIR,
    ChangeExistsError,
    ChangeInfo,
    ChangeStatus,
    InvalidChangeNameError,
    copy_template,
    get_template_dir,
    normalize_status,
)
from sspec.libs.md_yaml import parse_frontmatter, update_frontmatter


def find_change_matches(changes_dir: Path, name: str) -> list[Path]:
    """Find change directory candidates by exact or fuzzy match.

    Supports timestamped format: <yy-MM-ddTHH-mm>_<name>
    Tries exact match first, then suffix match (*_<name>), then contains.
    """
    if not changes_dir.exists():
        return []

    # Exact directory match
    exact = changes_dir / name
    if exact.is_dir() and exact.name != ARCHIVE_DIR:
        return [exact]

    # Pattern: *_<name> (suffix match)
    matches = [
        d
        for d in changes_dir.iterdir()
        if d.is_dir() and d.name != ARCHIVE_DIR and d.name.endswith(f'_{name}')
    ]
    if matches:
        return sorted(matches)

    # Contains match (fallback)
    contains = [
        d for d in changes_dir.iterdir() if d.is_dir() and d.name != ARCHIVE_DIR and name in d.name
    ]
    return sorted(contains)


def extract_change_name_from_dirname(dirname: str) -> str:
    """Extract pure change name from directory name (remove timestamp prefix).

    Format: <yy-MM-ddTHH-mm>_<name> -> <name>
    """
    if '_' in dirname:
        parts = dirname.split('_', 1)
        if len(parts) > 1:
            return parts[1]
    return dirname


def parse_change(change_path: Path, archived: bool = False) -> ChangeInfo:
    """Parse change directory into structured data."""

    spec_file = change_path / 'spec.md'
    tasks_file = change_path / 'tasks.md'

    status = ChangeStatus.PLANNING.value
    change_name = change_path.name
    change_type = ''
    description = ''
    progress = {'done': 0, 'total': 0}
    has_pivot = False
    has_blockers = False

    if spec_file.exists():
        content = spec_file.read_text(encoding='utf-8')
        meta, body = parse_frontmatter(content)

        if meta:
            raw_status = str(meta.get('status', ChangeStatus.PLANNING.value))
            status = normalize_status(raw_status, ChangeStatus)
            change_type = meta.get('type', '') or ''
            description = meta.get('description', '') or ''
            change_name = meta.get('name', change_name)

        has_pivot = bool(re.search(r'PIVOT', content, re.IGNORECASE))
        has_blockers = status == ChangeStatus.BLOCKED.value

    if tasks_file.exists():
        content = tasks_file.read_text(encoding='utf-8')
        # Exclude template examples (lines containing <Demo Task>)
        # See src/sspec/templates/change/tasks.md
        checkbox_pattern = r'- \[[ xX~\-]](?!\s*<Demo Task>)'
        done_pattern = r'- \[[xX]](?!\s*<Demo Task>)'
        total = len(re.findall(checkbox_pattern, content))
        done = len(re.findall(done_pattern, content))
        progress = {'done': done, 'total': total}

    return ChangeInfo(
        name=change_name,
        path=change_path,
        status=status,
        type=change_type,
        description=description,
        progress=progress,
        has_pivot=has_pivot,
        has_blockers=has_blockers,
        archived=archived,
    )


def create_change(sspec_root: Path, change_name: str, *, is_root: bool = False) -> Path:
    """Create a new change directory with spec.md, tasks.md, and handover.md.

    Args:
        sspec_root: Path to .sspec directory
        change_name: Name for the change
        is_root: If True, use root change templates (phase-level coordination)
    """

    # Normalize name: lowercase, replace spaces with hyphens, remove invalid chars
    change_name = re.sub(r'\s+', '-', change_name.strip().lower())
    change_name = re.sub(r'[^a-z0-9\-]', '', change_name)

    if not change_name:
        raise InvalidChangeNameError('Invalid change name')

    # Generate timestamped name: <yy-MM-ddTHH-mm>_<name>
    timestamp = datetime.now().strftime('%y-%m-%dT%H-%M')
    change_file_name = f'{timestamp}_{change_name}'

    change_path = sspec_root / CHANGES_DIR / change_file_name
    if change_path.exists():
        raise ChangeExistsError(f"Change '{change_file_name}' already exists")

    template_subdir = 'change-root' if is_root else 'change'
    template_dir = get_template_dir() / template_subdir
    template_files = CHANGE_ROOT_TEMPLATE_FILES if is_root else CHANGE_TEMPLATE_FILES
    replacements = {
        'CHANGE_NAME': change_name,
        'TIME': datetime.now().isoformat(timespec='seconds'),
    }

    change_path.mkdir(parents=True, exist_ok=True)

    for file_name in template_files:
        copy_template(template_dir / file_name, change_path / file_name, replacements)

    return change_path


def list_changes(sspec_root: Path, include_archived: bool = False) -> list[ChangeInfo]:
    """List all changes with their status."""

    changes: list[ChangeInfo] = []
    changes_dir = sspec_root / CHANGES_DIR

    if not changes_dir.exists():
        return changes

    for change_path in changes_dir.iterdir():
        if not change_path.is_dir():
            continue
        if change_path.name == ARCHIVE_DIR:
            if include_archived:
                archive_dir = change_path
                for archived in archive_dir.iterdir():
                    if archived.is_dir():
                        changes.append(parse_change(archived, archived=True))
            continue

        changes.append(parse_change(change_path, archived=False))

    return sorted(changes, key=lambda x: (x.archived, x.name))


def archive_change(sspec_root: Path, change_info: ChangeInfo) -> Path:
    """Archive a completed change.

    Moves the change to archive/ directory and adds 'archived' timestamp to spec.md frontmatter.
    Name is preserved (no date prefix added).
    """

    change_path = change_info.path
    name = change_path.name

    # Add archived timestamp to spec.md frontmatter
    spec_file = change_path / 'spec.md'
    if spec_file.exists():
        content = spec_file.read_text(encoding='utf-8')
        archived_time = datetime.now().isoformat(timespec='seconds')
        updated_content = update_frontmatter(content, {'archived': archived_time})
        spec_file.write_text(updated_content, encoding='utf-8')

    archive_dir = sspec_root / CHANGES_DIR / ARCHIVE_DIR
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Preserve original name (no date prefix)
    archive_path = archive_dir / name
    counter = 1
    while archive_path.exists():
        archive_path = archive_dir / f'{name}_{counter}'
        counter += 1

    shutil.move(str(change_path), str(archive_path))

    # Update cross-references: any request pointing to this change should point to archive
    _update_requests_after_change_archive(sspec_root, name, archive_path)

    return archive_path


def _update_requests_after_change_archive(
    sspec_root: Path, old_change_dir_name: str, new_archive_path: Path
) -> None:
    """Update request.attach-change after archiving a change.

    When change is moved to archive/, requests pointing to it need updated paths.
    Supports both old format (dir name) and new format (spec.md path).
    """
    requests_dir = sspec_root / 'requests'
    if not requests_dir.exists():
        return

    # New archive path relative to sspec_root
    new_spec_relative = (new_archive_path / 'spec.md').relative_to(sspec_root).as_posix()
    # e.g. "changes/archive/26-02-05T19-28_refactor-clean-code/spec.md"

    for md_file in requests_dir.glob('*.md'):
        content = md_file.read_text(encoding='utf-8')
        meta, body = parse_frontmatter(content)
        attach = meta.get('attach-change', '')

        if not attach:
            continue

        # Match conditions: old format (dir name) or new format (spec.md path)
        should_update = (
            attach == old_change_dir_name
            or attach == f'changes/{old_change_dir_name}/spec.md'
            or old_change_dir_name in str(attach)
        )

        if should_update:
            updated = update_frontmatter(content, {'attach-change': new_spec_relative})
            md_file.write_text(updated, encoding='utf-8')


def validate_change(change_path: Path) -> list[str]:
    """Validate change directory structure and content quality.

    Returns a list of warning/issue strings. Empty list = all good.
    """
    issues: list[str] = []

    # Check required files
    for fname in CHANGE_TEMPLATE_FILES:
        fpath = change_path / fname
        if not fpath.exists():
            issues.append(f'Missing required file: {fname}')

    spec_file = change_path / 'spec.md'
    if spec_file.exists():
        content = spec_file.read_text(encoding='utf-8')
        meta, body = parse_frontmatter(content)

        if not meta.get('name'):
            issues.append('spec.md: missing "name" in frontmatter')
        if not meta.get('status'):
            issues.append('spec.md: missing "status" in frontmatter')

        sections = ['## A.', '## B.', '## C.']
        for section in sections:
            if section in body:
                idx = body.index(section)
                next_heading = body.find('\n## ', idx + len(section))
                section_body = body[idx:next_heading] if next_heading > 0 else body[idx:]
                lines = [
                    line
                    for line in section_body.split('\n')
                    if line.strip()
                    and not line.startswith('#')
                    and not line.strip().startswith('<!--')
                ]
                if len(lines) == 0:
                    issues.append(f'spec.md: Section "{section}" has no content (still template)')
            else:
                issues.append(f'spec.md: Missing section "{section}"')

    tasks_file = change_path / 'tasks.md'
    if tasks_file.exists():
        content = tasks_file.read_text(encoding='utf-8')
        checkbox_pattern = r'- \[[ xX~\-]](?!\s*<Demo Task>)'
        total = len(re.findall(checkbox_pattern, content))
        if total == 0:
            issues.append('tasks.md: No tasks defined (still template)')

    handover_file = change_path / 'handover.md'
    if handover_file.exists():
        content = handover_file.read_text(encoding='utf-8')
        if '## Background' in content:
            bg_idx = content.index('## Background')
            next_heading = content.find('\n## ', bg_idx + 13)
            bg_body = content[bg_idx:next_heading] if next_heading > 0 else content[bg_idx:]
            lines = [
                line
                for line in bg_body.split('\n')
                if line.strip() and not line.startswith('#') and not line.strip().startswith('<!--')
            ]
            if len(lines) == 0:
                issues.append('handover.md: Background section empty')

    return issues
