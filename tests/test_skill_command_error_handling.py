"""Command-level tests for `sspec skill` error handling."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from sspec.cli import main
from sspec.commands import skill as skill_cmd
from sspec.services.project_init_service import initialize_project
from sspec.services.skill_service import DominateSkillsResult


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


def test_skill_dominate_updates_meta_strategy_and_parent_gitignore(tmp_path: Path, monkeypatch):
    _init_project(tmp_path)
    sspec_root = tmp_path / '.sspec'
    source_dir = sspec_root / 'skills'

    def _fake_dominate(*, sspec_root: Path, dominate_dir: Path, force_relink: bool = False):
        del force_relink
        return DominateSkillsResult(
            status='linked',
            dominate_dir=dominate_dir,
            target_dir=dominate_dir / 'skills',
            source_dir=sspec_root / 'skills',
            link_kind='junction',
        )

    monkeypatch.setattr(skill_cmd, 'dominate_skills_location', _fake_dominate)

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['skill', 'dominate', '.claude'])

    assert result.exit_code == 0

    meta = json.loads((sspec_root / '.meta.json').read_text(encoding='utf-8'))
    assert '.claude/skills' in (meta.get('skill_locations') or [])
    assert (meta.get('skill_install_strategies') or {}).get('.claude/skills') == 'junction'

    gitignore_path = tmp_path / '.claude' / '.gitignore'
    content = gitignore_path.read_text(encoding='utf-8')
    assert '# >>> sspec-managed skills >>>' in content
    assert '# <<< sspec-managed skills <<<' in content
    assert '\nskills\n' in content
    assert source_dir.exists()
