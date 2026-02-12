"""Tests for sspec.services.agents_service — root AGENTS.md SSPEC block management."""

from __future__ import annotations

from pathlib import Path

from sspec.core import SCHEMA_VERSION, get_template_dir
from sspec.services.agents_service import update_root_agents_block


def _common_args(project_root: Path) -> dict:
    return {
        'project_root': project_root,
        'template_agents_path': get_template_dir() / 'AGENTS.md',
        'replacements': {'SCHEMA_VERSION': SCHEMA_VERSION, 'SCHEMA': SCHEMA_VERSION},
    }


class TestUpdateRootAgentsBlock:
    def test_creates_file_when_missing(self, tmp_path: Path):
        changed = update_root_agents_block(**_common_args(tmp_path), dry_run=False)
        assert changed is True
        agents = tmp_path / 'AGENTS.md'
        assert agents.exists()
        content = agents.read_text(encoding='utf-8')
        assert '<!-- SSPEC:START -->' in content
        assert '<!-- SSPEC:END -->' in content

    def test_replaces_existing_block(self, tmp_path: Path):
        agents = tmp_path / 'AGENTS.md'
        agents.write_text(
            '# My Project\n\n<!-- SSPEC:START -->old content<!-- SSPEC:END -->\n\nFooter\n',
            encoding='utf-8',
        )
        changed = update_root_agents_block(**_common_args(tmp_path), dry_run=False)
        assert changed is True

        content = agents.read_text(encoding='utf-8')
        assert '# My Project' in content  # header preserved
        assert 'Footer' in content  # footer preserved
        assert 'old content' not in content  # old block replaced

    def test_appends_when_no_markers(self, tmp_path: Path):
        agents = tmp_path / 'AGENTS.md'
        agents.write_text('# Custom Protocol\n\nSome custom content.\n', encoding='utf-8')

        changed = update_root_agents_block(**_common_args(tmp_path), dry_run=False)
        assert changed is True

        content = agents.read_text(encoding='utf-8')
        assert '# Custom Protocol' in content
        assert '<!-- SSPEC:START -->' in content

    def test_no_change_when_identical(self, tmp_path: Path):
        """If content is already up-to-date, should return False."""
        # First write creates the file
        update_root_agents_block(**_common_args(tmp_path), dry_run=False)
        # Second call with same content
        changed = update_root_agents_block(**_common_args(tmp_path), dry_run=False)
        assert changed is False

    def test_dry_run_does_not_modify(self, tmp_path: Path):
        changed = update_root_agents_block(**_common_args(tmp_path), dry_run=True)
        assert changed is True
        assert not (tmp_path / 'AGENTS.md').exists()

    def test_missing_template_returns_false(self, tmp_path: Path):
        changed = update_root_agents_block(
            project_root=tmp_path,
            template_agents_path=tmp_path / 'nonexistent.md',
            replacements={},
            dry_run=False,
        )
        assert changed is False
