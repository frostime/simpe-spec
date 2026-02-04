"""Tests for project init service (filesystem integration in temp dirs)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from sspec.core import SSPEC_DIR
from sspec.services.project_init_service import initialize_project


def test_initialize_project_creates_sspec_structure_and_meta():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        result = initialize_project(
            project_root=project_root,
            force=False,
            skill_locations=[".claude"],
            default_gitignore="x\n",
            prefer_symlink=False,
        )

        assert result.sspec_path == project_root / SSPEC_DIR
        assert (project_root / SSPEC_DIR / "changes" / "archive").is_dir()
        assert (project_root / SSPEC_DIR / "requests").is_dir()
        assert (project_root / SSPEC_DIR / "asks").is_dir()
        assert (project_root / SSPEC_DIR / "spec-docs").is_dir()

        meta_path = project_root / SSPEC_DIR / ".meta.json"
        assert meta_path.exists()

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        assert "schema_version" in meta
        assert "sspec_version" in meta
        assert "file_hashes" in meta
        locations = [str(p).replace('\\', '/') for p in meta.get("skill_locations", [])]
        assert ".sspec/skills" in locations

        # Root AGENTS.md should be created/updated.
        assert (project_root / "AGENTS.md").exists()
