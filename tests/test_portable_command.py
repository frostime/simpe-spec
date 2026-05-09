"""Command-level tests for `sspec portable`."""

from __future__ import annotations

import re
from pathlib import Path

from click.testing import CliRunner

from sspec.cli import main


def test_portable_works_without_sspec_project(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ['portable'])

    assert result.exit_code == 0
    assert '<sspec-portable schema=' in result.output
    assert '<what_is_this>' in result.output
    assert '<portable_constraints>' in result.output
    assert '<available_skills>' in result.output
    assert 'sspec portable read rule:sspec' in result.output
    assert not (tmp_path / '.sspec').exists()


def test_portable_read_rule_works_without_sspec_project(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ['portable', 'read', 'rule:sspec'])

    assert result.exit_code == 0
    assert '<ref>rule:sspec</ref>' in result.output
    source = _extract_source(result.output)
    assert source.is_absolute()
    assert source.parts[-3:] == ('sspec', 'templates', 'AGENTS.md')
    assert 'SSPEC_SCHEMA::6.0' in result.output
    assert not (tmp_path / '.sspec').exists()


def test_portable_read_skill_and_attachment(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    skill = runner.invoke(main, ['portable', 'read', 'skill:sspec-design'])
    attachment = runner.invoke(
        main,
        ['portable', 'read', 'skill:sspec-design/examples-feature.md'],
    )

    assert skill.exit_code == 0
    skill_source = _extract_source(skill.output)
    assert skill_source.is_absolute()
    assert skill_source.parts[-5:] == ('sspec', 'templates', 'skills', 'sspec-design', 'SKILL.md')
    assert '# SSPEC Design' in skill.output
    assert attachment.exit_code == 0
    attachment_source = _extract_source(attachment.output)
    assert attachment_source.is_absolute()
    assert attachment_source.parts[-5:] == (
        'sspec',
        'templates',
        'skills',
        'sspec-design',
        'examples-feature.md',
    )


def test_portable_read_howto_and_template(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    howto = runner.invoke(main, ['portable', 'read', 'howto:write-memory'])
    template = runner.invoke(main, ['portable', 'read', 'template:change/spec.md'])

    assert howto.exit_code == 0
    assert _extract_source(howto.output).parts[-3:] == ('sspec', 'howto', 'write-memory.md')
    assert _extract_source(howto.output).is_absolute()
    assert template.exit_code == 0
    assert _extract_source(template.output).parts[-4:] == (
        'sspec',
        'templates',
        'change',
        'spec.md',
    )
    assert _extract_source(template.output).is_absolute()
    assert 'Problem Statement' in template.output


def test_portable_read_reports_clear_errors(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ['portable', 'read', 'rule:portable'])

    assert result.exit_code != 0
    assert 'Unknown portable rule: portable' in result.output


def test_portable_read_rejects_unsafe_path(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ['portable', 'read', 'skill:../core.py'])

    assert result.exit_code != 0
    assert 'Unsafe resource path.' in result.output


def _extract_source(output: str) -> Path:
    match = re.search(r'<source>(.+)</source>', output)
    assert match is not None
    return Path(match.group(1))
