"""Utilities for updating file path references across multiple files."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath


def _matches_rglob_pattern(rel_path: Path, file_pattern: str) -> bool:
    """Match using semantics close to Path.rglob(file_pattern)."""
    rel = PurePosixPath(rel_path.as_posix())
    if rel.match(file_pattern):
        return True
    if file_pattern.startswith('**/'):
        return False
    # rglob() behaves like glob('**/<pattern>')
    return rel.match(f'**/{file_pattern}')


def update_file_references(
    file_path: Path,
    old_patterns: list[str],
    new_path: str,
) -> bool:
    """Update all occurrences of old patterns in a file.

    Args:
        file_path: Path to the file to update
        old_patterns: List of old path patterns to search for
            (sorted longest to shortest internally)
        new_path: The new path to replace old patterns with

    Returns:
        True if file was modified, False otherwise.
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception:
        return False

    sorted_patterns = sorted(old_patterns, key=len, reverse=True)

    updated_content = content
    for pattern in sorted_patterns:
        if pattern in updated_content:
            updated_content = updated_content.replace(pattern, new_path)

    if updated_content != content:
        file_path.write_text(updated_content, encoding='utf-8')
        return True
    return False


def update_references_in_dirs(
    dirs: list[Path],
    replacements: dict[str, str],
    file_pattern: str = '*.md',
    include_archived: bool = True,
    verbose: bool = True,
) -> int:
    """Update path references in all matching files across multiple directories.

    Args:
        dirs: List of directories to search in
        replacements: Mapping of old path -> new path (POSIX style)
        file_pattern: Glob pattern for files to match (default: *.md)
        include_archived: Whether to include files under */archive/*

    Returns:
        Number of files that were modified
    """
    normalized_replacements: list[tuple[list[str], str]] = []
    for old_path, new_path in replacements.items():
        old_patterns = [old_path]
        if '\\' not in old_path:
            old_patterns.append(old_path.replace('/', '\\'))
        normalized_replacements.append((sorted(old_patterns, key=len, reverse=True), new_path))

    modified_count = 0

    gathered_files: list[Path] = []
    for base_dir in dirs:
        if not base_dir.exists():
            continue

        # Use os.walk with followlinks=False to avoid traversing broken links/junctions.
        def _ignore_walk_error(_err: OSError) -> None:
            return

        for dirpath, dirnames, filenames in os.walk(
            base_dir,
            topdown=True,
            followlinks=False,
            onerror=_ignore_walk_error,
        ):
            # Optionally skip archived trees
            try:
                rel_dir_parts = Path(dirpath).relative_to(base_dir).parts
            except ValueError:
                rel_dir_parts = Path(dirpath).parts

            if not include_archived and 'archive' in rel_dir_parts:
                dirnames[:] = []
                continue

            for fname in filenames:
                file_path = Path(dirpath) / fname
                try:
                    rel_path = file_path.relative_to(base_dir)
                except ValueError:
                    continue

                if not _matches_rglob_pattern(rel_path, file_pattern):
                    continue

                try:
                    content = file_path.read_text(encoding='utf-8')
                except Exception:
                    continue

                updated_content = content
                for old_patterns, new_path in normalized_replacements:
                    for pattern in old_patterns:
                        if pattern in updated_content:
                            updated_content = updated_content.replace(pattern, new_path)

                if updated_content != content:
                    file_path.write_text(updated_content, encoding='utf-8')
                    modified_count += 1
                    gathered_files.append(file_path)

    if verbose:
        from .echo import echo

        echo(
            f'Updated {modified_count} files for {len(replacements)} replacement rule(s)', bold=True
        )
        for old_path, new_path in replacements.items():
            echo(f'{old_path} -> {new_path}', fg='cyan')
        cwd = Path('.').resolve()
        for f in gathered_files:
            try:
                display_path = f.relative_to(cwd).as_posix()
            except ValueError:
                display_path = f.as_posix()
            echo(f'  - {display_path}', dim=True)

    return modified_count
