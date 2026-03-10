"""Tests for sspec.services.project_init_service — project initialization."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sspec.core import SSPEC_DIR
from sspec.services.project_init_service import (
    InitResult,
    ProjectAlreadyInitializedError,
    get_skill_targets_from_locations,
    initialize_project,
)

# ---------------------------------------------------------------------------
# get_skill_targets_from_locations
# ---------------------------------------------------------------------------


class TestGetSkillTargets:
    def test_single_location(self, tmp_path: Path):
        targets = get_skill_targets_from_locations(project_root=tmp_path, locations=['.claude'])
        paths = [t.relative_to(tmp_path).as_posix() for t in targets]
        assert '.claude/skills' in paths
        assert '.sspec/skills' in paths  # always included

    def test_sspec_only(self, tmp_path: Path):
        targets = get_skill_targets_from_locations(project_root=tmp_path, locations=['.sspec'])
        assert len(targets) == 1
        assert targets[0] == tmp_path / SSPEC_DIR / 'skills'

    def test_multiple_locations(self, tmp_path: Path):
        targets = get_skill_targets_from_locations(
            project_root=tmp_path, locations=['.claude', '.github']
        )
        paths = [t.relative_to(tmp_path).as_posix() for t in targets]
        assert '.claude/skills' in paths
        assert '.github/skills' in paths
        assert '.sspec/skills' in paths


# ---------------------------------------------------------------------------
# initialize_project
# ---------------------------------------------------------------------------


class TestInitializeProject:
    def test_creates_full_directory_structure(self, tmp_path: Path):
        initialize_project(
            project_root=tmp_path,
            force=False,
            skill_locations=[],
            prefer_symlink=False,
        )
        sspec = tmp_path / SSPEC_DIR
        assert sspec.is_dir()
        assert (sspec / 'changes').is_dir()
        assert (sspec / 'changes' / 'archive').is_dir()
        assert (sspec / 'requests').is_dir()
        assert (sspec / 'asks').is_dir()
        assert (sspec / 'skills').is_dir()
        assert (sspec / 'howto').is_dir()
        assert (sspec / 'spec-docs').is_dir()

    def test_creates_meta_json(self, tmp_path: Path):
        initialize_project(
            project_root=tmp_path,
            force=False,
            skill_locations=[],
            prefer_symlink=False,
        )
        meta_path = tmp_path / SSPEC_DIR / '.meta.json'
        assert meta_path.exists()
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        assert 'sspec_schema' in meta
        assert 'meta_schema' in meta
        assert 'sspec_version' in meta
        assert 'file_hashes' in meta
        assert 'managed_skills' in meta
        assert 'schema_version' not in meta
        assert 'meta_schema_version' not in meta
        assert 'skill_install_strategies' not in meta

    def test_creates_project_md(self, tmp_path: Path):
        initialize_project(
            project_root=tmp_path,
            force=False,
            skill_locations=[],
            prefer_symlink=False,
        )
        assert (tmp_path / SSPEC_DIR / 'project.md').exists()

    def test_creates_root_agents_md(self, tmp_path: Path):
        result = initialize_project(
            project_root=tmp_path,
            force=False,
            skill_locations=[],
            prefer_symlink=False,
        )
        assert (tmp_path / 'AGENTS.md').exists()
        assert result.created_or_updated_agents is True

    def test_installs_skills(self, tmp_path: Path):
        initialize_project(
            project_root=tmp_path,
            force=False,
            skill_locations=[],
            prefer_symlink=False,
        )
        skills_dir = tmp_path / SSPEC_DIR / 'skills'
        # At least the built-in sspec skill should exist
        assert any(d.is_dir() for d in skills_dir.iterdir())

    def test_creates_gitignore(self, tmp_path: Path):
        initialize_project(
            project_root=tmp_path,
            force=False,
            skill_locations=[],
            prefer_symlink=False,
        )
        gi = tmp_path / SSPEC_DIR / '.gitignore'
        assert gi.exists()
        assert 'tmp/**' in gi.read_text(encoding='utf-8')

    def test_raises_when_exists_without_force(self, tmp_path: Path):
        (tmp_path / SSPEC_DIR).mkdir()
        with pytest.raises(ProjectAlreadyInitializedError):
            initialize_project(
                project_root=tmp_path,
                force=False,
                skill_locations=[],
                prefer_symlink=False,
            )

    def test_force_reinitializes(self, tmp_path: Path):
        initialize_project(
            project_root=tmp_path,
            force=False,
            skill_locations=[],
            prefer_symlink=False,
        )
        # Should not raise with force=True
        result = initialize_project(
            project_root=tmp_path,
            force=True,
            skill_locations=[],
            prefer_symlink=False,
        )
        assert result.sspec_path.exists()

    def test_skill_locations_recorded_in_meta(self, tmp_path: Path):
        (tmp_path / '.claude').mkdir()
        initialize_project(
            project_root=tmp_path,
            force=False,
            skill_locations=['.claude'],
            prefer_symlink=False,
        )
        meta = json.loads((tmp_path / SSPEC_DIR / '.meta.json').read_text(encoding='utf-8'))
        locations = [loc.replace('\\', '/') for loc in meta.get('skill_locations', [])]
        assert '.sspec/skills' in locations

    def test_return_type(self, tmp_path: Path):
        result = initialize_project(
            project_root=tmp_path,
            force=False,
            skill_locations=[],
            prefer_symlink=False,
        )
        assert isinstance(result, InitResult)
        assert result.sspec_path == tmp_path / SSPEC_DIR
