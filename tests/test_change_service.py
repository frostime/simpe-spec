"""Tests for sspec.services.change_service — create, parse, list, archive, validate changes."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from sspec.core import ChangeExistsError, ChangeStatus, InvalidChangeNameError
from sspec.libs.md_yaml import update_frontmatter
from sspec.services.change_service import (
    archive_change,
    create_change,
    extract_change_name_from_dirname,
    find_change_matches,
    list_changes,
    parse_change,
    validate_change,
)

GIT_AVAILABLE = shutil.which('git') is not None

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _set_spec_status(change_path: Path, status: str) -> None:
    """Overwrite status in spec.md frontmatter."""
    spec = change_path / 'spec.md'
    content = spec.read_text(encoding='utf-8')
    updated = update_frontmatter(content, {'status': status})
    spec.write_text(updated, encoding='utf-8')


def _write_tasks(change_path: Path, done: int, total: int) -> None:
    """Write a tasks.md with the given done/total checkbox counts."""
    lines = []
    for i in range(total):
        marker = 'x' if i < done else ' '
        lines.append(f'- [{marker}] Task {i + 1}')
    (change_path / 'tasks.md').write_text('\n'.join(lines), encoding='utf-8')


def _git(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run a git command in tests with stdout captured."""

    return subprocess.run(
        ['git', *args],
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True,
        encoding='utf-8',
    )


def _init_git_repo(project_root: Path) -> None:
    """Initialize a clean git repo for change creation tests."""

    _git(project_root, 'init')
    (project_root / 'tracked.txt').write_text('initial\n', encoding='utf-8')
    _git(project_root, 'add', '.')
    _git(
        project_root,
        '-c',
        'user.name=Test User',
        '-c',
        'user.email=test@example.com',
        'commit',
        '-m',
        'init',
    )


# ---------------------------------------------------------------------------
# extract_change_name_from_dirname
# ---------------------------------------------------------------------------


class TestExtractChangeName:
    def test_timestamped_format(self):
        assert extract_change_name_from_dirname('26-02-05T19-28_my-change') == 'my-change'

    def test_plain_name(self):
        assert extract_change_name_from_dirname('standalone') == 'standalone'


# ---------------------------------------------------------------------------
# create_change
# ---------------------------------------------------------------------------


class TestCreateChange:
    def test_creates_directory_with_required_files(self, sspec_root: Path):
        change_path = create_change(sspec_root, 'new-feature')
        assert change_path.is_dir()
        assert (change_path / 'spec.md').exists()
        assert (change_path / 'tasks.md').exists()
        assert (change_path / 'handover.md').exists()
        assert (change_path / 'reference').is_dir()

    def test_name_normalization(self, sspec_root: Path):
        change_path = create_change(sspec_root, 'My Feature!')
        dir_name = change_path.name
        # Should be lowercase, spaces→hyphens, special chars removed
        assert 'my-feature' in dir_name
        assert '!' not in dir_name

    def test_empty_name_raises(self, sspec_root: Path):
        with pytest.raises(InvalidChangeNameError):
            create_change(sspec_root, '!!!')

    def test_root_change_uses_different_templates(self, sspec_root: Path):
        normal = create_change(sspec_root, 'normal')
        root = create_change(sspec_root, 'root-change', is_root=True)

        normal_spec = (normal / 'spec.md').read_text(encoding='utf-8')
        root_spec = (root / 'spec.md').read_text(encoding='utf-8')
        # Root templates have different content (phase-level coordination)
        assert normal_spec != root_spec

    def test_duplicate_raises(self, sspec_root: Path):
        """Creating the same change twice within same minute should raise."""
        create_change(sspec_root, 'duplicate')
        with pytest.raises(ChangeExistsError):
            create_change(sspec_root, 'duplicate')

    @pytest.mark.skipif(not GIT_AVAILABLE, reason='git is required for snapshot tests')
    def test_records_clean_git_baseline_in_handover(self, sspec_root: Path):
        project_root = sspec_root.parent
        _init_git_repo(project_root)

        branch = _git(project_root, 'branch', '--show-current').stdout.strip()
        head_hash = _git(project_root, 'rev-parse', 'HEAD').stdout.strip()

        change_path = create_change(sspec_root, 'git-clean')
        handover = (change_path / 'handover.md').read_text(encoding='utf-8')

        assert '## Git Baseline (Immutable)' in handover
        assert f'- Branch: `{branch}`' in handover
        assert f'- HEAD: `{head_hash}`' in handover
        assert '- Worktree: `clean`' in handover
        assert '```text' in handover

    @pytest.mark.skipif(not GIT_AVAILABLE, reason='git is required for snapshot tests')
    def test_records_dirty_git_baseline_before_change_files_exist(self, sspec_root: Path):
        project_root = sspec_root.parent
        _init_git_repo(project_root)

        (project_root / 'tracked.txt').write_text('modified\n', encoding='utf-8')
        (project_root / 'staged.txt').write_text('staged\n', encoding='utf-8')
        (project_root / 'untracked.txt').write_text('untracked\n', encoding='utf-8')
        _git(project_root, 'add', 'staged.txt')

        change_path = create_change(sspec_root, 'git-dirty')
        handover = (change_path / 'handover.md').read_text(encoding='utf-8')

        assert '- Worktree: `dirty`' in handover
        assert 'tracked.txt' in handover
        assert 'staged.txt' in handover
        assert 'untracked.txt' in handover
        assert change_path.name not in handover

    def test_non_repo_gets_fallback_git_baseline(self, sspec_root: Path):
        change_path = create_change(sspec_root, 'git-fallback')
        handover = (change_path / 'handover.md').read_text(encoding='utf-8')

        assert '## Git Baseline (Immutable)' in handover
        assert '- Repository: unavailable' in handover
        assert 'Not a git repository.' in handover

    @pytest.mark.skipif(not GIT_AVAILABLE, reason='git is required for snapshot tests')
    def test_root_change_handover_also_includes_git_baseline(self, sspec_root: Path):
        project_root = sspec_root.parent
        _init_git_repo(project_root)

        change_path = create_change(sspec_root, 'git-root', is_root=True)
        handover = (change_path / 'handover.md').read_text(encoding='utf-8')

        assert '## Git Baseline (Immutable)' in handover
        assert '- Branch: `' in handover


# ---------------------------------------------------------------------------
# parse_change
# ---------------------------------------------------------------------------


class TestParseChange:
    def test_default_status_is_planning(self, sspec_root: Path):
        change_path = create_change(sspec_root, 'parse-test')
        info = parse_change(change_path)
        assert info.status == ChangeStatus.PLANNING.value

    def test_reads_custom_status(self, sspec_root: Path):
        change_path = create_change(sspec_root, 'status-test')
        _set_spec_status(change_path, 'DOING')
        info = parse_change(change_path)
        assert info.status == 'DOING'

    def test_normalizes_alias_status(self, sspec_root: Path):
        change_path = create_change(sspec_root, 'alias-test')
        _set_spec_status(change_path, 'IN_PROGRESS')
        info = parse_change(change_path)
        assert info.status == 'DOING'

    def test_task_progress_counted(self, sspec_root: Path):
        change_path = create_change(sspec_root, 'progress-test')
        _write_tasks(change_path, done=3, total=5)
        info = parse_change(change_path)
        assert info.progress == {'done': 3, 'total': 5}

    def test_pivot_detected(self, sspec_root: Path):
        change_path = create_change(sspec_root, 'pivot-test')
        spec = change_path / 'spec.md'
        content = spec.read_text(encoding='utf-8')
        spec.write_text(content + '\n\nPIVOT: direction changed\n', encoding='utf-8')
        info = parse_change(change_path)
        assert info.has_pivot is True

    def test_blocked_detection(self, sspec_root: Path):
        change_path = create_change(sspec_root, 'blocked-test')
        _set_spec_status(change_path, 'BLOCKED')
        info = parse_change(change_path)
        assert info.has_blockers is True

    def test_archived_flag(self, sspec_root: Path):
        change_path = create_change(sspec_root, 'archived-test')
        info = parse_change(change_path, archived=True)
        assert info.archived is True

    def test_demo_tasks_excluded_from_progress(self, sspec_root: Path):
        """Template demo tasks (containing <Demo Task>) should not be counted."""
        change_path = create_change(sspec_root, 'demo-excl')
        (change_path / 'tasks.md').write_text(
            '- [x] <Demo Task> Example\n- [ ] Real task\n- [x] Done task\n',
            encoding='utf-8',
        )
        info = parse_change(change_path)
        assert info.progress == {'done': 1, 'total': 2}


# ---------------------------------------------------------------------------
# find_change_matches
# ---------------------------------------------------------------------------


class TestFindChangeMatches:
    def test_exact_match(self, sspec_root: Path):
        changes_dir = sspec_root / 'changes'
        d = changes_dir / 'exact-name'
        d.mkdir()
        matches = find_change_matches(changes_dir, 'exact-name')
        assert matches == [d]

    def test_suffix_match(self, sspec_root: Path):
        changes_dir = sspec_root / 'changes'
        d = changes_dir / '26-02-05T10-00_feature'
        d.mkdir()
        matches = find_change_matches(changes_dir, 'feature')
        assert d in matches

    def test_contains_match(self, sspec_root: Path):
        changes_dir = sspec_root / 'changes'
        d = changes_dir / '26-02-05T10-00_add-auth-module'
        d.mkdir()
        matches = find_change_matches(changes_dir, 'auth')
        assert d in matches

    def test_archive_dir_excluded(self, sspec_root: Path):
        changes_dir = sspec_root / 'changes'
        matches = find_change_matches(changes_dir, 'archive')
        assert matches == []

    def test_no_matches(self, sspec_root: Path):
        matches = find_change_matches(sspec_root / 'changes', 'nonexistent')
        assert matches == []


# ---------------------------------------------------------------------------
# list_changes
# ---------------------------------------------------------------------------


class TestListChanges:
    def test_empty_project(self, sspec_root: Path):
        assert list_changes(sspec_root) == []

    def test_lists_active_changes(self, sspec_root: Path):
        create_change(sspec_root, 'alpha')
        create_change(sspec_root, 'beta')
        changes = list_changes(sspec_root)
        assert len(changes) == 2

    def test_excludes_archived_by_default(self, sspec_root: Path):
        change_path = create_change(sspec_root, 'to-archive')
        _set_spec_status(change_path, 'DONE')
        info = parse_change(change_path)
        archive_change(sspec_root, info)
        assert len(list_changes(sspec_root)) == 0

    def test_includes_archived_when_requested(self, sspec_root: Path):
        change_path = create_change(sspec_root, 'archived-inc')
        _set_spec_status(change_path, 'DONE')
        info = parse_change(change_path)
        archive_change(sspec_root, info)
        changes = list_changes(sspec_root, include_archived=True)
        assert any(c.archived for c in changes)

    def test_sorted_by_name(self, sspec_root: Path):
        create_change(sspec_root, 'zebra')
        create_change(sspec_root, 'alpha')
        changes = list_changes(sspec_root)
        names = [c.name for c in changes]
        # parse_change may use the name from spec.md frontmatter;
        # but directory listing should still be sorted
        assert names == sorted(names)


# ---------------------------------------------------------------------------
# archive_change
# ---------------------------------------------------------------------------


class TestArchiveChange:
    def test_moves_to_archive_directory(self, sspec_root: Path):
        change_path = create_change(sspec_root, 'to-archive')
        _set_spec_status(change_path, 'DONE')
        info = parse_change(change_path)
        archive_path = archive_change(sspec_root, info)

        assert archive_path.exists()
        assert not change_path.exists()
        assert 'archive' in str(archive_path)

    def test_adds_archived_timestamp_to_spec(self, sspec_root: Path):
        change_path = create_change(sspec_root, 'ts-test')
        _set_spec_status(change_path, 'DONE')
        info = parse_change(change_path)
        archive_path = archive_change(sspec_root, info)

        spec_content = (archive_path / 'spec.md').read_text(encoding='utf-8')
        assert 'archived:' in spec_content

    def test_conflict_resolution(self, sspec_root: Path):
        """Archiving twice with same name should not fail (counter appended)."""
        # Create first change, archive it
        c1 = create_change(sspec_root, 'conflict')
        _set_spec_status(c1, 'DONE')
        info1 = parse_change(c1)
        archive_change(sspec_root, info1)

        # Create second change with same name
        c2 = create_change(sspec_root, 'conflict')
        _set_spec_status(c2, 'DONE')
        info2 = parse_change(c2)
        p2 = archive_change(sspec_root, info2)
        assert p2.exists()

    def test_updates_references_inside_archive_dirs(self, sspec_root: Path):
        change_path = create_change(sspec_root, 'archive-refs')
        _set_spec_status(change_path, 'DONE')
        old_change_rel = f'.sspec/changes/{change_path.name}'

        request_archive_dir = sspec_root / 'requests' / 'archive'
        ask_archive_dir = sspec_root / 'asks' / 'archive'
        request_archive_dir.mkdir(parents=True, exist_ok=True)
        ask_archive_dir.mkdir(parents=True, exist_ok=True)

        archived_req = request_archive_dir / 'req.md'
        archived_ask = ask_archive_dir / 'ask.md'
        archived_req.write_text(f'attach-change: {old_change_rel}/spec.md\n', encoding='utf-8')
        archived_ask.write_text(f'change: {old_change_rel}/spec.md\n', encoding='utf-8')

        info = parse_change(change_path)
        archive_path = archive_change(sspec_root, info)
        new_change_rel = archive_path.relative_to(sspec_root.parent).as_posix()

        req_content = archived_req.read_text(encoding='utf-8')
        ask_content = archived_ask.read_text(encoding='utf-8')
        assert f'{new_change_rel}/spec.md' in req_content
        assert f'{new_change_rel}/spec.md' in ask_content


# ---------------------------------------------------------------------------
# validate_change
# ---------------------------------------------------------------------------


class TestValidateChange:
    def test_valid_template_has_template_warnings(self, sspec_root: Path):
        """Freshly created change should have warnings about empty template sections."""
        change_path = create_change(sspec_root, 'validate-test')
        issues = validate_change(change_path)
        # Template has unfilled sections → should produce issues
        assert len(issues) > 0

    def test_missing_files_reported(self, tmp_path: Path):
        """Missing spec.md/tasks.md/handover.md should be flagged."""
        empty_change = tmp_path / 'empty-change'
        empty_change.mkdir()
        issues = validate_change(empty_change)
        assert any('spec.md' in i for i in issues)
        assert any('tasks.md' in i for i in issues)
        assert any('handover.md' in i for i in issues)

    def test_filled_spec_reduces_issues(self, sspec_root: Path):
        change_path = create_change(sspec_root, 'filled')
        # Fill in spec sections
        spec = change_path / 'spec.md'
        # Ensure sections A, B, C have content
        filled = (
            '---\nname: filled\nstatus: DOING\n---\n'
            '## A. Problem\nUsers need auth\n'
            '## B. Solution\nAdd OAuth\n'
            '## C. Implementation\nmodify auth.py\n'
        )
        spec.write_text(filled, encoding='utf-8')

        # Add real tasks
        _write_tasks(change_path, done=1, total=3)

        # Fill handover background
        handover = change_path / 'handover.md'
        handover.write_text('## Background\nImplementing auth system\n', encoding='utf-8')

        issues = validate_change(change_path)
        # Should have fewer or no issues about empty sections
        assert not any('no content' in i.lower() for i in issues)
        assert not any('No tasks defined' in i for i in issues)
        assert not any('Background section empty' in i for i in issues)
