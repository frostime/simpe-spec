"""Shared fixtures for sspec tests."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from sspec.core import SSPEC_DIR


@pytest.fixture()
def tmp_project(tmp_path: Path) -> Path:
    """A temporary project root with .sspec/ skeleton (no init)."""
    sspec = tmp_path / SSPEC_DIR
    sspec.mkdir()
    (sspec / 'changes').mkdir()
    (sspec / 'changes' / 'archive').mkdir()
    (sspec / 'requests').mkdir()
    (sspec / 'asks').mkdir()
    (sspec / 'skills').mkdir()
    (sspec / 'spec-docs').mkdir()
    # project.md is the marker file that find_sspec_root looks for
    (sspec / 'project.md').write_text('# Project\n', encoding='utf-8')
    return tmp_path


@pytest.fixture()
def sspec_root(tmp_project: Path) -> Path:
    """The .sspec directory inside tmp_project."""
    return tmp_project / SSPEC_DIR
