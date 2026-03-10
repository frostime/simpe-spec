"""Command-level tests for `sspec howto` workflows."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from sspec.cli import main
from sspec.services.howto_service import collect_howtos
from sspec.services.project_init_service import initialize_project

LOCAL_GUIDE = '---\nname: local-guide\ndesc: local test guide\n---\n\nFollow the steps.\n'


def _init_project(tmp_path: Path) -> Path:
    initialize_project(
        project_root=tmp_path,
        force=False,
        skill_locations=[],
        prefer_symlink=False,
    )
    return tmp_path / '.sspec'


def test_howto_list_uses_plain_text_default_output(tmp_path: Path, monkeypatch) -> None:
    sspec_root = _init_project(tmp_path)
    (sspec_root / 'howto' / 'local-guide.md').write_text(LOCAL_GUIDE, encoding='utf-8')

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['howto', '--list'])

    assert result.exit_code == 0
    assert '- name: local-guide' in result.output
    assert '  source: project' in result.output
    assert '  desc: local test guide' in result.output
    assert '- name:' in result.output


def test_howto_implicit_read_renders_body_without_frontmatter(
    tmp_path: Path,
    monkeypatch,
) -> None:
    sspec_root = _init_project(tmp_path)
    (sspec_root / 'howto' / 'local-guide.md').write_text(LOCAL_GUIDE, encoding='utf-8')

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['howto', 'Local_Guide'])

    assert result.exit_code == 0
    assert '===== HOWTO/local-guide =====' in result.output
    assert '# local-guide' in result.output
    assert 'Follow the steps.' in result.output
    assert '---\nname:' not in result.output
    assert 'source: project' not in result.output


def test_howto_rich_format_uses_pretty_rendering(tmp_path: Path, monkeypatch) -> None:
    sspec_root = _init_project(tmp_path)
    (sspec_root / 'howto' / 'local-guide.md').write_text(LOCAL_GUIDE, encoding='utf-8')

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['howto', 'local-guide', '--format', 'rich'])

    assert result.exit_code == 0
    assert 'HOWTO: local-guide' in result.output
    assert 'local test guide' in result.output
    assert 'source: project' not in result.output


def test_howto_read_supports_multiple_names(tmp_path: Path, monkeypatch) -> None:
    sspec_root = _init_project(tmp_path)
    (sspec_root / 'howto' / 'local-guide.md').write_text(LOCAL_GUIDE, encoding='utf-8')
    (sspec_root / 'howto' / 'extra-guide.md').write_text(
        '---\nname: extra-guide\ndesc: extra guide\n---\n\nSecond body.\n',
        encoding='utf-8',
    )

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['howto', 'read', 'local-guide', 'extra-guide'])

    assert result.exit_code == 0
    assert '===== HOWTO/local-guide =====' in result.output
    assert '===== HOWTO/extra-guide =====' in result.output
    assert 'Second body.' in result.output
    assert '\n\n\n===== HOWTO/extra-guide =====' in result.output


def test_howto_list_and_read_work_without_sspec_project(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ['howto', '--list'])
    assert result.exit_code == 0
    assert 'source: builtin' in result.output

    result = runner.invoke(main, ['howto', 'write-howto'])
    assert result.exit_code == 0
    assert '===== HOWTO/write-howto =====' in result.output


def test_howto_can_use_standalone_sspec_howto_dir(tmp_path: Path, monkeypatch) -> None:
    # Standalone mode: `.sspec/howto/` exists, but `.sspec/project.md` is absent.
    sspec_howto_dir = tmp_path / '.sspec' / 'howto'
    sspec_howto_dir.mkdir(parents=True, exist_ok=True)
    (sspec_howto_dir / 'local-guide.md').write_text(LOCAL_GUIDE, encoding='utf-8')

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(main, ['howto', '--list'])
    assert result.exit_code == 0
    assert '- name: local-guide' in result.output
    assert '  source: project' in result.output

    result = runner.invoke(main, ['howto', 'local-guide'])
    assert result.exit_code == 0
    assert '===== HOWTO/local-guide =====' in result.output


def test_howto_new_creates_project_file(tmp_path: Path, monkeypatch) -> None:
    sspec_root = _init_project(tmp_path)

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['howto', 'new', 'draft-guide'])

    created = sspec_root / 'howto' / 'draft-guide.md'
    assert result.exit_code == 0
    assert created.exists()
    assert "Created HOWTO 'draft-guide'" in result.output
    assert 'name: draft-guide' in created.read_text(encoding='utf-8')
    assert '# draft-guide' not in created.read_text(encoding='utf-8')


def test_howto_duplicate_warning_skips_project_conflict(
    tmp_path: Path,
    monkeypatch,
) -> None:
    sspec_root = _init_project(tmp_path)
    builtin_name = next(
        item.name for item in collect_howtos(sspec_root).items if item.source == 'builtin'
    )
    project_howto = sspec_root / 'howto' / f'{builtin_name}.md'
    project_howto.write_text(
        (f'---\nname: {builtin_name}\ndesc: project-only duplicate marker\n---\n\n# duplicate\n'),
        encoding='utf-8',
    )

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['howto', '--list'])

    assert result.exit_code == 0
    assert 'WARNING: Skipped duplicate HOWTO' in result.output
    assert builtin_name in result.output
    assert 'project-only duplicate marker' not in result.output


def test_howto_help_mentions_implicit_read_shorthand(tmp_path: Path, monkeypatch) -> None:
    _init_project(tmp_path)

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['howto', '--help'])

    assert result.exit_code == 0
    assert '`sspec howto <name>` is shorthand' in result.output
    assert '--format [plain|rich]' in result.output


def test_howto_without_name_or_list_errors(tmp_path: Path, monkeypatch) -> None:
    _init_project(tmp_path)

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['howto'])

    assert result.exit_code != 0
    assert 'Provide a HOWTO name or use --list.' in result.output
