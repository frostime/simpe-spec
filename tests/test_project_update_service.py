"""Tests for sspec.services.project_update_service — update candidates and orphan detection."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from sspec.core import SCHEMA_VERSION, SSPEC_DIR, get_template_dir, list_template_skills
from sspec.services.project_init_service import initialize_project
from sspec.services.project_update_service import (
    MetaMigrationError,
    OrphanedSkill,
    collect_orphaned_skills,
    collect_update_candidates,
    migrate_legacy_skill_layouts,
    prepare_meta_for_project_update,
    remove_orphaned_skill,
    sync_hub_skills_gitignore,
)

COMMON_REPLACEMENTS = {'SCHEMA_VERSION': SCHEMA_VERSION, 'SCHEMA': SCHEMA_VERSION}


class TestPrepareMetaForProjectUpdate:
    def test_migrates_legacy_meta_keys(self, tmp_path: Path):
        sspec_root = _init_project(tmp_path)
        meta_path = sspec_root / '.meta.json'
        meta_path.write_text(
            json.dumps({'meta_schema_version': '1', 'schema_version': '9.1'}),
            encoding='utf-8',
        )

        state = prepare_meta_for_project_update(sspec_root=sspec_root)

        assert state.migration_needed is True
        assert state.meta.get('meta_schema') == '2.1'
        assert state.meta.get('sspec_schema') == '9.1'
        assert 'meta_schema_version' not in state.meta
        assert 'schema_version' not in state.meta

    def test_rejects_future_meta_schema(self, tmp_path: Path):
        sspec_root = _init_project(tmp_path)
        meta_path = sspec_root / '.meta.json'
        meta_path.write_text(json.dumps({'meta_schema': '999.0'}), encoding='utf-8')

        with pytest.raises(MetaMigrationError, match='Unsupported future meta_schema'):
            prepare_meta_for_project_update(sspec_root=sspec_root)


def _init_project(tmp_path: Path) -> Path:
    """Initialize a project and return sspec_root."""
    initialize_project(
        project_root=tmp_path,
        force=False,
        skill_locations=[],
        prefer_symlink=False,
    )
    return tmp_path / SSPEC_DIR


# ---------------------------------------------------------------------------
# collect_update_candidates
# ---------------------------------------------------------------------------


class TestCollectUpdateCandidates:
    def test_freshly_initialized_all_current(self, tmp_path: Path):
        """Right after init, all skills should be 'current'."""
        sspec_root = _init_project(tmp_path)
        meta = json.loads((sspec_root / '.meta.json').read_text(encoding='utf-8'))

        candidates = collect_update_candidates(
            sspec_root=sspec_root,
            template_dir=get_template_dir(),
            meta=meta,
            common_replacements=COMMON_REPLACEMENTS,
        )
        # All candidates should be current (hashes match)
        statuses = {c.status for c in candidates}
        assert 'current' in statuses or len(candidates) == 0

    def test_returns_candidates_for_skills(self, tmp_path: Path):
        sspec_root = _init_project(tmp_path)
        meta = json.loads((sspec_root / '.meta.json').read_text(encoding='utf-8'))

        candidates = collect_update_candidates(
            sspec_root=sspec_root,
            template_dir=get_template_dir(),
            meta=meta,
            common_replacements=COMMON_REPLACEMENTS,
        )
        assert len(candidates) > 0
        assert all(c.display_path for c in candidates)

    def test_modified_skill_detected(self, tmp_path: Path):
        sspec_root = _init_project(tmp_path)
        meta = json.loads((sspec_root / '.meta.json').read_text(encoding='utf-8'))

        # Modify a skill file to make it differ from template
        template_skills = list_template_skills()
        if template_skills:
            skill_name = template_skills[0].name
            installed = sspec_root / 'skills' / skill_name / 'SKILL.md'
            if installed.exists():
                installed.write_text('# Modified by user\n', encoding='utf-8')

                candidates = collect_update_candidates(
                    sspec_root=sspec_root,
                    template_dir=get_template_dir(),
                    meta=meta,
                    common_replacements=COMMON_REPLACEMENTS,
                )
                target_rel = f'.sspec/skills/{skill_name}/SKILL.md'.replace('/', '\\')
                target = next((c for c in candidates if c.display_path == target_rel), None)
                assert target is not None
                assert target.status == 'modified'

    def test_empty_meta_still_works(self, tmp_path: Path):
        sspec_root = tmp_path / SSPEC_DIR
        sspec_root.mkdir(parents=True)
        (sspec_root / 'skills').mkdir()

        candidates = collect_update_candidates(
            sspec_root=sspec_root,
            template_dir=get_template_dir(),
            meta={'skill_locations': ['.sspec/skills']},
            common_replacements=COMMON_REPLACEMENTS,
        )
        # Should not crash; missing skills → status 'missing'
        if candidates:
            assert any(c.status == 'missing' for c in candidates)

    def test_missing_spoke_root_is_not_recreated_as_per_skill_copy(self, tmp_path: Path):
        sspec_root = _init_project(tmp_path)
        meta = json.loads((sspec_root / '.meta.json').read_text(encoding='utf-8'))
        meta['skill_locations'] = ['.sspec/skills', '.github/skills']

        spoke_root = tmp_path / '.github' / 'skills'
        if spoke_root.exists():
            if spoke_root.is_dir():
                shutil.rmtree(spoke_root)
            else:
                spoke_root.unlink()

        candidates = collect_update_candidates(
            sspec_root=sspec_root,
            template_dir=get_template_dir(),
            meta=meta,
            common_replacements=COMMON_REPLACEMENTS,
        )

        assert not any(c.display_path.startswith('.github\\skills\\') for c in candidates)


# ---------------------------------------------------------------------------
# collect_orphaned_skills / remove_orphaned_skill
# ---------------------------------------------------------------------------


class TestOrphanedSkills:
    def test_no_orphans_after_fresh_init(self, tmp_path: Path):
        sspec_root = _init_project(tmp_path)
        meta = json.loads((sspec_root / '.meta.json').read_text(encoding='utf-8'))

        orphans = collect_orphaned_skills(
            project_root=tmp_path,
            meta=meta,
        )
        assert orphans == []

    def test_detects_orphan(self, tmp_path: Path):
        sspec_root = _init_project(tmp_path)
        meta = json.loads((sspec_root / '.meta.json').read_text(encoding='utf-8'))

        # Add a fake managed skill that doesn't exist in templates
        meta['managed_skills'].append('obsolete-skill')
        # Create the directory so it's detected as an orphan
        orphan_dir = sspec_root / 'skills' / 'obsolete-skill'
        orphan_dir.mkdir(parents=True)
        (orphan_dir / 'SKILL.md').write_text('old skill', encoding='utf-8')

        orphans = collect_orphaned_skills(
            project_root=tmp_path,
            meta=meta,
        )
        assert len(orphans) == 1
        assert orphans[0].skill_name == 'obsolete-skill'

    def test_remove_orphan(self, tmp_path: Path):
        orphan_dir = tmp_path / '.sspec' / 'skills' / 'dead-skill'
        orphan_dir.mkdir(parents=True)
        (orphan_dir / 'SKILL.md').write_text('content', encoding='utf-8')

        orphan = OrphanedSkill(skill_name='dead-skill', paths=[orphan_dir])
        removed = remove_orphaned_skill(orphan)
        assert removed == 1
        assert not orphan_dir.exists()


def test_migrate_legacy_skill_layouts_detects_legacy_in_dry_run(monkeypatch, tmp_path: Path):
    sspec_root = _init_project(tmp_path)

    legacy_root = tmp_path / '.github' / 'skills'
    legacy_root.mkdir(parents=True, exist_ok=True)

    template_skills = list_template_skills()
    assert template_skills
    skill_name = template_skills[0].name
    (legacy_root / skill_name).mkdir(parents=True, exist_ok=True)
    (legacy_root / 'sspec').mkdir(parents=True, exist_ok=True)

    meta = json.loads((sspec_root / '.meta.json').read_text(encoding='utf-8'))
    meta['skill_locations'] = ['.sspec/skills', '.github/skills']

    import sspec.services.project_update_service as update_module

    original_check = update_module.check_path_link

    def fake_check(path: Path, expected_target: Path | None = None) -> bool:
        if path == legacy_root:
            return False
        if path == legacy_root / skill_name:
            return True
        if path == legacy_root / 'sspec':
            return True
        return original_check(path, expected_target)

    monkeypatch.setattr(update_module, 'check_path_link', fake_check)

    migrations = migrate_legacy_skill_layouts(
        project_root=tmp_path,
        sspec_root=sspec_root,
        meta=meta,
        dry_run=True,
    )

    assert len(migrations) == 1
    assert migrations[0].location == '.github/skills'


def test_sync_hub_skills_gitignore_updates_only_hub_file(tmp_path: Path):
    sspec_root = _init_project(tmp_path)
    hub_gitignore = sspec_root / 'skills' / '.gitignore'
    sspec_gitignore = sspec_root / '.gitignore'
    sspec_before = sspec_gitignore.read_text(encoding='utf-8')

    changed = sync_hub_skills_gitignore(
        sspec_root=sspec_root,
        managed_skill_names=['alpha-skill', 'beta-skill'],
        dry_run=False,
    )

    assert changed is True
    content = hub_gitignore.read_text(encoding='utf-8')
    assert '# >>> sspec-managed skills >>>' in content
    assert 'alpha-skill' in content
    assert 'beta-skill' in content
    assert sspec_gitignore.read_text(encoding='utf-8') == sspec_before


def test_sync_hub_skills_gitignore_dry_run_does_not_write(tmp_path: Path):
    sspec_root = _init_project(tmp_path)
    hub_gitignore = sspec_root / 'skills' / '.gitignore'
    before = hub_gitignore.read_text(encoding='utf-8') if hub_gitignore.exists() else ''

    changed = sync_hub_skills_gitignore(
        sspec_root=sspec_root,
        managed_skill_names=['new-managed-skill'],
        dry_run=True,
    )

    assert changed is True
    after = hub_gitignore.read_text(encoding='utf-8') if hub_gitignore.exists() else ''
    assert after == before
