from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml


@dataclass
class AskPrompt:
    question: str
    answer: str | None = None
    time: datetime | None = None


def ask_prompt(q: str, tldr: str | None = None) -> str:
    print(f"\n{'='*60}\n  🤖 Agent needs your input\n{'='*60}\n\n{q}\n", file=sys.stderr)
    print('💡 Enter response (type END on new line to finish):', file=sys.stderr)
    lines = []
    try:
        while (line := input()) != 'END':
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass
    result = '\n'.join(lines)
    print(f"\n✓ Received ({len(result)} chars)\n{'='*60}\n", file=sys.stderr)
    return result


def normalize_ask_name(name: str) -> str:
    """Normalize an ask name to kebab-case for safe filenames."""

    normalized = re.sub(r'\s+', '-', name.strip().lower())
    normalized = re.sub(r'[^a-z0-9\-]', '', normalized)
    return normalized


def collect_multiline_input(
    *,
    prompt: str,
    end_token: str = 'END',
    input_fn=input,
    output_stream=sys.stderr,
) -> str:
    """Collect multi-line input until end_token is entered on a new line."""

    print(f"\n{'='*60}\n  🤖 sspec ask\n{'='*60}\n\n{prompt}\n", file=output_stream)
    print(f"💡 Enter response (type {end_token} on new line to finish):", file=output_stream)
    lines: list[str] = []
    try:
        while (line := input_fn()) != end_token:
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass
    result = '\n'.join(lines)
    print(f"\n✓ Received ({len(result)} chars)\n{'='*60}\n", file=output_stream)
    return result


def write_ask_record(
    *,
    sspec_root: Path,
    name: str,
    why: str | None,
    question: str,
    answer: str,
    now: datetime | None = None,
) -> Path:
    """Write an ask record to .sspec/asks and return the created path."""

    asks_dir = sspec_root / 'asks'
    asks_dir.mkdir(parents=True, exist_ok=True)

    normalized = normalize_ask_name(name)
    if not normalized:
        raise ValueError('Invalid ask name')

    dt = now or datetime.now()
    timestamp = dt.isoformat(timespec='seconds')
    timeprefix = dt.strftime('%y%m%d%H%M%S')

    base = f'{timeprefix}_{normalized}'
    path = asks_dir / f'{base}.md'

    if path.exists():
        counter = 1
        while path.exists():
            path = asks_dir / f'{base}_{counter}.md'
            counter += 1

    meta = {
        'created': timestamp,
        'name': normalized,
        'why': (why or '').strip(),
    }
    yaml_text = yaml.dump(meta, allow_unicode=True, sort_keys=False)

    body_parts: list[str] = [f'# Ask: {normalized}', '']

    if why and why.strip():
        body_parts.extend(['## Why', why.strip(), ''])

    body_parts.extend(['## Question', question.strip(), '', '## Answer', answer.strip(), ''])

    content = f'---\n{yaml_text}---\n\n' + '\n'.join(body_parts)
    path.write_text(content, encoding='utf-8')
    return path


def resolve_question(*, question_opt: str, stdin_stream=sys.stdin) -> str:
    """Resolve question from option value. Use '-' to read full stdin."""

    if question_opt.strip() == '-':
        return stdin_stream.read()
    return question_opt
