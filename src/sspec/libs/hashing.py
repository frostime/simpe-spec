"""Hashing helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path


def compute_hash(content: str) -> str:
    """Compute a short SHA256 hash of content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]


def compute_file_hash(path: Path) -> str | None:
    """Compute the hash of a text file, or None if missing."""
    if not path.exists():
        return None
    return compute_hash(path.read_text(encoding='utf-8'))


def compute_dir_hash(
    dir_path: Path,
    replacements: dict[str, str] | None = None,
) -> str:
    """Compute a combined hash of all files in a directory.

    Includes file paths in the hash so renames/additions/removals are detected.
    Applies template replacements to .md files.
    """
    replacements = replacements or {}
    hasher = hashlib.sha256()

    for file_path in sorted(dir_path.rglob('*')):
        if not file_path.is_file():
            continue

        # Include relative path in hash (detects renames/moves)
        rel_path = str(file_path.relative_to(dir_path))
        hasher.update(rel_path.encode('utf-8'))

        content = file_path.read_text(encoding='utf-8')
        if file_path.suffix == '.md':
            for old, new in replacements.items():
                content = content.replace(f'{{{{{old}}}}}', new)
        hasher.update(content.encode('utf-8'))

    return hasher.hexdigest()[:16]
