"""Command-level tests for `sspec change` workflows."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from sspec.cli import main
from sspec.core import SSPEC_DIR
from sspec.libs.md_yaml import update_frontmatter
from sspec.services.change_service import archive_change, create_change, parse_change


def _update_spec_frontmatter(change_path: Path, **values: str) -> None:
    """Update one or more spec.md frontmatter values."""

    spec = change_path / 'spec.md'
    content = spec.read_text(encoding='utf-8')
    updated = update_frontmatter(content, values)
    spec.write_text(updated, encoding='utf-8')


def test_change_list_prints_newest_active_first(tmp_path: Path, monkeypatch):
    sspec_root = tmp_path / SSPEC_DIR
    sspec_root.mkdir()
    (sspec_root / 'changes').mkdir()
    (sspec_root / 'changes' / 'archive').mkdir()
    (sspec_root / 'project.md').write_text('# Project\n', encoding='utf-8')

    alpha = create_change(sspec_root, 'alpha')
    beta = create_change(sspec_root, 'beta')
    gamma = create_change(sspec_root, 'gamma')

    _update_spec_frontmatter(alpha, created='2026-02-01T10:00:00')
    _update_spec_frontmatter(beta, created='2026-02-03T10:00:00')
    _update_spec_frontmatter(gamma, created='2026-02-02T10:00:00')

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['change', 'list'])

    assert result.exit_code == 0
    beta_pos = result.output.index('beta')
    gamma_pos = result.output.index('gamma')
    alpha_pos = result.output.index('alpha')
    assert beta_pos < gamma_pos < alpha_pos


def test_change_list_shows_hidden_archived_count_without_all(tmp_path: Path, monkeypatch):
    sspec_root = tmp_path / SSPEC_DIR
    sspec_root.mkdir()
    (sspec_root / 'changes').mkdir()
    (sspec_root / 'changes' / 'archive').mkdir()
    (sspec_root / 'project.md').write_text('# Project\n', encoding='utf-8')

    active = create_change(sspec_root, 'active-change')
    archived = create_change(sspec_root, 'archived-change')

    _update_spec_frontmatter(active, created='2026-02-03T10:00:00')
    _update_spec_frontmatter(archived, status='DONE', created='2026-02-01T10:00:00')
    archive_change(sspec_root, parse_change(archived))

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['change', 'list'])

    assert result.exit_code == 0
    assert 'Archived: 1 (use --all to show)' in result.output
    assert 'Active: 1 | Archived: 1' in result.output
