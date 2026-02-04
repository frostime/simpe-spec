"""Tests for root AGENTS.md update service."""

from __future__ import annotations

import tempfile
from pathlib import Path

from sspec.core import SCHEMA_VERSION, get_template_dir
from sspec.services.agents_service import update_root_agents_block


def test_update_root_agents_block_creates_file_when_missing():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        changed = update_root_agents_block(
            project_root=project_root,
            template_agents_path=get_template_dir() / "AGENTS.md",
            replacements={"SCHEMA_VERSION": SCHEMA_VERSION, "SCHEMA": SCHEMA_VERSION},
            dry_run=False,
        )
        assert changed is True
        assert (project_root / "AGENTS.md").exists()


def test_update_root_agents_block_replaces_existing_block():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        agents_path = project_root / "AGENTS.md"
        agents_path.write_text(
            "header\n\n<!-- SSPEC:START -->old<!-- SSPEC:END -->\n\nfooter\n",
            encoding="utf-8",
        )

        changed = update_root_agents_block(
            project_root=project_root,
            template_agents_path=get_template_dir() / "AGENTS.md",
            replacements={"SCHEMA_VERSION": SCHEMA_VERSION, "SCHEMA": SCHEMA_VERSION},
            dry_run=False,
        )
        assert changed is True

        content = agents_path.read_text(encoding="utf-8")
        assert "<!-- SSPEC:START -->" in content
        assert "<!-- SSPEC:END -->" in content
        assert "<!-- SSPEC:START -->old<!-- SSPEC:END -->" not in content
