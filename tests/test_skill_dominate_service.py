"""Tests for skill dominate service workflow."""

from __future__ import annotations

from pathlib import Path

from sspec.services import skill_service


def _write_skill(root: Path, name: str, body: str) -> None:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / 'SKILL.md').write_text(body, encoding='utf-8')


def test_dominate_links_when_target_missing(monkeypatch, tmp_path: Path):
    sspec_root = tmp_path / '.sspec'
    (sspec_root / 'skills').mkdir(parents=True)

    monkeypatch.setattr(skill_service, '_create_skills_link', lambda **_kwargs: 'junction')

    result = skill_service.dominate_skills_location(
        sspec_root=sspec_root,
        dominate_dir=tmp_path / '.github',
    )

    assert result.status == 'linked'
    assert result.link_kind == 'junction'


def test_dominate_reports_needs_relink_for_wrong_link(monkeypatch, tmp_path: Path):
    sspec_root = tmp_path / '.sspec'
    (sspec_root / 'skills').mkdir(parents=True)

    target = tmp_path / '.claude' / 'skills'
    target.parent.mkdir(parents=True)

    monkeypatch.setattr(skill_service, 'detect_path_link', lambda _path: 'symlink')
    monkeypatch.setattr(skill_service, 'check_path_link', lambda *_args, **_kwargs: False)

    result = skill_service.dominate_skills_location(
        sspec_root=sspec_root,
        dominate_dir=tmp_path / '.claude',
    )

    assert result.status == 'needs_relink'


def test_dominate_merges_directory_then_links(monkeypatch, tmp_path: Path):
    sspec_root = tmp_path / '.sspec'
    hub = sspec_root / 'skills'
    hub.mkdir(parents=True)

    _write_skill(hub, 'same-skill', '# same')
    _write_skill(hub, 'diff-skill', '# old')

    external_skills = tmp_path / '.github' / 'skills'
    _write_skill(external_skills, 'same-skill', '# same')
    _write_skill(external_skills, 'diff-skill', '# new')
    _write_skill(external_skills, 'new-skill', '# another')

    monkeypatch.setattr(skill_service, '_create_skills_link', lambda **_kwargs: 'junction')

    result = skill_service.dominate_skills_location(
        sspec_root=sspec_root,
        dominate_dir=tmp_path / '.github',
    )

    assert result.status == 'merged'
    assert result.backup_path is not None
    assert result.backup_path.exists()
    assert set(result.merged_skills or []) == {'new-skill'}
    assert set(result.conflict_skills or []) == {'diff-skill'}
    assert (hub / 'diff-skill' / 'SKILL.md').read_text(encoding='utf-8') == '# old'
