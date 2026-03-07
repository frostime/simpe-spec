"""Core sspec functionality."""

import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TypedDict

SSPEC_DIR = '.sspec'
SKILLS_DIR = 'skills'
WORKSPACE_DIRS = ['.github', '.claude', '.agents']
SKILL_SUBDIR = 'skills'
CHANGES_DIR = 'changes'
REQUEST_DIR = 'requests'
SPEC_DOCS_DIR = 'spec-docs'
ARCHIVE_DIR = 'archive'

# Schema version - increment when template structure changes
SCHEMA_VERSION = '3.0'

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
CHANGE_ROOT_TEMPLATE_FILES: list[str] = ['spec.md', 'tasks.md', 'handover.md']

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


@dataclass(frozen=True, slots=True)
class ChangeInfo:
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
    frontmatter: dict[str, str | list | dict]


@dataclass(frozen=True, slots=True)
class SessionLogSummary:
    """Latest session log summary extracted from handover.md."""

    timestamp: str | None
    tags: list[str]
    title: str | None
    next_items: list[str]


@dataclass(frozen=True, slots=True)
class ChangeStatusSummary:
    """Read-only local dashboard summary for a change."""

    name: str
    path: str
    status: str
    change_type: str
    tasks_done: int
    tasks_total: int
    updated: str | None
    linked_requests: list[str]
    latest_log: SessionLogSummary | None
    root_snapshot_rows: list[dict[str, str]] | None
    source_links: dict[str, str]


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


def list_template_skills() -> list[Path]:
    """List skill template directories that contain SKILL.md."""

    template_skills_dir = get_template_dir() / 'skills'
    if not template_skills_dir.exists():
        return []

    return [d for d in template_skills_dir.iterdir() if d.is_dir() and (d / 'SKILL.md').exists()]


def configure_stdio_error_fallback() -> None:
    """Prevent UnicodeEncodeError on non-UTF terminals.

    Some Windows shells still run with legacy encodings (for example GBK/cp936).
    Reconfiguring stdout/stderr to use ``errors='replace'`` keeps CLI output from
    crashing when symbols like emoji are rendered.
    """

    _set_stream_error_fallback(sys.stdout)
    _set_stream_error_fallback(sys.stderr)


def _set_stream_error_fallback(stream: object) -> None:
    """Best-effort stream reconfigure; no-op when unsupported."""

    reconfigure = getattr(stream, 'reconfigure', None)
    if not callable(reconfigure):
        return

    encoding = getattr(stream, 'encoding', None)
    errors = getattr(stream, 'errors', None)
    if not encoding or errors == 'replace':
        return

    try:
        reconfigure(errors='replace')
    except Exception:
        # Never block CLI startup due to stream quirks.
        return
