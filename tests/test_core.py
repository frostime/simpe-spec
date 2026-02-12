"""Tests for sspec.core — types, constants, template rendering, path resolution."""

from __future__ import annotations

from pathlib import Path

import pytest

from sspec.core import (
    SCHEMA_VERSION,
    SSPEC_DIR,
    ChangeStatus,
    RequestStatus,
    SkillInfo,
    copy_template,
    find_sspec_root,
    get_template_dir,
    get_workspace_skill_targets,
    list_skills,
    list_template_skills,
    normalize_status,
    parse_skill_metadata,
    render_template,
)


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------


class TestRenderTemplate:
    def test_basic_replacement(self):
        assert render_template('Hello {{NAME}}!', {'NAME': 'World'}) == 'Hello World!'

    def test_multiple_placeholders(self):
        tpl = '{{A}} and {{B}}'
        assert render_template(tpl, {'A': 'X', 'B': 'Y'}) == 'X and Y'

    def test_missing_key_becomes_empty(self):
        """Undefined placeholders are silently replaced with empty string."""
        assert render_template('{{MISSING}}', {}) == ''

    def test_whitespace_inside_braces(self):
        assert render_template('{{ NAME }}', {'NAME': 'ok'}) == 'ok'
        assert render_template('{{  NAME  }}', {'NAME': 'ok'}) == 'ok'

    def test_no_placeholders(self):
        text = 'plain text without variables'
        assert render_template(text, {'X': 'Y'}) == text

    def test_repeated_placeholder(self):
        tpl = '{{X}}-{{X}}'
        assert render_template(tpl, {'X': 'a'}) == 'a-a'


# ---------------------------------------------------------------------------
# normalize_status
# ---------------------------------------------------------------------------


class TestNormalizeStatus:
    """Test status normalization with canonical values and aliases."""

    @pytest.mark.parametrize(
        'raw, expected',
        [
            ('PLANNING', 'PLANNING'),
            ('DOING', 'DOING'),
            ('BLOCKED', 'BLOCKED'),
            ('REVIEW', 'REVIEW'),
            ('DONE', 'DONE'),
            ('CLOSED', 'CLOSED'),
        ],
    )
    def test_canonical_change_statuses(self, raw: str, expected: str):
        assert normalize_status(raw, ChangeStatus) == expected

    @pytest.mark.parametrize(
        'alias, expected',
        [
            ('DESIGN', 'PLANNING'),
            ('设计中', 'PLANNING'),
            ('DEV', 'DOING'),
            ('IN_PROGRESS', 'DOING'),
            ('IN-PROGRESS', 'DOING'),
            ('进行中', 'DOING'),
            ('HANGUP', 'BLOCKED'),
            ('IN_REVIEW', 'REVIEW'),
            ('REVIEWING', 'REVIEW'),
            ('COMPLETED', 'DONE'),
            ('FINISHED', 'DONE'),
            ('CANCELLED', 'CLOSED'),
            ('CANCELED', 'CLOSED'),
        ],
    )
    def test_change_status_aliases(self, alias: str, expected: str):
        assert normalize_status(alias, ChangeStatus) == expected

    @pytest.mark.parametrize(
        'alias, expected',
        [
            ('OPEN', 'OPEN'),
            ('TODO', 'OPEN'),
            ('TO_DO', 'OPEN'),
            ('RESOLVED', 'DONE'),
        ],
    )
    def test_request_status_aliases(self, alias: str, expected: str):
        assert normalize_status(alias, RequestStatus) == expected

    def test_case_insensitive(self):
        assert normalize_status('doing', ChangeStatus) == 'DOING'
        assert normalize_status('  Doing  ', ChangeStatus) == 'DOING'

    def test_unknown_status_returned_as_is(self):
        result = normalize_status('INVENTED', ChangeStatus)
        assert result == 'INVENTED'


# ---------------------------------------------------------------------------
# find_sspec_root
# ---------------------------------------------------------------------------


class TestFindSspecRoot:
    def test_returns_none_for_empty_dir(self, tmp_path: Path):
        assert find_sspec_root(tmp_path) is None

    def test_finds_root_at_start(self, tmp_project: Path):
        result = find_sspec_root(tmp_project)
        assert result is not None
        assert result == tmp_project / SSPEC_DIR

    def test_finds_root_from_subdirectory(self, tmp_project: Path):
        sub = tmp_project / 'src' / 'deep'
        sub.mkdir(parents=True)
        result = find_sspec_root(sub)
        assert result is not None
        assert result == tmp_project / SSPEC_DIR

    def test_returns_none_without_project_md(self, tmp_path: Path):
        """A bare .sspec/ without project.md is not a valid project."""
        (tmp_path / SSPEC_DIR).mkdir()
        assert find_sspec_root(tmp_path) is None


# ---------------------------------------------------------------------------
# get_template_dir / list_template_skills
# ---------------------------------------------------------------------------


class TestTemplateDir:
    def test_template_dir_exists(self):
        tdir = get_template_dir()
        assert tdir.is_dir()
        assert (tdir / 'AGENTS.md').exists()
        assert (tdir / 'project.md').exists()

    def test_list_template_skills_returns_dirs_with_skill_md(self):
        skills = list_template_skills()
        assert len(skills) > 0
        for skill_dir in skills:
            assert (skill_dir / 'SKILL.md').exists()


# ---------------------------------------------------------------------------
# copy_template
# ---------------------------------------------------------------------------


class TestCopyTemplate:
    def test_copy_file_with_replacements(self, tmp_path: Path):
        src = tmp_path / 'src.md'
        src.write_text('Version: {{SCHEMA_VERSION}}', encoding='utf-8')
        dest = tmp_path / 'dest.md'
        copy_template(src, dest, {'SCHEMA_VERSION': '6.1'})
        assert dest.read_text(encoding='utf-8') == 'Version: 6.1'

    def test_copy_directory_recursively(self, tmp_path: Path):
        src_dir = tmp_path / 'tpl'
        src_dir.mkdir()
        (src_dir / 'a.md').write_text('{{X}}', encoding='utf-8')
        sub = src_dir / 'sub'
        sub.mkdir()
        (sub / 'b.md').write_text('{{Y}}', encoding='utf-8')

        dest_dir = tmp_path / 'out'
        copy_template(src_dir, dest_dir, {'X': 'hello', 'Y': 'world'})

        assert (dest_dir / 'a.md').read_text(encoding='utf-8') == 'hello'
        assert (dest_dir / 'sub' / 'b.md').read_text(encoding='utf-8') == 'world'


# ---------------------------------------------------------------------------
# parse_skill_metadata
# ---------------------------------------------------------------------------


class TestParseSkillMetadata:
    def test_valid_yaml_frontmatter(self, tmp_path: Path):
        skill = tmp_path / 'SKILL.md'
        skill.write_text('---\nname: test-skill\ndescription: A test\n---\nBody\n', encoding='utf-8')
        meta = parse_skill_metadata(skill)
        assert meta['name'] == 'test-skill'
        assert meta['description'] == 'A test'

    def test_no_frontmatter(self, tmp_path: Path):
        skill = tmp_path / 'SKILL.md'
        skill.write_text('# No frontmatter\n', encoding='utf-8')
        assert parse_skill_metadata(skill) == {}

    def test_missing_file(self, tmp_path: Path):
        assert parse_skill_metadata(tmp_path / 'nope.md') == {}

    def test_with_replacements(self, tmp_path: Path):
        skill = tmp_path / 'SKILL.md'
        skill.write_text('---\nversion: {{VER}}\n---\nBody\n', encoding='utf-8')
        meta = parse_skill_metadata(skill, {'VER': '2.0'})
        assert meta['version'] == 2.0  # YAML parses as number


# ---------------------------------------------------------------------------
# get_workspace_skill_targets
# ---------------------------------------------------------------------------


class TestGetWorkspaceSkillTargets:
    def test_with_primary_location(self, tmp_path: Path):
        targets = get_workspace_skill_targets(tmp_path, primary_loc='.claude')
        paths = [str(t.relative_to(tmp_path)) for t in targets]
        assert '.claude/skills' in [p.replace('\\', '/') for p in paths]
        assert '.sspec/skills' in [p.replace('\\', '/') for p in paths]

    def test_auto_detect_existing_dirs(self, tmp_path: Path):
        (tmp_path / '.github').mkdir()
        targets = get_workspace_skill_targets(tmp_path, primary_loc=None)
        paths = [t.relative_to(tmp_path).as_posix() for t in targets]
        assert '.github/skills' in paths
        assert '.sspec/skills' in paths

    def test_always_includes_sspec_skills(self, tmp_path: Path):
        targets = get_workspace_skill_targets(tmp_path, primary_loc='.sspec')
        assert len(targets) == 1
        assert targets[0] == tmp_path / SSPEC_DIR / 'skills'


# ---------------------------------------------------------------------------
# list_skills
# ---------------------------------------------------------------------------


class TestListSkills:
    def test_empty_skills_dir(self, sspec_root: Path):
        skills = list_skills(sspec_root)
        assert skills == []

    def test_skills_from_directory(self, sspec_root: Path):
        skill_dir = sspec_root / 'skills' / 'my-skill'
        skill_dir.mkdir(parents=True)
        (skill_dir / 'SKILL.md').write_text(
            '---\nname: my-skill\ndescription: desc\n---\n# Skill\n', encoding='utf-8'
        )
        skills = list_skills(sspec_root)
        assert len(skills) == 1
        assert skills[0]['skill'] == 'my-skill'
        assert skills[0]['description'] == 'desc'

    def test_skills_from_flat_file(self, sspec_root: Path):
        skill_file = sspec_root / 'skills' / 'flat.md'
        skill_file.write_text(
            '---\nname: flat-skill\ndescription: flat\n---\n', encoding='utf-8'
        )
        skills = list_skills(sspec_root)
        assert any(s['skill'] == 'flat-skill' for s in skills)

    def test_skills_sorted_by_name(self, sspec_root: Path):
        for name in ['zebra', 'alpha', 'middle']:
            d = sspec_root / 'skills' / name
            d.mkdir(parents=True)
            (d / 'SKILL.md').write_text(f'---\nname: {name}\n---\n', encoding='utf-8')
        skills = list_skills(sspec_root)
        names = [s['skill'] for s in skills]
        assert names == sorted(names)
