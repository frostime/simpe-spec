"""Command-level tests for builtin `sspec tool` helpers."""

from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

from click.testing import CliRunner

from sspec.cli import main

ISO_MINUTE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}[+-]\d{2}:\d{2}\n?$')
ISO_SECOND_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}\n?$')
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}\n?$')


def test_tool_treesitter_prompt_output() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ['tool', 'treesitter', '--prompt'])

    assert result.exit_code == 0
    assert '# treesitter - Python Symbol Outline' in result.output


def test_tool_treesitter_returns_dependency_hint_when_missing(monkeypatch) -> None:
    from sspec.builtin_tools import treesitter

    runner = CliRunner()

    with runner.isolated_filesystem():
        target = Path('demo.py')
        target.write_text('def demo():\n    return 1\n', encoding='utf-8')

        monkeypatch.setattr(
            treesitter,
            '_check_tree_sitter_dependency',
            lambda lang: (
                False,
                f'missing deps for {lang}',
            ),
        )

        result = runner.invoke(main, ['tool', 'treesitter', str(target)])

        assert result.exit_code != 0
        assert 'missing deps for py' in result.output


def test_tool_treesitter_supports_depth_option(monkeypatch) -> None:
    from sspec.builtin_tools import treesitter

    runner = CliRunner()

    with runner.isolated_filesystem():
        target = Path('demo.py')
        target.write_text('def demo():\n    return 1\n', encoding='utf-8')

        monkeypatch.setattr(
            treesitter,
            '_check_tree_sitter_dependency',
            lambda lang: (True, None),
        )
        monkeypatch.setattr(
            treesitter,
            'pyfile_symbols_outline',
            lambda file_path, max_depth: (
                f'outline depth={max_depth} file={Path(file_path).name}'
            ),
        )

        result = runner.invoke(main, ['tool', 'treesitter', str(target), '--depth', '2'])

        assert result.exit_code == 0
        assert 'outline depth=2 file=demo.py' in result.output


def test_tool_treesitter_supports_ts_with_orthogonal_dependency(monkeypatch) -> None:
    from sspec.builtin_tools import treesitter

    runner = CliRunner()

    with runner.isolated_filesystem():
        target = Path('demo.ts')
        target.write_text('const id = 1\n', encoding='utf-8')

        monkeypatch.setattr(
            treesitter,
            '_check_tree_sitter_dependency',
            lambda lang: (lang == 'ts', 'missing deps for ts'),
        )
        monkeypatch.setattr(
            treesitter,
            'jstsfile_symbols_outline',
            lambda file_path, max_depth, lang: (
                f'outline depth={max_depth} lang={lang} file={Path(file_path).name}'
            ),
        )

        result = runner.invoke(main, ['tool', 'treesitter', str(target), '--depth', '1'])

        assert result.exit_code == 0
        assert 'outline depth=1 lang=ts file=demo.ts' in result.output


def test_tool_now_outputs_local_iso_timestamp() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ['tool', 'now'])

    assert result.exit_code == 0
    assert ISO_MINUTE_RE.fullmatch(result.output)


def test_tool_now_supports_date_only_output() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ['tool', 'now', '--date'])

    assert result.exit_code == 0
    assert DATE_RE.fullmatch(result.output)


def test_tool_now_supports_seconds_and_utc() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ['tool', 'now', '--seconds', '--utc'])

    assert result.exit_code == 0
    assert ISO_SECOND_RE.fullmatch(result.output)
    assert result.output.rstrip().endswith('+00:00')


def test_tool_now_supports_json_output() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ['tool', 'now', '--json'])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert set(payload) == {'timestamp', 'date', 'timezone', 'local', 'utc'}
    assert ISO_MINUTE_RE.fullmatch(payload['timestamp'])
    assert DATE_RE.fullmatch(payload['date'])
    assert ISO_MINUTE_RE.fullmatch(payload['local'])
    assert ISO_MINUTE_RE.fullmatch(payload['utc'])


def test_tool_write_create_with_text_outside_sspec_project() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        target = Path('note.txt').resolve()
        result = runner.invoke(
            main,
            ['tool', 'write', str(target), '--mode', 'create', '--text', 'hello\nworld\n'],
        )

        assert result.exit_code == 0
        assert target.read_text(encoding='utf-8') == 'hello\nworld\n'
        assert 'create wrote' in result.output


def test_tool_write_prompt_does_not_require_target() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ['tool', 'write', '--prompt'])

    assert result.exit_code == 0
    assert '# write - Explicit File Writing Helper' in result.output


def test_tool_patch_accepts_stdin_input() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        target = Path('note.txt')
        target.write_text('old\n', encoding='utf-8')
        patch_text = """# note.txt
<<<<<<< SEARCH
old
=======
new
>>>>>>> REPLACE
"""

        result = runner.invoke(
            main,
            ['tool', 'patch', '--stdin', '--yes'],
            input=patch_text,
        )

        assert result.exit_code == 0
        assert target.read_text(encoding='utf-8') == 'new\n'


def test_tool_patch_failure_outside_sspec_writes_temp_markdown_bundle() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        target = Path('note.txt')
        target.write_text('alpha\n', encoding='utf-8')
        patch_text = """# note.txt
<<<<<<< SEARCH
missing
=======
beta
>>>>>>> REPLACE
"""

        result = runner.invoke(
            main,
            ['tool', 'patch', '--stdin', '--yes'],
            input=patch_text,
        )

        assert result.exit_code == 1
        assert 'File: note.txt' in result.output
        assert 'Patch line: L1' in result.output
        assert '<<<<<<< SEARCH' in result.output
        assert not Path('.sspec').exists()

        match = re.search(r'Full failed patch bundle:\s*(.+)\r?\n', result.output)
        assert match is not None
        bundle_path = Path(match.group(1).strip())
        assert bundle_path.exists()
        content = bundle_path.read_text(encoding='utf-8')
        assert '## Failed Patch 1' in content
        assert '```patch' in content


def test_tool_patch_bundle_markdown_is_reusable_as_patch_input() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        target = Path('note.txt')
        target.write_text('alpha\n', encoding='utf-8')
        patch_text = """# note.txt
<<<<<<< SEARCH
missing
=======
beta
>>>>>>> REPLACE
"""

        failed = runner.invoke(
            main,
            ['tool', 'patch', '--stdin', '--yes'],
            input=patch_text,
        )
        assert failed.exit_code == 1

        match = re.search(r'Full failed patch bundle:\s*(.+)\r?\n', failed.output)
        assert match is not None
        bundle_path = Path(match.group(1).strip())

        target.write_text('missing\n', encoding='utf-8')
        rerun = runner.invoke(main, ['tool', 'patch', str(bundle_path), '--yes'])

        assert rerun.exit_code == 0
        assert target.read_text(encoding='utf-8') == 'beta\n'


def test_tool_patch_open_ended_range_preview_uses_canonical_scope() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        target = Path('note.txt')
        target.write_text('one\ntwo\nthree\n', encoding='utf-8')
        patch_path = Path('patch.md')
        patch_path.write_text(
            """# note.txt:L2-
<<<<<<< SEARCH
two
three
=======
TWO
THREE
>>>>>>> REPLACE
""",
            encoding='utf-8',
        )

        result = runner.invoke(main, ['tool', 'patch', str(patch_path), '--dry-run'])

        assert result.exit_code == 0
        assert 'L2-' in result.output
        assert 'L2-LNone' not in result.output


def test_tool_patch_dry_run_warns_for_outside_workspace_absolute_paths() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem(), tempfile.TemporaryDirectory() as external_dir:
        external_target = Path(external_dir) / 'note.txt'
        external_target.write_text('old\n', encoding='utf-8')
        patch_path = Path('patch.md')
        patch_path.write_text(
            f"""# {external_target}
<<<<<<< SEARCH
old
=======
new
>>>>>>> REPLACE
""",
            encoding='utf-8',
        )

        result = runner.invoke(main, ['tool', 'patch', str(patch_path), '--dry-run'])

        assert result.exit_code == 0
        assert 'Absolute path(s) outside the current workspace' in result.output
        assert 'Dry-run note:' in result.output
        assert external_target.read_text(encoding='utf-8') == 'old\n'


def test_tool_patch_absolute_path_outside_workspace_requires_confirmation() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem(), tempfile.TemporaryDirectory() as external_dir:
        external_target = Path(external_dir) / 'note.txt'
        external_target.write_text('old\n', encoding='utf-8')
        patch_path = Path('patch.md')
        patch_path.write_text(
            f"""# {external_target}
<<<<<<< SEARCH
old
=======
new
>>>>>>> REPLACE
""",
            encoding='utf-8',
        )

        denied = runner.invoke(main, ['tool', 'patch', str(patch_path), '--yes'], input='n\n')
        assert denied.exit_code != 0
        assert 'Absolute path(s) outside the current workspace' in denied.output
        assert external_target.read_text(encoding='utf-8') == 'old\n'

        allowed = runner.invoke(main, ['tool', 'patch', str(patch_path), '--yes'], input='y\n')
        assert allowed.exit_code == 0
        assert external_target.read_text(encoding='utf-8') == 'new\n'


def test_tool_patch_stdin_requires_unsafe_for_absolute_path_outside_workspace() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem(), tempfile.TemporaryDirectory() as external_dir:
        external_target = Path(external_dir) / 'note.txt'
        external_target.write_text('old\n', encoding='utf-8')
        patch_text = f"""# {external_target}
<<<<<<< SEARCH
old
=======
new
>>>>>>> REPLACE
"""

        blocked = runner.invoke(main, ['tool', 'patch', '--stdin', '--yes'], input=patch_text)
        assert blocked.exit_code == 1
        assert '--stdin` mode cannot request outside-workspace confirmation' in blocked.output
        assert external_target.read_text(encoding='utf-8') == 'old\n'

        allowed = runner.invoke(
            main,
            ['tool', 'patch', '--stdin', '--yes', '--unsafe'],
            input=patch_text,
        )
        assert allowed.exit_code == 0
        assert 'Unsafe mode:' in allowed.output
        assert external_target.read_text(encoding='utf-8') == 'new\n'


def test_tool_patch_supports_paths_with_spaces() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        target = Path('note space.txt')
        target.write_text('old\n', encoding='utf-8')
        patch_text = """# note space.txt
<<<<<<< SEARCH
old
=======
new
>>>>>>> REPLACE
"""

        result = runner.invoke(main, ['tool', 'patch', '--stdin', '--yes'], input=patch_text)

        assert result.exit_code == 0
        assert target.read_text(encoding='utf-8') == 'new\n'


def test_tool_write_append_with_stdin_preserves_existing_newlines() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        target = Path('note.txt')
        target.write_text('alpha\r\n', encoding='utf-8', newline='')

        result = runner.invoke(
            main,
            ['tool', 'write', 'note.txt', '--mode', 'append', '--stdin'],
            input='beta\ngamma\n',
        )

        assert result.exit_code == 0
        with target.open('r', encoding='utf-8', newline='') as handle:
            assert handle.read() == 'alpha\r\nbeta\r\ngamma\r\n'


def test_tool_fileinfo_supports_directories_globs_and_json() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        docs = Path('docs')
        docs.mkdir()
        nested = docs / 'nested'
        nested.mkdir()

        (docs / 'a.txt').write_text('hello\nworld\n', encoding='utf-8', newline='')
        (nested / 'b.txt').write_text('nihao\r\n', encoding='utf-8', newline='')

        result = runner.invoke(main, ['tool', 'fileinfo', 'docs', '*.txt', '--json'])

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload['count'] == 2
        assert payload['missing_sources'] == []

        by_name = {Path(item['path']).name: item for item in payload['files']}
        assert by_name['a.txt']['encoding'] == 'utf-8'
        assert by_name['a.txt']['newline'] == 'lf'
        assert by_name['a.txt']['line_count'] == 2
        assert by_name['b.txt']['newline'] == 'crlf'
