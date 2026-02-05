"""Tests for change creation and archiving."""

from __future__ import annotations

import tempfile
from pathlib import Path

from sspec.core import SSPEC_DIR
from sspec.services.change_service import archive_change, create_change, parse_change


def _write_done_status(spec_file: Path) -> None:
    content = spec_file.read_text(encoding="utf-8")
    if content.startswith("---"):
        # Replace first status line in YAML frontmatter.
        lines = content.splitlines()
        for idx, line in enumerate(lines):
            if line.startswith("status:"):
                lines[idx] = "status: DONE"
                spec_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
                return

    spec_file.write_text("---\nstatus: DONE\n---\n\n" + content, encoding="utf-8")


def test_archive_change_moves_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        sspec_root = project_root / SSPEC_DIR
        sspec_root.mkdir(parents=True, exist_ok=True)
        (sspec_root / "changes" / "archive").mkdir(parents=True, exist_ok=True)

        change_path = create_change(sspec_root, "demo")
        _write_done_status(change_path / "spec.md")

        change_info = parse_change(change_path)
        archived_path = archive_change(sspec_root, change_info)
        assert archived_path.exists()
        assert not change_path.exists()
