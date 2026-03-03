"""Command-level tests for `sspec skill` error handling."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from sspec.cli import main
from sspec.commands import skill as skill_cmd
from sspec.services.project_init_service import initialize_project


def _init_project(tmp_path: Path) -> None:
    initialize_project(
        project_root=tmp_path,
        force=False,
        skill_locations=[],
        prefer_symlink=False,
    )


def test_skill_new_converts_oserror_to_click_exception(tmp_path: Path, monkeypatch):
    _init_project(tmp_path)

    def _boom(**_kwargs):
        raise OSError('boom')

    monkeypatch.setattr(skill_cmd, 'create_skill_in_hub', _boom)

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['skill', 'new', 'test-skill'])

    assert result.exit_code != 0
    assert 'boom' in result.output
