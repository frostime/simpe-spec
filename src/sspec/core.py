"""Core sspec functionality."""

import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

SSPEC_DIR = ".sspec"
KNOWLEDGE_DIR = "knowledge"
CHANGES_DIR = "changes"
ARCHIVE_DIR = "archive"
PROMPTS_DIR = "prompts"

# Schema version - increment when template structure changes
# Major: breaking changes requiring manual migration
# Minor: additive changes (new files, new sections)
SCHEMA_VERSION = "1.5"

# File categories for tracking and updates
UPDATABLE_FILES = [
    "AGENTS.md",
    "prompts/archive.md",
    "prompts/context.md",
    "prompts/handover.md",
    "prompts/pivot.md",
    "prompts/propose.md",
    "prompts/requests.md",
    "prompts/status.md",
]

USER_FILES = ["knowledge/index.md", "handover.md"]

# Files that should never be touched during update
PROTECTED_PATTERNS = ["changes/*", "requests/*"]


class SspecNotFoundError(Exception):
    """Raised when sspec project is not found."""

    pass


def find_sspec_root(start: Optional[Path] = None) -> Optional[Path]:
    """Find .sspec directory by walking up from start path."""
    path = start or Path.cwd()
    for parent in [path] + list(path.parents):
        sspec_path = parent / SSPEC_DIR
        if sspec_path.is_dir() and (sspec_path / "AGENTS.md").exists():
            return sspec_path
    return None


def get_sspec_root() -> Path:
    """Get .sspec directory or raise error."""
    root = find_sspec_root()
    if root is None:
        raise SspecNotFoundError("Not a sspec project")
    return root


def get_template_dir() -> Path:
    """Get templates directory from package."""
    return Path(__file__).parent / "templates"


def copy_template(src: Path, dest: Path, replacements: Optional[dict] = None) -> None:
    """Copy template file/dir with variable replacements."""
    replacements = replacements or {}

    if src.is_dir():
        dest.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            copy_template(item, dest / item.name, replacements)
    else:
        content = src.read_text(encoding="utf-8")
        for key, value in replacements.items():
            content = content.replace(f"{{{{{key}}}}}", value)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")


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

    return sorted(changes, key=lambda x: (x["archived"], x["name"]))


def parse_change(change_path: Path, archived: bool = False) -> dict:
    """Parse change directory into structured data."""
    tasks_file = change_path / "tasks.md"
    status = "UNKNOWN"
    progress = {"done": 0, "total": 0}
    has_pivot = False
    has_blockers = False

    if tasks_file.exists():
        content = tasks_file.read_text(encoding="utf-8")

        # Extract status - try HTML comment format first, then fallback to backticks
        # status_match = re.search(r"<!--\s*STATUS:\s*([A-Z_]+)\s*-->", content)
        # if not status_match:
        #     status_match = re.search(r"`([A-Z_]+)`", content)

        status_match = re.search(r"\s*STATUS::([A-Z_]+)\s*", content)
        if status_match:
            status = status_match.group(1)

        # Count tasks
        total = len(re.findall(r"- \[[ x]\]", content))
        done = len(re.findall(r"- \[x\]", content))
        progress = {"done": done, "total": total}

        # Check for pivots
        has_pivot = bool(re.search(r"## Pivot\s*\n\s*###", content))

        # Check for blockers
        has_blockers = bool(re.search(r"## Blockers\s*\n\s*[^\n#]", content))

    return {
        "name": change_path.name,
        "path": change_path,
        "status": status,
        "progress": progress,
        "has_pivot": has_pivot,
        "has_blockers": has_blockers,
        "archived": archived,
    }


def create_change(sspec_root: Path, name: str) -> Path:
    """Create a new change directory from template."""
    # Normalize name
    name = re.sub(r"\s+", "-", name.strip().lower())
    name = re.sub(r"[^a-z0-9\-]", "", name)

    if not name:
        raise ValueError("Invalid change name")

    change_path = sspec_root / CHANGES_DIR / name
    if change_path.exists():
        raise ValueError(f"Change '{name}' already exists")

    template_dir = get_template_dir() / "change"
    copy_template(template_dir, change_path, {"CHANGE_NAME": name})

    return change_path


def archive_change(sspec_root: Path, name: str) -> Path:
    """Archive a completed change."""
    change_path = sspec_root / CHANGES_DIR / name
    if not change_path.exists():
        raise ValueError(f"Change '{name}' not found")

    archive_dir = sspec_root / CHANGES_DIR / ARCHIVE_DIR
    archive_dir.mkdir(parents=True, exist_ok=True)

    date_prefix = datetime.now().strftime("%Y-%m-%d")
    archive_name = f"{date_prefix}_{name}"

    # Handle name conflicts
    archive_path = archive_dir / archive_name
    counter = 1
    while archive_path.exists():
        archive_path = archive_dir / f"{archive_name}_{counter}"
        counter += 1

    shutil.move(str(change_path), str(archive_path))
    return archive_path
