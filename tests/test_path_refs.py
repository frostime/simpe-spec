"""Tests for path reference rewriting utilities."""

from __future__ import annotations

from pathlib import Path

from sspec.libs.path_refs import update_references_in_dirs


def test_update_references_matches_nested_patterns_like_rglob(tmp_path: Path):
    base = tmp_path / 'base'
    target = base / 'a' / 'b' / 'note.md'
    target.parent.mkdir(parents=True)
    target.write_text('ref: .sspec/changes/demo', encoding='utf-8')

    changed = update_references_in_dirs(
        dirs=[base],
        replacements={'.sspec/changes/demo': '.sspec/changes/archive/demo'},
        file_pattern='b/*.md',
        verbose=False,
    )

    assert changed == 1
    assert '.sspec/changes/archive/demo' in target.read_text(encoding='utf-8')


def test_update_references_skips_archive_tree_when_requested(tmp_path: Path):
    base = tmp_path / 'base'
    normal = base / 'notes.md'
    archived = base / 'archive' / 'old.md'
    archived.parent.mkdir(parents=True)
    normal.parent.mkdir(parents=True, exist_ok=True)

    normal.write_text('ref: .sspec/changes/demo', encoding='utf-8')
    archived.write_text('ref: .sspec/changes/demo', encoding='utf-8')

    changed = update_references_in_dirs(
        dirs=[base],
        replacements={'.sspec/changes/demo': '.sspec/changes/archive/demo'},
        include_archived=False,
        verbose=False,
    )

    assert changed == 1
    assert '.sspec/changes/archive/demo' in normal.read_text(encoding='utf-8')
    assert '.sspec/changes/demo' in archived.read_text(encoding='utf-8')


def test_update_references_handles_walk_errors_without_crashing(tmp_path: Path, monkeypatch):
    base = tmp_path / 'base'
    base.mkdir(parents=True)
    ok_file = base / 'ok.md'
    ok_file.write_text('ref: .sspec/changes/demo', encoding='utf-8')

    def fake_walk(_base, topdown=True, followlinks=False, onerror=None):
        if onerror:
            onerror(OSError('broken link'))
        yield str(base), [], ['ok.md']

    import sspec.libs.path_refs as path_refs

    monkeypatch.setattr(path_refs.os, 'walk', fake_walk)

    changed = update_references_in_dirs(
        dirs=[base],
        replacements={'.sspec/changes/demo': '.sspec/changes/archive/demo'},
        verbose=False,
    )

    assert changed == 1
    assert '.sspec/changes/archive/demo' in ok_file.read_text(encoding='utf-8')
