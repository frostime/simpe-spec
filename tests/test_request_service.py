"""Tests for request service (filesystem integration in temp dirs)."""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

from sspec.services.request_service import (
    archive_request_file,
    create_request,
    find_request_matches,
    link_request_to_change,
    list_requests,
)


def test_create_request_writes_file_with_frontmatter():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        sspec_root = project_root / ".sspec"
        sspec_root.mkdir(parents=True, exist_ok=True)

        request_path = create_request(
            sspec_root=sspec_root,
            name="My Request",
            template_path=None,
            now=datetime(2025, 1, 2, 3, 4, 5),
        )

        assert request_path.exists()
        text = request_path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert "status: OPEN" in text
        assert "attach-change" in text


def test_list_requests_parses_status_aliases_and_tldr():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        requests_dir = project_root / ".sspec" / "requests"
        requests_dir.mkdir(parents=True, exist_ok=True)

        (requests_dir / "a.md").write_text(
            "---\ncreated: 2025-01-01\nstatus: TODO\ntldr: ''\n---\n\nHello\n",
            encoding="utf-8",
        )
        (requests_dir / "b.md").write_text(
            "---\n"
            "created: 2025-01-02\n"
            "status: IN_PROGRESS\n"
            "attach-change: demo\n"
            "---\n\n"
            "Body\n",
            encoding="utf-8",
        )
        (requests_dir / "c.md").write_text(
            "---\ncreated: 2025-01-03\nstatus: CLOSED\ntldr: Done\n---\n\nBody\n",
            encoding="utf-8",
        )

        items = {r.name: r for r in list_requests(requests_dir)}
        assert items["a"].status == "OPEN"
        assert items["a"].tldr  # extracted from body
        assert items["b"].status == "DOING"
        assert items["b"].attach_change == "demo"
        assert items["c"].status == "DONE"
        assert items["c"].tldr == "Done"


def test_find_request_matches_exact_and_fuzzy():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        requests_dir = project_root / ".sspec" / "requests"
        requests_dir.mkdir(parents=True, exist_ok=True)

        exact = requests_dir / "foo.md"
        exact.write_text("---\nstatus: OPEN\n---\n\nX\n", encoding="utf-8")

        fuzzy = requests_dir / "250102030405-bar.md"
        fuzzy.write_text("---\nstatus: OPEN\n---\n\nY\n", encoding="utf-8")

        assert find_request_matches(requests_dir, "foo") == [exact]
        assert find_request_matches(requests_dir, "bar") == [fuzzy]


def test_link_request_to_change_updates_frontmatter():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        sspec_root = project_root / ".sspec"
        requests_dir = sspec_root / "requests"
        changes_dir = sspec_root / "changes" / "demo"
        changes_dir.mkdir(parents=True, exist_ok=True)
        requests_dir.mkdir(parents=True, exist_ok=True)

        req = requests_dir / "r.md"
        req.write_text(
            "---\ncreated: 2025-01-01\nstatus: OPEN\nattach-change: null\n---\n\nBody\n",
            encoding="utf-8",
        )

        link_request_to_change(
            sspec_root=sspec_root,
            requests_dir=requests_dir,
            request_file=req,
            change_name="demo",
        )

        updated = req.read_text(encoding="utf-8")
        assert "attach-change: demo" in updated
        assert "status: DOING" in updated


def test_archive_request_file_moves_and_resolves_conflicts():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        requests_dir = project_root / ".sspec" / "requests"
        requests_dir.mkdir(parents=True, exist_ok=True)

        req = requests_dir / "x.md"
        req.write_text("---\nstatus: OPEN\n---\n\nBody\n", encoding="utf-8")

        archive_dir = requests_dir / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        (archive_dir / "x.md").write_text("old", encoding="utf-8")

        dest = archive_request_file(requests_dir=requests_dir, request_file=req)

        assert not req.exists()
        assert dest.exists()
        assert dest.name.startswith("x_")
