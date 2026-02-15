"""Tests for editor command resolution order."""

from __future__ import annotations

from pathlib import Path

from sspec.services import editor_service


class _GlobalConfig:
    def __init__(self, sspec_editor: str):
        self.sspec_editor = sspec_editor


def test_env_sspec_editor_has_highest_priority(monkeypatch, tmp_path: Path):
    sspec_root = tmp_path / '.sspec'
    sspec_root.mkdir()

    monkeypatch.setattr(editor_service, 'get_global_config', lambda: _GlobalConfig('code {file}'))

    result = editor_service.get_editor_command(
        sspec_root,
        env={'SSPEC_EDITOR': 'nvim {file}'},
        cwd=tmp_path,
    )

    assert result == 'nvim {file}'


def test_dotenv_overrides_config(monkeypatch, tmp_path: Path):
    sspec_root = tmp_path / '.sspec'
    sspec_root.mkdir()

    (tmp_path / '.env').write_text('SSPEC_EDITOR=zed {file}\n', encoding='utf-8')
    monkeypatch.setattr(editor_service, 'get_global_config', lambda: _GlobalConfig('code {file}'))

    result = editor_service.get_editor_command(sspec_root, env={}, cwd=tmp_path)

    assert result == 'zed {file}'


def test_global_config_used_when_no_env(monkeypatch, tmp_path: Path):
    sspec_root = tmp_path / '.sspec'
    sspec_root.mkdir()

    monkeypatch.setattr(
        editor_service,
        'get_global_config',
        lambda: _GlobalConfig('cursor --goto {file}'),
    )

    result = editor_service.get_editor_command(sspec_root, env={}, cwd=tmp_path)

    assert result == 'cursor --goto {file}'
