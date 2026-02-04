"""Tests for extracted project-related services."""

from __future__ import annotations

import tempfile
from pathlib import Path

from sspec.core import SCHEMA_VERSION, get_template_dir
from sspec.services.meta_service import load_meta, save_meta
from sspec.services.project_update_service import collect_update_candidates


def test_meta_service_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        sspec_root = Path(tmpdir) / ".sspec"
        sspec_root.mkdir(parents=True, exist_ok=True)

        assert load_meta(sspec_root) == {}

        meta = {
            "file_hashes": {"x": "y"},
            "skill_locations": [".sspec/skills"],
            "skill_install_strategies": {".sspec/skills": "copy"},
        }
        save_meta(sspec_root, meta)

        loaded = load_meta(sspec_root)
        assert loaded["file_hashes"] == {"x": "y"}
        assert loaded["skill_locations"] == [".sspec/skills"]


def test_collect_update_candidates_smoke():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        sspec_root = project_root / ".sspec"
        sspec_root.mkdir(parents=True, exist_ok=True)

        # Simulate one skill install location.
        (project_root / ".sspec" / "skills").mkdir(parents=True, exist_ok=True)

        meta = {
            "file_hashes": {},
            "skill_locations": [".sspec/skills"],
            "skill_install_strategies": {".sspec/skills": "copy"},
        }

        candidates = collect_update_candidates(
            sspec_root=sspec_root,
            template_dir=get_template_dir(),
            meta=meta,
            common_replacements={"SCHEMA_VERSION": SCHEMA_VERSION, "SCHEMA": SCHEMA_VERSION},
        )

        # UPDATABLE_FILES is empty in this repo, so this mainly covers skills.
        assert candidates
        assert all(c.display_path for c in candidates)
        assert any(c.strategy in {"copy", "symlink"} for c in candidates)
