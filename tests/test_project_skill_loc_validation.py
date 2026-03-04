"""Tests for skill location validation in `sspec project init`."""

from __future__ import annotations

from pathlib import Path

import click
import pytest

from sspec.commands.project import _validate_skill_locations


def test_validate_skill_locations_rejects_parent_escape(tmp_path: Path):
    with pytest.raises(click.ClickException):
        _validate_skill_locations(tmp_path, ['..'])


def test_validate_skill_locations_rejects_absolute_path(tmp_path: Path):
    # Use a platform-independent absolute by joining then making absolute.
    abs_path = (tmp_path / 'abs').resolve()
    with pytest.raises(click.ClickException):
        _validate_skill_locations(tmp_path, [str(abs_path)])


def test_validate_skill_locations_normalizes_skills_suffix(tmp_path: Path):
    assert _validate_skill_locations(tmp_path, ['.claude/skills']) == ['.claude']
