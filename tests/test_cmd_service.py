"""Tests for sspec.services.cmd_service — command registry CRUD and script handling.

NOTE: cmd_service imports sspec.commands.project at module level, which requires
questionary. These tests will be skipped if questionary is not installed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

try:
    from sspec.services.cmd_service import (
        CommandExistsError,
        CommandInfo,
        CommandNotFoundError,
        add_command,
        handle_script_file,
        load_registry,
        remove_command,
        resolve_invoke,
        save_registry,
        suggest_invoke_pattern,
    )

    HAS_CMD_SERVICE = True
except ImportError:
    HAS_CMD_SERVICE = False

pytestmark = pytest.mark.skipif(not HAS_CMD_SERVICE, reason='questionary not installed')


# ---------------------------------------------------------------------------
# Registry load/save
# ---------------------------------------------------------------------------


class TestRegistryIO:
    def test_empty_when_no_file(self, sspec_root: Path):
        assert load_registry(sspec_root) == {}

    def test_save_and_load_roundtrip(self, sspec_root: Path):
        cmds = {
            'build': CommandInfo(
                name='build',
                description='Build project',
                type='cmd-line',
                invoke='make build',
            ),
        }
        save_registry(sspec_root, cmds)
        loaded = load_registry(sspec_root)
        assert 'build' in loaded
        assert loaded['build'].invoke == 'make build'

    def test_corrupt_yaml_returns_empty(self, sspec_root: Path):
        cmd_dir = sspec_root / 'commands'
        cmd_dir.mkdir(parents=True, exist_ok=True)
        (cmd_dir / 'registry.yaml').write_text('{{not yaml', encoding='utf-8')
        assert load_registry(sspec_root) == {}


# ---------------------------------------------------------------------------
# add / remove
# ---------------------------------------------------------------------------


class TestCommandCRUD:
    def test_add_command(self, sspec_root: Path):
        cmd = CommandInfo(name='test', description='test cmd', type='cmd-line', invoke='echo hi')
        add_command(sspec_root, cmd)
        loaded = load_registry(sspec_root)
        assert 'test' in loaded

    def test_add_duplicate_raises(self, sspec_root: Path):
        cmd = CommandInfo(name='dup', description='', type='cmd-line', invoke='')
        add_command(sspec_root, cmd)
        with pytest.raises(CommandExistsError):
            add_command(sspec_root, cmd)

    def test_remove_command(self, sspec_root: Path):
        cmd = CommandInfo(name='rm-me', description='', type='cmd-line', invoke='')
        add_command(sspec_root, cmd)
        removed = remove_command(sspec_root, 'rm-me')
        assert removed.name == 'rm-me'
        assert 'rm-me' not in load_registry(sspec_root)

    def test_remove_nonexistent_raises(self, sspec_root: Path):
        with pytest.raises(CommandNotFoundError):
            remove_command(sspec_root, 'ghost')

    def test_remove_cleans_up_script(self, sspec_root: Path):
        # Create a script file first
        cmd_dir = sspec_root / 'commands'
        cmd_dir.mkdir(parents=True, exist_ok=True)
        script = cmd_dir / 'run.sh'
        script.write_text('#!/bin/bash\necho ok\n', encoding='utf-8')

        cmd = CommandInfo(
            name='scripted',
            description='',
            type='script',
            invoke='bash {script}',
            script_file='run.sh',
            script_strategy='copy',
        )
        add_command(sspec_root, cmd)
        remove_command(sspec_root, 'scripted')
        assert not script.exists()


# ---------------------------------------------------------------------------
# handle_script_file
# ---------------------------------------------------------------------------


class TestHandleScriptFile:
    def test_copy_strategy(self, sspec_root: Path, tmp_path: Path):
        src = tmp_path / 'build.sh'
        src.write_text('#!/bin/bash\necho build\n', encoding='utf-8')
        filename = handle_script_file(sspec_root, src, 'copy')
        assert filename == 'build.sh'
        assert (sspec_root / 'commands' / 'build.sh').exists()
        assert src.exists()  # original preserved

    def test_move_strategy(self, sspec_root: Path, tmp_path: Path):
        src = tmp_path / 'deploy.sh'
        src.write_text('#!/bin/bash\n', encoding='utf-8')
        filename = handle_script_file(sspec_root, src, 'move')
        assert filename == 'deploy.sh'
        assert not src.exists()  # original moved

    def test_ref_strategy(self, sspec_root: Path, tmp_path: Path):
        src = tmp_path / 'external.sh'
        src.write_text('', encoding='utf-8')
        result = handle_script_file(sspec_root, src, 'ref')
        assert result is not None
        # Should contain the path reference
        assert 'external.sh' in result

    def test_copy_conflict_resolution(self, sspec_root: Path, tmp_path: Path):
        cmd_dir = sspec_root / 'commands'
        cmd_dir.mkdir(parents=True, exist_ok=True)
        (cmd_dir / 'dup.sh').write_text('old', encoding='utf-8')

        src = tmp_path / 'dup.sh'
        src.write_text('new', encoding='utf-8')
        filename = handle_script_file(sspec_root, src, 'copy')
        assert filename != 'dup.sh'  # counter appended


# ---------------------------------------------------------------------------
# resolve_invoke / suggest_invoke_pattern
# ---------------------------------------------------------------------------


class TestInvokeResolution:
    def test_suggest_py(self, tmp_path: Path):
        assert suggest_invoke_pattern(tmp_path / 'run.py') == 'python {script}'

    def test_suggest_sh(self, tmp_path: Path):
        assert suggest_invoke_pattern(tmp_path / 'run.sh') == 'bash {script}'

    def test_suggest_unknown(self, tmp_path: Path):
        assert suggest_invoke_pattern(tmp_path / 'run.xyz') is None

    def test_resolve_cmd_line(self, sspec_root: Path):
        cmd = CommandInfo(name='t', description='', type='cmd-line', invoke='echo hello')
        result = resolve_invoke(cmd, sspec_root, ['--flag'])
        assert result == 'echo hello --flag'

    def test_resolve_script_placeholder(self, sspec_root: Path):
        cmd_dir = sspec_root / 'commands'
        cmd_dir.mkdir(parents=True, exist_ok=True)
        (cmd_dir / 'run.py').write_text('', encoding='utf-8')

        cmd = CommandInfo(
            name='t',
            description='',
            type='script',
            invoke='python {script}',
            script_file='run.py',
            script_strategy='copy',
        )
        result = resolve_invoke(cmd, sspec_root, [])
        assert 'run.py' in result
        assert '{script}' not in result
