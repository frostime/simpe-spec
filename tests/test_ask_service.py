"""Tests for ask service (record writing and name normalization)."""

from __future__ import annotations

import io
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from sspec.services.ask_service import (
    normalize_ask_name,
    resolve_question,
    write_ask_record,
)


def _frontmatter(text: str) -> dict:
    if not text.startswith('---'):
        return {}
    parts = text.split('---', 2)
    if len(parts) < 3:
        return {}
    return yaml.safe_load(parts[1]) or {}


def test_normalize_ask_name_to_kebab_case():
    assert normalize_ask_name("My Ask") == "my-ask"
    assert normalize_ask_name("  Hello__World ") == "helloworld"
    assert normalize_ask_name("a/b?c") == "abc"


def test_resolve_question_reads_stdin_when_dash():
    stdin = io.StringIO("hello\nworld\n")
    assert resolve_question(question_opt="-", stdin_stream=stdin) == "hello\nworld\n"
    assert resolve_question(question_opt="hi", stdin_stream=io.StringIO("x")) == "hi"


def test_write_ask_record_creates_timestamped_file_and_content():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        sspec_root = project_root / ".sspec"
        sspec_root.mkdir(parents=True, exist_ok=True)

        record_path = write_ask_record(
            sspec_root=sspec_root,
            name="My Ask",
            why="Because",
            question="Q?",
            answer="A!",
            now=datetime(2025, 1, 2, 3, 4, 5),
        )

        assert record_path.exists()
        assert record_path.name == "250102030405_my-ask.md"

        text = record_path.read_text(encoding="utf-8")
        assert text.startswith("---\n")

        meta = _frontmatter(text)
        assert meta["created"] == "2025-01-02T03:04:05"
        assert meta["name"] == "my-ask"
        assert meta["why"] == "Because"
        assert "## Question" in text
        assert "Q?" in text
        assert "## Answer" in text
        assert "A!" in text


def test_write_ask_record_resolves_name_conflicts():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        sspec_root = project_root / ".sspec"
        sspec_root.mkdir(parents=True, exist_ok=True)

        first = write_ask_record(
            sspec_root=sspec_root,
            name="My Ask",
            why=None,
            question="Q",
            answer="A",
            now=datetime(2025, 1, 2, 3, 4, 5),
        )
        second = write_ask_record(
            sspec_root=sspec_root,
            name="My Ask",
            why=None,
            question="Q",
            answer="A",
            now=datetime(2025, 1, 2, 3, 4, 5),
        )

        assert first.name == "250102030405_my-ask.md"
        assert second.name == "250102030405_my-ask_1.md"


def test_write_ask_record_rejects_invalid_name():
    with tempfile.TemporaryDirectory() as tmpdir:
        sspec_root = Path(tmpdir) / ".sspec"
        sspec_root.mkdir(parents=True, exist_ok=True)

        with pytest.raises(ValueError):
            write_ask_record(
                sspec_root=sspec_root,
                name="!!!",
                why=None,
                question="Q",
                answer="A",
                now=datetime(2025, 1, 2, 3, 4, 5),
            )
