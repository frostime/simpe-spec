"""Core sspec functionality."""

import re
import shutil
from collections.abc import Mapping
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TypedDict

import yaml

SSPEC_DIR = '.sspec'
SKILLS_DIR = 'skills'
WORKSPACE_DIRS = ['.github', '.claude', '.agent']
SKILL_SUBDIR = 'skills'
CHANGES_DIR = 'changes'
ARCHIVE_DIR = 'archive'

# Schema version - increment when template structure changes
SCHEMA_VERSION = '5.2'

# Files tracked for updates (relative to .sspec/)
# NOTE: Empty by design. The .sspec/ directory contains user-managed files that should
# not be auto-updated. The 'project update' command specifically handles updating the
# root AGENTS.md file's SSPEC protocol block via update_root_agents_block().
# If future templates need auto-update support, add them here.
UPDATABLE_FILES: list[str] = []


# User-managed files tracked for changes but not auto-updated
USER_FILES = ['project.md', 'spec-docs/README.md']

# Change template source files
CHANGE_TEMPLATE_FILES = ['spec.md', 'tasks.md', 'handover.md']

# Files that should never be touched during update
PROTECTED_PATTERNS = ['changes/*', 'requests/*', 'skills/*', 'spec-docs/*']


class SspecError(Exception):
    """Base sspec exception."""


class SspecNotFoundError(SspecError):
    """Raised when sspec project is not found."""


class ChangeNotFoundError(SspecError):
    """Raised when change is not found."""


class ChangeExistsError(SspecError):
    """Raised when change already exists."""


class InvalidChangeNameError(SspecError):
    """Raised when change name is invalid."""


class ChangeStatus(str, Enum):
    """Canonical change status values."""

    PLANNING = 'PLANNING'
    DOING = 'DOING'
    BLOCKED = 'BLOCKED'
    REVIEW = 'REVIEW'
    DONE = 'DONE'
    CLOSED = 'CLOSED'


class RequestStatus(str, Enum):
    """Canonical request status values."""

    OPEN = 'OPEN'
    DOING = 'DOING'
    DONE = 'DONE'
    BLOCKED = 'BLOCKED'
    CLOSED = 'CLOSED'


# Status alias map (legacy compatibility and common variants)
STATUS_ALIASES: dict[str, str] = {
    # ===== ChangeStatus Aliases =====
    # PLANNING
    'DESIGN': ChangeStatus.PLANNING.value,
    '设计中': ChangeStatus.PLANNING.value,

    # DOING
    'DEV': ChangeStatus.DOING.value,
    'IN_DEV': ChangeStatus.DOING.value,
    'IN_PROGRESS': ChangeStatus.DOING.value,
    'IN-PROGRESS': ChangeStatus.DOING.value,
    'INPROGRESS': ChangeStatus.DOING.value,
    '进行中': ChangeStatus.DOING.value,
    '开发中': ChangeStatus.DOING.value,

    # BLOCKED
    'HANGUP': ChangeStatus.BLOCKED.value,
    'WAIT': ChangeStatus.BLOCKED.value,
    '已阻塞': ChangeStatus.BLOCKED.value,
    '挂起': ChangeStatus.BLOCKED.value,

    # REVIEW
    'IN_REVIEW': ChangeStatus.REVIEW.value,
    'IN-REVIEW': ChangeStatus.REVIEW.value,
    'REVIEWING': ChangeStatus.REVIEW.value,
    '待审核': ChangeStatus.REVIEW.value,
    '审核中': ChangeStatus.REVIEW.value,

    # DONE
    'COMPLETED': ChangeStatus.DONE.value,
    'FINISHED': ChangeStatus.DONE.value,
    '已完成': ChangeStatus.DONE.value,

    # CLOSED
    'CANCELLED': ChangeStatus.CLOSED.value,
    'CANCELED': ChangeStatus.CLOSED.value,
    'ARCHIVED': ChangeStatus.CLOSED.value,
    '已关闭': ChangeStatus.CLOSED.value,

    # ===== RequestStatus Aliases =====
    # OPEN
    'TODO': RequestStatus.OPEN.value,
    'TO_DO': RequestStatus.OPEN.value,
    'TO-DO': RequestStatus.OPEN.value,
    '待办': RequestStatus.OPEN.value,

    # DONE
    'RESOLVED': RequestStatus.DONE.value,
}



def normalize_status(raw: str, valid_enum: type[Enum]) -> str:
    """Normalize status value using aliases and enum validation."""

    upper = raw.strip().upper()
    normalized = STATUS_ALIASES.get(upper, upper)
    try:
        return valid_enum(normalized).value
    except ValueError:
        return normalized


class ChangeInfo(TypedDict):
    """Structured change information."""

    name: str
    path: Path
    status: str
    type: str
    description: str
    progress: dict[str, int]
    has_pivot: bool
    has_blockers: bool
    archived: bool


class SkillInfo(TypedDict):
    """Structured skill information."""

    file: str
    path: Path
    skill: str
    description: str


def find_sspec_root(start: Path | None = None) -> Path | None:
    """Find .sspec directory by walking up from start path."""

    path = start or Path.cwd()
    for parent in [path] + list(path.parents):
        sspec_path = parent / SSPEC_DIR
        if sspec_path.is_dir():
            markers = ['project.md']
            if any((sspec_path / marker).exists() for marker in markers):
                return sspec_path
    return None


def get_sspec_root() -> Path:
    """Get .sspec directory or raise error."""

    root = find_sspec_root()
    if root is None:
        raise SspecNotFoundError('Not a sspec project')
    return root


def get_template_dir() -> Path:
    """Get templates directory from package."""
    return Path(__file__).parent / 'templates'


def copy_template(src: Path, dest: Path, replacements: dict | None = None) -> None:
    """Copy template file/dir with variable replacements."""

    replacements = replacements or {}

    if src.is_dir():
        dest.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            copy_template(item, dest / item.name, replacements)
    else:
        content = src.read_text(encoding='utf-8')
        rendered = render_template(content, replacements)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(rendered, encoding='utf-8')


def render_template(content: str, replacements: Mapping[str, str]) -> str:
    """Render {{var}} placeholders with provided replacements."""

    def _replace(match: re.Match) -> str:
        key = match.group(1).strip()
        return str(replacements.get(key, ''))

    return re.sub(r'{{\s*(.+?)\s*}}', _replace, content)


def parse_skill_metadata(
    skill_path: Path, replacements: Mapping[str, str] | None = None
) -> dict:
    """Parse YAML front matter from a SKILL.md file."""

    if not skill_path.exists():
        return {}

    content = skill_path.read_text(encoding='utf-8')
    if replacements:
        content = render_template(content, replacements)
    if not content.startswith('---'):
        return {}

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}

    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


def get_workspace_skill_targets(
    project_root: Path, primary_loc: str | None = None
) -> list[Path]:
    """Return workspace directories that should host skills.

    Args:
        project_root: Project root directory
        primary_loc: Primary location for skills (.claude, .github, or .sspec)
                    If specified, only install to primary_loc and .sspec (for compatibility)
                    If None, auto-detect existing workspace dirs

    Returns:
        List of target directories for skill installation
    """
    targets: list[Path] = []

    if primary_loc:
        # User specified primary location - use it + .sspec for backward compatibility
        if primary_loc != '.sspec':
            primary_path = project_root / primary_loc / SKILL_SUBDIR
            targets.append(primary_path)
        # Always include .sspec/skills for backward compatibility
        targets.append(project_root / SSPEC_DIR / SKILL_SUBDIR)
    else:
        # Auto-detect mode: install to all existing workspace dirs
        for ws_dir in WORKSPACE_DIRS:
            ws_path = project_root / ws_dir
            if ws_path.is_dir():
                targets.append(ws_path / SKILL_SUBDIR)
        # Always include .sspec/skills for backward compatibility
        targets.append(project_root / SSPEC_DIR / SKILL_SUBDIR)

    return targets


def list_template_skills() -> list[Path]:
    """List skill template directories that contain SKILL.md."""

    template_skills_dir = get_template_dir() / 'skills'
    if not template_skills_dir.exists():
        return []

    return [
        d
        for d in template_skills_dir.iterdir()
        if d.is_dir() and (d / 'SKILL.md').exists()
    ]


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

    return sorted(changes, key=lambda x: (x['archived'], x['name']))


def list_skills(sspec_root: Path) -> list[SkillInfo]:
    """List all skills found in skills directory."""

    skills: list[SkillInfo] = []
    skills_dir = sspec_root / SKILLS_DIR

    if not skills_dir.exists():
        return skills

    for entry in skills_dir.iterdir():
        if entry.is_file() and entry.suffix == '.md':
            meta = parse_skill_metadata(entry)
            if meta.get('skill'):
                skills.append(
                    {
                        'file': entry.name,
                        'path': entry,
                        'skill': str(meta['skill']),
                        'description': str(meta.get('description', '')),
                    }
                )
        elif entry.is_dir():
            skill_file = entry / 'SKILL.md'
            meta = parse_skill_metadata(skill_file)
            if meta.get('skill'):
                skills.append(
                    {
                        'file': f'{entry.name}/SKILL.md',
                        'path': skill_file,
                        'skill': str(meta['skill']),
                        'description': str(meta.get('description', '')),
                    }
                )

    return sorted(skills, key=lambda x: x['skill'])


def parse_change(change_path: Path, archived: bool = False) -> ChangeInfo:
    """Parse change directory into structured data."""
    from sspec.libs.md_yaml import parse_frontmatter

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

    return {
        'name': change_name,
        'path': change_path,
        'status': status,
        'type': change_type,
        'description': description,
        'progress': progress,
        'has_pivot': has_pivot,
        'has_blockers': has_blockers,
        'archived': archived,
    }


def create_change(sspec_root: Path, change_name: str) -> Path:
    """Create a new change directory with spec.md, tasks.md, and handover.md."""

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

    template_dir = get_template_dir() / 'change'
    replacements = {
        'CHANGE_NAME': change_name,
        'TIME': datetime.now().isoformat(timespec='seconds'),
    }

    change_path.mkdir(parents=True, exist_ok=True)

    for file_name in CHANGE_TEMPLATE_FILES:
        copy_template(template_dir / file_name, change_path / file_name, replacements)

    return change_path


def archive_change(
    sspec_root: Path, change_info: ChangeInfo
) -> Path:
    """Archive a completed change.

    Moves the change to archive/ directory and adds 'archived' timestamp to spec.md frontmatter.
    Name is preserved (no date prefix added).
    """

    change_path = change_info['path']
    name = change_path.name

    # if not force:
    #     if change_info['status'] != ChangeStatus.DONE.value:
    #         raise ValueError(
    #             f"Change '{name}' status is {change_info['status']}, not DONE. "
    #             f"Use --force to archive anyway."
    #         )

    # Add archived timestamp to spec.md frontmatter
    spec_file = change_path / 'spec.md'
    if spec_file.exists():
        from sspec.libs.md_yaml import update_frontmatter

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
    return archive_path
