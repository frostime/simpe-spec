"""Tests for editor command resolution order."""

from __future__ import annotations

from pathlib import Path

from sspec.services import editor_service


def test_dotenv_sspec_editor_has_highest_priority(tmp_path: Path):
    sspec_root = tmp_path / '.sspec'
    sspec_root.mkdir()
    (tmp_path / '.env').write_text('SSPEC_EDITOR=zed {file}\n', encoding='utf-8')

    result = editor_service.get_editor_command(
        sspec_root,
        env={'SSPEC_EDITOR': 'nvim {file}'},
        cwd=tmp_path,
    )

    assert result == 'zed {file}'


def test_env_sspec_editor_used_when_dotenv_missing(tmp_path: Path):
    sspec_root = tmp_path / '.sspec'
    sspec_root.mkdir()

    result = editor_service.get_editor_command(
        sspec_root,
        env={'SSPEC_EDITOR': 'nvim {file}'},
        cwd=tmp_path,
    )

    assert result == 'nvim {file}'


def test_editor_fallback_used_when_sspec_editor_missing(tmp_path: Path):
    sspec_root = tmp_path / '.sspec'
    sspec_root.mkdir()

    result = editor_service.get_editor_command(
        sspec_root,
        env={'EDITOR': 'nano'},
        cwd=tmp_path,
    )

    assert result == 'nano'
