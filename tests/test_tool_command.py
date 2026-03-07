"""Command-level tests for builtin `sspec tool` helpers."""

from __future__ import annotations

import json
import re

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
