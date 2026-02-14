"""Tests for deferred skill sync flow in project init service."""

from __future__ import annotations

import json
from pathlib import Path

from sspec.core import SSPEC_DIR
from sspec.services.project_init_service import initialize_project, sync_skill_locations


def test_sync_skill_locations_updates_meta_and_targets(tmp_path: Path):
    initialize_project(
        project_root=tmp_path,
        force=False,
        skill_locations=[],
        prefer_symlink=False,
    )

    result = sync_skill_locations(
        project_root=tmp_path,
        locations=['.github'],
        prefer_symlink=False,
    )

    assert any(str(p).endswith('.github\\skills') for p in result.skill_targets)
    assert result.skill_install_strategies.get('.github/skills') == 'copy'
    assert (tmp_path / '.github' / 'skills' / 'sspec-change' / 'SKILL.md').exists()

    meta_path = tmp_path / SSPEC_DIR / '.meta.json'
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    locations = [loc.replace('\\', '/') for loc in meta.get('skill_locations', [])]
    assert '.github/skills' in locations
    assert '.sspec/skills' in locations


def test_sync_skill_locations_writes_fenced_gitignore(tmp_path: Path):
    initialize_project(
        project_root=tmp_path,
        force=False,
        skill_locations=[],
        prefer_symlink=False,
    )

    sync_skill_locations(
        project_root=tmp_path,
        locations=['.github'],
        prefer_symlink=False,
    )

    gitignore_path = tmp_path / '.github' / '.gitignore'
    content = gitignore_path.read_text(encoding='utf-8')

    assert '# >>> sspec-managed skills >>>' in content
    assert '# <<< sspec-managed skills <<<' in content
    assert 'skills' in content
