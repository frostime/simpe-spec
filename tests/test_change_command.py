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


def test_change_status_shows_new_memory_state_and_milestone(tmp_path: Path, monkeypatch):
    sspec_root = tmp_path / SSPEC_DIR
    sspec_root.mkdir()
    (sspec_root / 'changes').mkdir()
    (sspec_root / 'project.md').write_text('# Project\n', encoding='utf-8')

    change_path = create_change(sspec_root, 'status-demo')
    (change_path / 'memory.md').write_text(
        '# Memory: status-demo\n\n'
        '**Updated**: 2026-04-09T19:00\n\n'
        '## Git Baseline (Immutable)\n\n'
        '- Repository: unavailable\n\n'
        '## State\n'
        'Implementing parser cleanup.\n'
        'Next: update CLI.\n\n'
        '## Milestones\n'
        '- [2026-04-09T19:00] Planning finished\n',
        encoding='utf-8',
    )

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['change', 'status', 'status-demo'])

    assert result.exit_code == 0
    assert 'Current State' in result.output
    assert 'Implementing parser cleanup.' in result.output
    assert 'Latest Milestone' in result.output
    assert '[2026-04-09T19:00] Planning finished' in result.output


def test_change_status_shows_coordination_for_root_memory(tmp_path: Path, monkeypatch):
    sspec_root = tmp_path / SSPEC_DIR
    sspec_root.mkdir()
    (sspec_root / 'changes').mkdir()
    (sspec_root / 'project.md').write_text('# Project\n', encoding='utf-8')

    change_path = create_change(sspec_root, 'root-status', is_root=True)
    (change_path / 'memory.md').write_text(
        '# Memory: root-status\n\n'
        '**Updated**: 2026-04-09T19:00\n\n'
        '## Git Baseline (Immutable)\n\n'
        '- Repository: unavailable\n\n'
        '## Coordination\n\n'
        '| Phase | Sub-Change | Status | Blocker |\n'
        '|-------|------------|--------|---------|\n'
        '| Phase 1 | alpha | ✅ | — |\n\n'
        '## State\n'
        'Coordinating root rollout.\n\n'
        '## Milestones\n'
        '- [2026-04-09T19:00] Root planning finished\n',
        encoding='utf-8',
    )

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['change', 'status', 'root-status'])

    assert result.exit_code == 0
    assert 'Coordination' in result.output
    assert 'alpha' in result.output


def test_change_status_marks_legacy_handover_as_unsupported(tmp_path: Path, monkeypatch):
    sspec_root = tmp_path / SSPEC_DIR
    sspec_root.mkdir()
    (sspec_root / 'changes').mkdir()
    (sspec_root / 'project.md').write_text('# Project\n', encoding='utf-8')

    change_path = create_change(sspec_root, 'legacy-status')
    (change_path / 'memory.md').unlink()
    (change_path / 'handover.md').write_text('## Session Log\n', encoding='utf-8')

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['change', 'status', 'legacy-status'])

    assert result.exit_code == 0
    assert 'unsupported or missing' in result.output
    assert 'Latest Session Log' not in result.output
