"""Command-level tests for `sspec ask` workflows."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from sspec.cli import main
from sspec.services.ask_service import create_ask_template


def test_ask_prompt_prints_utf8_file_note(sspec_root: Path, monkeypatch) -> None:
    ask_path, _ = create_ask_template(sspec_root, 'encoding-note')
    content = ask_path.read_text(encoding='utf-8')
    content = content.replace('<brief_reason>', 'Need user input')
    content = content.replace('<YOUR_QUESTION_HERE>', 'What should we do?')
    content = content.replace('USER_FILL_HERE', '保持 UTF-8 即可')
    ask_path.write_text(content, encoding='utf-8')

    monkeypatch.chdir(sspec_root.parent)
    runner = CliRunner()
    result = runner.invoke(main, ['ask', 'prompt', str(ask_path)])

    assert result.exit_code == 0
    assert '[OK] Ask recorded to: .sspec/asks/' in result.output
    assert 'Note: If the answer output below looks garbled in this terminal, open' in result.output
    assert '(UTF-8).' in result.output
    assert 'Answer:' in result.output
    assert '保持 UTF-8 即可' in result.output
