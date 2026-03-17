"""Command-level tests for builtin `sspec tool` helpers."""

from __future__ import annotations

import json
import re
from pathlib import Path

from click.testing import CliRunner

from sspec.cli import main

ISO_MINUTE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}[+-]\d{2}:\d{2}\n?$')
ISO_SECOND_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}\n?$')
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}\n?$')


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
