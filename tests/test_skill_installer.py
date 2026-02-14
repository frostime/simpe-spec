"""Tests for sspec.skill_installer helpers."""

from __future__ import annotations

from pathlib import Path

from sspec import skill_installer
from sspec.skill_installer import (
    GITIGNORE_FENCE_END,
    GITIGNORE_FENCE_START,
    SkillInstaller,
    check_path_link,
)


def test_check_path_link_for_regular_path(tmp_path: Path):
    normal_dir = tmp_path / 'normal'
    normal_dir.mkdir()
    assert check_path_link(normal_dir) is False


def test_check_path_link_detects_junction_via_helper(monkeypatch, tmp_path: Path):
    maybe_junction = tmp_path / 'junction-like'
    maybe_junction.mkdir()

    monkeypatch.setattr(skill_installer, '_is_junction', lambda path: path == maybe_junction)
    assert check_path_link(maybe_junction) is True


def test_gitignore_fence_upsert_is_idempotent(tmp_path: Path):
    target_a = tmp_path / '.github' / 'skills'
    target_b = tmp_path / '.github' / 'skills'

    SkillInstaller.add_skill_to_gitignore(target_a)
    SkillInstaller.add_skill_to_gitignore(target_b)
    SkillInstaller.add_skill_to_gitignore(target_a)

    gitignore_path = tmp_path / '.github' / '.gitignore'
    content = gitignore_path.read_text(encoding='utf-8')

    assert content.count(GITIGNORE_FENCE_START) == 1
    assert content.count(GITIGNORE_FENCE_END) == 1
    assert '\nskills\n' in content


def test_install_batch_uses_junction_fallback(monkeypatch, tmp_path: Path):
    source = tmp_path / 'source-skills'
    source.mkdir()
    (source / 'SKILL.md').write_text('# demo', encoding='utf-8')
    target = tmp_path / 'target-skills'

    installer = SkillInstaller()
    monkeypatch.setattr(installer, '_try_create_symlink', lambda _s, _t: False)
    monkeypatch.setattr(installer, '_try_create_junction', lambda _s, _t: True)
    monkeypatch.setattr(installer._elevation, 'try_elevated_symlinks', lambda _pairs: [False])
    monkeypatch.setattr(skill_installer.sys, 'platform', 'win32')

    results = installer.install_batch([(source, target)], prefer_symlink=True)

    assert len(results) == 1
    assert results[0].strategy == 'junction'
