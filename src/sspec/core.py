"""Core sspec functionality."""

import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Mapping, Optional

SSPEC_DIR = '.sspec'
KNOWLEDGE_DIR = 'knowledge'
CHANGES_DIR = 'changes'
ARCHIVE_DIR = 'archive'

# Schema version - increment when template structure changes
SCHEMA_VERSION = '3.0'

# Files tracked for updates
UPDATABLE_FILES: list[str] = []
USER_FILES = ['project.md', 'handover.md']

# Files that should never be touched during update
PROTECTED_PATTERNS = ['changes/*', 'requests/*', 'knowledge/*']


class SspecNotFoundError(Exception):
    """Raised when sspec project is not found."""
    pass


def find_sspec_root(start: Optional[Path] = None) -> Optional[Path]:
    """Find .sspec directory by walking up from start path."""
    path = start or Path.cwd()
    for parent in [path] + list(path.parents):
        sspec_path = parent / SSPEC_DIR
        if sspec_path.is_dir():
            markers = ['project.md', 'AGENTS.md', 'handover.md']
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


def copy_template(src: Path, dest: Path, replacements: Optional[dict] = None) -> None:
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


def list_changes(sspec_root: Path, include_archived: bool = False) -> list[dict]:
    """List all changes with their status."""
    changes = []
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


def parse_change(change_path: Path, archived: bool = False) -> dict:
    """Parse change directory into structured data."""
    spec_file = change_path / 'spec.md'
    tasks_file = change_path / 'tasks.md'
    status = 'UNKNOWN'
    progress = {'done': 0, 'total': 0}
    has_pivot = False
    has_blockers = False
    spec_progress: Optional[dict[str, int]] = None

    if spec_file.exists():
        content = spec_file.read_text(encoding='utf-8')

        # Extract status (supports legacy STATUS:: and new **Status** markers)
        status_match = re.search(r'\*\*Status\*\*:\s*([A-Za-z_]+)', content)
        if not status_match:
            status_match = re.search(r'\s*STATUS::([A-Z_]+)\s*', content)
        if status_match:
            status = status_match.group(1).upper()

        checkbox_pattern = r'- \[[^\]]\]'
        total = len(re.findall(checkbox_pattern, content))
        done = len(re.findall(r'- \[[xX]\]', content))
        if total > 0:
            spec_progress = {'done': done, 'total': total}

        # Check for pivots
        has_pivot = bool(re.search(r'PIVOT', content))

        # Check for blockers (STATUS::BLOCKED)
        has_blockers = status == 'BLOCKED'

    if tasks_file.exists():
        content = tasks_file.read_text(encoding='utf-8')
        checkbox_pattern = r'- \[[ xX~\-]\]'
        total = len(re.findall(checkbox_pattern, content))
        done = len(re.findall(r'- \[[xX]\]', content))
        progress = {'done': done, 'total': total}
    elif spec_progress:
        progress = spec_progress

    return {
        'name': change_path.name,
        'path': change_path,
        'status': status,
        'progress': progress,
        'has_pivot': has_pivot,
        'has_blockers': has_blockers,
        'archived': archived,
    }


def create_change(sspec_root: Path, name: str) -> Path:
    """Create a new change directory with spec.md, tasks.md, and handover.md."""
    # Normalize name
    name = re.sub(r'\s+', '-', name.strip().lower())
    name = re.sub(r'[^a-z0-9\-]', '', name)

    if not name:
        raise ValueError('Invalid change name')

    change_path = sspec_root / CHANGES_DIR / name
    if change_path.exists():
        raise ValueError(f"Change '{name}' already exists")

    template_dir = get_template_dir() / 'change'
    replacements = {
        'CHANGE_NAME': name,
        'TIME': datetime.now().isoformat(timespec='seconds'),
    }

    # Create change directory
    change_path.mkdir(parents=True, exist_ok=True)

    # Copy spec.md
    copy_template(template_dir / 'spec.md', change_path / 'spec.md', replacements)

    # Copy tasks.md
    copy_template(template_dir / 'tasks.md', change_path / 'tasks.md', replacements)

    # Copy handover.md
    copy_template(template_dir / 'handover.md', change_path / 'handover.md', replacements)

    return change_path


def archive_change(sspec_root: Path, name: str) -> Path:
    """Archive a completed change."""
    change_path = sspec_root / CHANGES_DIR / name
    if not change_path.exists():
        raise ValueError(f"Change '{name}' not found")

    archive_dir = sspec_root / CHANGES_DIR / ARCHIVE_DIR
    archive_dir.mkdir(parents=True, exist_ok=True)

    date_prefix = datetime.now().strftime('%Y-%m-%d')
    archive_name = f'{date_prefix}_{name}'

    # Handle name conflicts
    archive_path = archive_dir / archive_name
    counter = 1
    while archive_path.exists():
        archive_path = archive_dir / f'{archive_name}_{counter}'
        counter += 1

    shutil.move(str(change_path), str(archive_path))
    return archive_path
