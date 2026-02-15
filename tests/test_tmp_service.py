"""Tests for tmp entry creation service."""

from __future__ import annotations

from pathlib import Path

import pytest

from sspec.services.tmp_service import create_tmp_entry


def test_create_tmp_file_with_default_extension(tmp_path: Path):
    sspec_root = tmp_path / '.sspec'
    sspec_root.mkdir()

    result = create_tmp_entry(sspec_root=sspec_root, name='notes', is_dir=False)

    assert result.path == sspec_root / 'tmp' / 'notes.md'
    assert result.path.exists()
    assert result.path.read_text(encoding='utf-8') == ''


def test_create_tmp_dir(tmp_path: Path):
    sspec_root = tmp_path / '.sspec'
    sspec_root.mkdir()

    result = create_tmp_entry(sspec_root=sspec_root, name='scratch', is_dir=True)

    assert result.path == sspec_root / 'tmp' / 'scratch'
    assert result.path.is_dir()


def test_create_tmp_uses_timestamp_when_name_missing(tmp_path: Path):
    sspec_root = tmp_path / '.sspec'
    sspec_root.mkdir()

    result = create_tmp_entry(sspec_root=sspec_root, name=None, is_dir=False)

    assert result.path.parent == sspec_root / 'tmp'
    assert result.path.suffix == '.md'


def test_create_tmp_raises_when_exists(tmp_path: Path):
    sspec_root = tmp_path / '.sspec'
    sspec_root.mkdir()
    existing = sspec_root / 'tmp' / 'exists.md'
    existing.parent.mkdir(parents=True)
    existing.write_text('', encoding='utf-8')

    with pytest.raises(FileExistsError):
        create_tmp_entry(sspec_root=sspec_root, name='exists', is_dir=False)
