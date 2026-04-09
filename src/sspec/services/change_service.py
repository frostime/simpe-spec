"""Change-related domain logic (no click/rich/questionary dependencies)."""

from __future__ import annotations

import re
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from sspec.core import (
    ARCHIVE_DIR,
    CHANGE_BASE_FILES,
    CHANGES_DIR,
    REQUEST_DIR,
    SCAFFOLD_FILE_MAP,
    SCAFFOLD_ROOT_TYPES,
    SCAFFOLD_SINGLE_TYPES,
    ChangeExistsError,
    ChangeInfo,
    ChangeStatus,
    ChangeStatusSummary,
    InvalidChangeNameError,
    SessionLogSummary,
    copy_template,
    get_template_dir,
    normalize_status,
)
from sspec.libs.md_yaml import parse_frontmatter, update_frontmatter
from sspec.libs.path_refs import update_references_in_dirs


def _run_git(project_root: Path, *args: str) -> subprocess.CompletedProcess[str] | None:
    """Run a git command in the project root, returning None when git is unavailable."""

    try:
        return subprocess.run(
            ['git', *args],
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=False,
        )
    except OSError:
        return None


def _git_stdout(project_root: Path, *args: str) -> str | None:
    """Return stripped git stdout on success, otherwise None."""

    result = _run_git(project_root, *args)
    if result is None or result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _render_git_snapshot(project_root: Path) -> str:
    """Render the immutable git baseline section for memory templates."""

    repo_root = _git_stdout(project_root, 'rev-parse', '--show-toplevel')
    if repo_root is None:
        return '\n'.join(
            [
                '- Captured: before change file creation',
                '- Repository: unavailable',
                '- Reason: current project root is not inside a git worktree, or `git` '
                'is unavailable.',
                '',
                '```text',
                'Not a git repository.',
                '```',
            ]
        )

    branch = _git_stdout(project_root, 'branch', '--show-current')
    head_hash = _git_stdout(project_root, 'rev-parse', 'HEAD')
    status_output = _git_stdout(project_root, 'status', '--short', '--branch')
    status_lines = status_output.splitlines() if status_output else ['status unavailable']
    worktree_state = 'dirty' if len(status_lines) > 1 else 'clean'

    branch_label = branch or 'detached HEAD'
    head_label = head_hash or '(no commits yet)'

    lines = [
        '- Captured: before change file creation',
        f'- Repository: `{Path(repo_root).as_posix()}`',
        f'- Branch: `{branch_label}`',
        f'- HEAD: `{head_label}`',
        f'- Worktree: `{worktree_state}`',
        '- Status Snapshot: raw `git status --short --branch` output',
    ]

    lines.extend(['', '```text', *status_lines, '```'])
    return '\n'.join(lines)


def find_change_matches(changes_dir: Path, name: str, include_archived: bool = False) -> list[Path]:
    """Find change directory candidates by exact or fuzzy match.

    Supports timestamped format: <yy-MM-ddTHH-mm>_<name>
    Tries exact match first, then suffix match (*_<name>), then contains.
    """
    if not changes_dir.exists():
        return []

    def _collect_from(dir_path: Path) -> list[Path]:
        # Exact directory match
        exact = dir_path / name
        if exact.is_dir() and exact.name != ARCHIVE_DIR:
            return [exact]

        # Pattern: *_<name> (suffix match)
        matches = [
            d
            for d in dir_path.iterdir()
            if d.is_dir() and d.name != ARCHIVE_DIR and d.name.endswith(f'_{name}')
        ]
        if matches:
            return matches

        # Contains match (fallback)
        return [
            d for d in dir_path.iterdir() if d.is_dir() and d.name != ARCHIVE_DIR and name in d.name
        ]

    results = _collect_from(changes_dir)

    if include_archived:
        archive_dir = changes_dir / ARCHIVE_DIR
        if archive_dir.exists():
            results.extend(_collect_from(archive_dir))

    return sorted(set(results))


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

    meta = {}
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
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
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
        frontmatter=meta,
    )


def _parse_change_datetime(value: object) -> datetime | None:
    """Parse a change frontmatter timestamp when present."""

    if not isinstance(value, str) or not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _parse_change_dir_timestamp(change_path: Path) -> datetime | None:
    """Parse the timestamp prefix from a change directory name."""

    prefix = change_path.name.split('_', 1)[0]
    try:
        return datetime.strptime(prefix, '%y-%m-%dT%H-%M')
    except ValueError:
        return None


def _get_change_sort_time(change: ChangeInfo) -> datetime | None:
    """Return the most relevant timestamp for list ordering."""

    meta = change.frontmatter
    primary_key = 'archived' if change.archived else 'created'
    fallback_key = 'created' if change.archived else None

    primary = _parse_change_datetime(meta.get(primary_key))
    if primary is not None:
        return primary

    if fallback_key is not None:
        fallback = _parse_change_datetime(meta.get(fallback_key))
        if fallback is not None:
            return fallback

    return _parse_change_dir_timestamp(change.path)


def _change_sort_key(change: ChangeInfo) -> tuple[bool, timedelta, str]:
    """Sort active changes first, then newest-first within each group."""

    sort_time = _get_change_sort_time(change)
    age = datetime.max - sort_time if sort_time is not None else timedelta.max
    return (change.archived, age, change.name)


def _display_path(path: Path, base: Path) -> str:
    """Render path relative to base when possible."""
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def _extract_updated(memory_content: str) -> str | None:
    """Extract Updated field from memory content."""
    match = re.search(r'^\*\*Updated\*\*:\s*(.+?)\s*$', memory_content, re.MULTILINE)
    if not match:
        return None

    value = match.group(1).strip()
    return None if value.startswith('<!--') else value


def _extract_latest_session_log(memory_content: str) -> SessionLogSummary | None:
    """Extract the newest session log entry summary from memory.md."""
    lines = memory_content.splitlines()

    try:
        start = next(i for i, line in enumerate(lines) if line.startswith('## Session Log'))
    except StopIteration:
        return None

    heading_index = None
    heading_match = None
    heading_pattern = re.compile(
        r'^###\s+(?P<timestamp>\S+)(?:\s+\[(?P<tags>[^\]]+)\])?(?:\s+(?P<title>.+))?$'
    )
    in_comment = False
    for idx in range(start + 1, len(lines)):
        raw_line = lines[idx]
        candidate = raw_line.strip()
        if '<!--' in raw_line:
            in_comment = True
        if in_comment:
            if '-->' in raw_line:
                in_comment = False
            continue
        match = heading_pattern.match(candidate)
        if match and not match.group('timestamp').startswith('<'):
            heading_index = idx
            heading_match = match
            break

    if heading_index is None or heading_match is None:
        return None

    next_items: list[str] = []
    in_next_block = False
    bullet_pattern = re.compile(r'^(-|\d+\.)\s+(.*\S)\s*$')
    for idx in range(heading_index + 1, len(lines)):
        stripped = lines[idx].strip()
        if stripped.startswith('### ') or stripped.startswith('## '):
            break
        if stripped == '**Next**':
            in_next_block = True
            continue
        if stripped.startswith('**') and stripped != '**Next**':
            in_next_block = False
            continue
        if not in_next_block or not stripped:
            continue
        if match := bullet_pattern.match(stripped):
            next_items.append(match.group(2))

    tags_raw = heading_match.group('tags') or ''
    tags = [tag.strip() for tag in tags_raw.split(',') if tag.strip()]
    title = (heading_match.group('title') or '').strip() or None
    return SessionLogSummary(
        timestamp=heading_match.group('timestamp'),
        tags=tags,
        title=title,
        next_items=next_items,
    )


def _extract_root_snapshot_rows(memory_content: str) -> list[dict[str, str]] | None:
    """Extract rows from the root change volatile snapshot table."""
    lines = memory_content.splitlines()

    try:
        start = next(i for i, line in enumerate(lines) if line.startswith('## Sub-Change Status'))
    except StopIteration:
        return None

    table_lines: list[str] = []
    for idx in range(start + 1, len(lines)):
        stripped = lines[idx].strip()
        if stripped.startswith('## '):
            break
        if stripped.startswith('|'):
            table_lines.append(stripped)

    if len(table_lines) < 3:
        return None

    def _split_row(row: str) -> list[str]:
        return [cell.strip() for cell in row.strip('|').split('|')]

    headers = _split_row(table_lines[0])
    rows: list[dict[str, str]] = []
    for row in table_lines[2:]:
        cells = _split_row(row)
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells, strict=False)))

    return rows or None


def _extract_linked_request_paths(change: ChangeInfo) -> list[str]:
    """Extract linked request source paths from frontmatter."""
    references = change.frontmatter.get('reference', [])
    if not isinstance(references, list):
        return []

    linked: list[str] = []
    for ref in references:
        if not isinstance(ref, dict) or ref.get('type') != 'request':
            continue
        source = ref.get('source')
        if isinstance(source, str) and source:
            linked.append(source)
    return linked


def summarize_change(change_path: Path, cwd: Path | None = None) -> ChangeStatusSummary:
    """Build a read-only local dashboard summary for a change."""
    base = cwd or Path.cwd()
    change = parse_change(change_path)
    raw_change_type = change.frontmatter.get('change-type', '')
    change_type = raw_change_type if isinstance(raw_change_type, str) else ''

    memory_file = change_path / 'memory.md'
    if not memory_file.exists():
        memory_file = change_path / 'handover.md'  # backward compat
    memory_content = memory_file.read_text(encoding='utf-8') if memory_file.exists() else ''

    source_links = {
        'spec': _display_path(change_path / 'spec.md', base),
        'tasks': _display_path(change_path / 'tasks.md', base),
        'memory': _display_path(memory_file, base),
    }
    research_file = change_path / 'reference' / 'status-research.md'
    if research_file.exists():
        source_links['research'] = _display_path(research_file, base)

    return ChangeStatusSummary(
        name=change.name,
        path=_display_path(change_path, base),
        status=change.status,
        change_type=change_type,
        tasks_done=change.progress['done'],
        tasks_total=change.progress['total'],
        updated=_extract_updated(memory_content),
        linked_requests=_extract_linked_request_paths(change),
        latest_log=_extract_latest_session_log(memory_content),
        root_snapshot_rows=_extract_root_snapshot_rows(memory_content),
        source_links=source_links,
    )


def create_change(
    sspec_root: Path,
    change_name: str,
    *,
    is_root: bool = False,
    scaffold: list[str] | None = None,
) -> Path:
    """Create a new change directory with base files + optional scaffolded files.

    Base files (always created): spec.md, tasks.md, memory.md
    Additional scaffold types: design (single only), revision (single only)

    Args:
        sspec_root: Path to .sspec directory
        change_name: Name for the change
        is_root: If True, use root change templates (phase-level coordination)
        scaffold: Additional file types to scaffold at creation time
    """

    # Normalize name: lowercase, replace spaces with hyphens, remove invalid chars
    change_name = re.sub(r'\s+', '-', change_name.strip().lower())
    change_name = re.sub(r'[^a-z0-9\-]', '', change_name)

    if not change_name:
        raise InvalidChangeNameError('Invalid change name')

    # Validate scaffold types
    allowed_types = SCAFFOLD_ROOT_TYPES if is_root else SCAFFOLD_SINGLE_TYPES
    for s in scaffold or []:
        if s not in allowed_types:
            raise InvalidChangeNameError(
                f"Scaffold type '{s}' not valid for {'root' if is_root else 'single'} change. "
                f'Allowed: {", ".join(sorted(allowed_types))}'
            )

    # Generate timestamped name: <yy-MM-ddTHH-mm>_<name>
    timestamp = datetime.now().strftime('%y-%m-%dT%H-%M')
    change_file_name = f'{timestamp}_{change_name}'

    change_path = sspec_root / CHANGES_DIR / change_file_name
    if change_path.exists():
        raise ChangeExistsError(f"Change '{change_file_name}' already exists")

    project_root = sspec_root.parent
    template_subdir = 'change-root' if is_root else 'change'
    template_dir = get_template_dir() / template_subdir
    replacements = _build_template_replacements(change_name, project_root)

    change_path.mkdir(parents=True, exist_ok=True)

    # Always create base files
    base_files = CHANGE_BASE_FILES
    for file_name in base_files:
        copy_template(template_dir / file_name, change_path / file_name, replacements)

    # Scaffold additional files
    for s in scaffold or []:
        if s == 'revision':
            _scaffold_revision(change_path, template_dir, replacements, title=change_name)
        else:
            tpl_file = SCAFFOLD_FILE_MAP[s]
            copy_template(template_dir / tpl_file, change_path / tpl_file, replacements)

    (change_path / 'reference').mkdir(exist_ok=True)

    return change_path


def _build_template_replacements(change_name: str, project_root: Path) -> dict[str, str]:
    """Build the standard template variable replacements dict."""
    return {
        'CHANGE_NAME': change_name,
        'TIME': datetime.now().isoformat(timespec='seconds'),
        'GIT': _render_git_snapshot(project_root),
    }


def scaffold_change_file(
    sspec_root: Path,
    change_path: Path,
    file_type: str,
    *,
    title: str | None = None,
) -> Path:
    """Scaffold a single file into an existing change directory.

    Args:
        sspec_root: Path to .sspec directory
        change_path: Path to the change directory
        file_type: One of 'spec', 'tasks', 'design', 'revision'
        title: Required for revision type, used in filename and template

    Returns:
        Path to the created file

    Raises:
        ChangeExistsError: If the file already exists (non-revision)
        InvalidChangeNameError: If the file_type is not valid for this change type
    """
    # Determine change type from spec.md frontmatter
    spec_file = change_path / 'spec.md'
    is_root = False
    if spec_file.exists():
        content = spec_file.read_text(encoding='utf-8')
        meta, _ = parse_frontmatter(content)
        is_root = meta.get('change-type') == 'root'

    allowed_types = SCAFFOLD_ROOT_TYPES if is_root else SCAFFOLD_SINGLE_TYPES
    if file_type not in allowed_types:
        raise InvalidChangeNameError(
            f"Scaffold type '{file_type}' not valid for {'root' if is_root else 'single'} change. "
            f'Allowed: {", ".join(sorted(allowed_types))}'
        )

    project_root = sspec_root.parent
    template_subdir = 'change-root' if is_root else 'change'
    template_dir = get_template_dir() / template_subdir

    # Extract change_name from directory name (after timestamp_)
    dir_name = change_path.name
    change_name = dir_name.split('_', 1)[1] if '_' in dir_name else dir_name
    replacements = _build_template_replacements(change_name, project_root)

    if file_type == 'revision':
        return _scaffold_revision(
            change_path, template_dir, replacements, title=title or 'untitled'
        )

    tpl_file = SCAFFOLD_FILE_MAP[file_type]
    target = change_path / tpl_file
    if target.exists():
        raise ChangeExistsError(f"File '{tpl_file}' already exists in {change_path.name}")

    copy_template(template_dir / tpl_file, target, replacements)
    return target


def _scaffold_revision(
    change_path: Path,
    template_dir: Path,
    replacements: dict[str, str],
    *,
    title: str,
) -> Path:
    """Create a numbered revision file in the change's revisions/ directory."""
    revisions_dir = change_path / 'revisions'
    revisions_dir.mkdir(exist_ok=True)

    # Find next revision number
    existing = sorted(revisions_dir.glob('*.md'))
    next_num = 1
    for f in existing:
        match = re.match(r'(\d+)-', f.name)
        if match:
            next_num = max(next_num, int(match.group(1)) + 1)

    # Normalize title for filename
    slug = re.sub(r'\s+', '-', title.strip().lower())
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    filename = f'{next_num:03d}-{slug}.md'

    rev_replacements = {
        **replacements,
        'N': str(next_num),
        'TITLE': title,
    }

    tpl = template_dir / 'revision.md'
    target = revisions_dir / filename
    copy_template(tpl, target, rev_replacements)
    return target


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

    return sorted(changes, key=_change_sort_key)


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
    _rewrite_references_after_change_archive(sspec_root, name, archive_path)

    return archive_path


def _rewrite_references_after_change_archive(
    sspec_root: Path, old_change_dir_name: str, new_archive_path: Path
) -> None:
    """Update references after archiving a change.

    When change is moved to archive/, all references to it need updated paths.
    Searches in: requests/, changes/, asks/, tmp/ (including archive subdirs).
    """
    # New archive path relative to sspec_root
    new_spec_relative = new_archive_path.relative_to(sspec_root.parent).as_posix()

    # Update all relevant markdown files via exact path replacement.
    old_pattern = f'.sspec/changes/{old_change_dir_name}'
    dirs_to_update = [
        sspec_root / CHANGES_DIR,
        sspec_root / REQUEST_DIR,
        sspec_root / 'asks',
        sspec_root / 'tmp',
    ]
    update_references_in_dirs(
        dirs=dirs_to_update,
        replacements={old_pattern: new_spec_relative},
        file_pattern='*.md',
    )


def validate_change(change_path: Path) -> list[str]:
    """Validate change directory structure and content quality.

    Returns a list of warning/issue strings. Empty list = all good.
    """
    issues: list[str] = []

    # Check base required files (spec.md + tasks.md + memory.md)
    for fname in CHANGE_BASE_FILES:
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

        # Check for new spec structure (## Problem Statement, ## Proposed Solution)
        # or legacy structure (## A., ## B.) — support both
        new_sections = ['## Problem Statement', '## Proposed Solution']
        legacy_sections = ['## A.', '## B.']
        has_new = any(s in body for s in new_sections)
        has_legacy = any(s in body for s in legacy_sections)

        check_sections = (
            new_sections if has_new else legacy_sections if has_legacy else new_sections
        )
        for section in check_sections:
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

    memory_file = change_path / 'memory.md'
    if not memory_file.exists():
        memory_file = change_path / 'handover.md'  # backward compat
    if memory_file.exists():
        content = memory_file.read_text(encoding='utf-8')
        # Support both new (## State) and legacy (## Background) formats
        has_state = '## State' in content
        if '## Background' in content and not has_state:
            bg_idx = content.index('## Background')
            next_heading = content.find('\n## ', bg_idx + 13)
            bg_body = content[bg_idx:next_heading] if next_heading > 0 else content[bg_idx:]
            lines = [
                line
                for line in bg_body.split('\n')
                if line.strip() and not line.startswith('#') and not line.strip().startswith('<!--')
            ]
            if len(lines) == 0:
                issues.append('memory.md: Background section empty')

    return issues
