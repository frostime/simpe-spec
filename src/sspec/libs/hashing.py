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
