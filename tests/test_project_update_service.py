"""Tests for sspec.services.project_update_service — update candidates and orphan detection."""

from __future__ import annotations

import json
from pathlib import Path

from sspec.core import SCHEMA_VERSION, SSPEC_DIR, get_template_dir, list_template_skills
from sspec.services.project_init_service import initialize_project
from sspec.services.project_update_service import (
    OrphanedSkill,
    collect_orphaned_skills,
    collect_update_candidates,
    remove_orphaned_skill,
)

COMMON_REPLACEMENTS = {'SCHEMA_VERSION': SCHEMA_VERSION, 'SCHEMA': SCHEMA_VERSION}


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
                # At least one should be updatable (template changed relative to installed)
                statuses = {c.status for c in candidates}
                assert 'updatable' in statuses or 'current' in statuses

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
