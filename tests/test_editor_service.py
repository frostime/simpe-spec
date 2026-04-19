"""Tests for editor command resolution order."""

from __future__ import annotations

from pathlib import Path

import pytest

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


def test_open_in_editor_quotes_placeholder_file_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    sspec_root = tmp_path / '.sspec'
    sspec_root.mkdir()

    file_path = sspec_root / 'tmp' / '26-04-19T15-26_claude \u53cd\u9988\u7684\u4fe1\u606f.md'
    file_path.parent.mkdir(parents=True)
    file_path.write_text('', encoding='utf-8')

    monkeypatch.setattr(
        editor_service,
        'get_editor_command',
        lambda *args, **kwargs: 'code {file}',
    )

    captured: dict[str, str | bool] = {}

    def _fake_run(cmd: str, *, shell: bool, check: bool) -> None:
        captured['cmd'] = cmd
        captured['shell'] = shell
        captured['check'] = check

    monkeypatch.setattr(editor_service.subprocess, 'run', _fake_run)

    opened = editor_service.open_in_editor(file_path=file_path, sspec_root=sspec_root)

    path_str = str(file_path)
    assert opened is True
    assert captured['shell'] is True
    assert captured['check'] is True
    assert path_str in str(captured['cmd'])
    assert f'"{path_str}"' in str(captured['cmd']) or f"'{path_str}'" in str(captured['cmd'])


def test_open_in_editor_replaces_prequoted_placeholder_without_double_quotes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    sspec_root = tmp_path / '.sspec'
    sspec_root.mkdir()

    file_path = sspec_root / 'tmp' / 'file with space.md'
    file_path.parent.mkdir(parents=True)
    file_path.write_text('', encoding='utf-8')

    monkeypatch.setattr(
        editor_service,
        'get_editor_command',
        lambda *args, **kwargs: 'code "{file}"',
    )

    captured: dict[str, str | bool] = {}

    def _fake_run(cmd: str, *, shell: bool, check: bool) -> None:
        captured['cmd'] = cmd
        captured['shell'] = shell
        captured['check'] = check

    monkeypatch.setattr(editor_service.subprocess, 'run', _fake_run)

    opened = editor_service.open_in_editor(file_path=file_path, sspec_root=sspec_root)

    path_str = str(file_path)
    assert opened is True
    assert captured['shell'] is True
    assert captured['check'] is True
    assert str(captured['cmd']).count(path_str) == 1
    assert f'""{path_str}""' not in str(captured['cmd'])
