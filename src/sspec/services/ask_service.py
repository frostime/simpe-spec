from __future__ import annotations

import importlib.util
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from sspec.core import ARCHIVE_DIR
from sspec.libs.path_refs import update_references_in_dirs


@dataclass
class AskPrompt:
    question: str
    answer: str | None = None
    time: datetime | None = None


def extract_ask_name_from_filename(filename: str) -> str:
    """Extract ask name from filename (strip timestamp prefix)."""
    if '_' in filename:
        parts = filename.split('_', 1)
        if len(parts) > 1:
            return parts[1]
    return filename


def find_ask_matches(asks_dir: Path, name: str) -> list[Path]:
    """Find ask file candidates by exact or fuzzy match."""
    if not asks_dir.exists():
        return []

    normalized = name
    if normalized.endswith('.md'):
        normalized = normalized[:-3]

    exact_path = asks_dir / f'{normalized}.md'
    if exact_path.exists():
        return [exact_path]

    matches = list(asks_dir.glob(f'*_{normalized}.md'))
    if matches:
        return sorted(matches)

    contains = [p for p in asks_dir.glob('*.md') if normalized in p.stem]
    if contains:
        return sorted(contains)

    return []


def archive_ask(sspec_root: Path, asks_dir: Path, ask_path: Path) -> Path:
    """Archive a completed ask (.md) by moving it into asks/archive/.

    Also updates references in requests/, changes/, asks/, tmp/ directories,
    including archive subdirectories.
    """
    # Capture old path before moving
    old_ask_relative = ask_path.relative_to(sspec_root.parent).as_posix()

    archive_dir = asks_dir / ARCHIVE_DIR
    archive_dir.mkdir(parents=True, exist_ok=True)

    dest_path = archive_dir / ask_path.name
    counter = 1
    while dest_path.exists():
        dest_path = archive_dir / f'{ask_path.stem}_{counter}.md'
        counter += 1

    shutil.move(str(ask_path), str(dest_path))

    # Update references after moving
    new_ask_relative = dest_path.relative_to(sspec_root.parent).as_posix()
    old_pattern = old_ask_relative

    dirs_to_update = [
        sspec_root / 'requests',
        sspec_root / 'asks',
        sspec_root / 'tmp',
        sspec_root / 'changes',
    ]
    update_references_in_dirs(
        dirs=dirs_to_update,
        replacements={old_pattern: new_ask_relative},
        file_pattern='*.md',
    )

    return dest_path


def ask_prompt(q: str, tldr: str | None = None) -> str:
    print(f'\n{"=" * 60}\n  🤖 Agent needs your input\n{"=" * 60}\n\n{q}\n', file=sys.stderr)
    print('💡 Enter response (type END on new line to finish):', file=sys.stderr)
    lines = []
    try:
        while (line := input()) != 'END':
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass
    result = '\n'.join(lines)
    print(f'\n✓ Received ({len(result)} chars)\n{"=" * 60}\n', file=sys.stderr)
    return result


def normalize_ask_name(name: str) -> tuple[str, str | None]:
    """
    Normalize ask name to Python-safe identifier.

    Converts hyphens and other characters to underscores.
    Returns (normalized_name, warning_message).

    Raises ValueError if result is empty or invalid.
    """
    original = name

    # Convert to lowercase, replace non-alphanumeric (except _) with _
    normalized = re.sub(r'[^a-z0-9_]', '_', name.lower())
    # Remove leading/trailing underscores, collapse multiple underscores
    normalized = re.sub(r'_+', '_', normalized).strip('_')

    if not normalized:
        raise ValueError(f'Invalid ask name: "{name}". Must contain at least one letter or number.')

    # Check if conversion happened
    warning = None
    if normalized != original:
        warning = f'Ask name converted: "{original}" → "{normalized}"'

    return normalized, warning


def collect_multiline_input(
    *,
    prompt: str,
    end_token: str = 'END',
    input_fn=input,
    output_stream=sys.stderr,
) -> str:
    """Collect multi-line input until end_token is entered on a new line."""

    print(
        f'\n{"=" * 60}\n  🤖 sspec ask\n{"=" * 60}\n\n{prompt}\n',
        file=output_stream,
    )
    print(
        f'💡 Enter response (type {end_token} on new line to finish):',
        file=output_stream,
    )
    lines: list[str] = []
    try:
        while (line := input_fn()) != end_token:
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass
    result = '\n'.join(lines)
    print(f'\n✓ Received ({len(result)} chars)\n{"=" * 60}\n', file=output_stream)
    return result


def create_ask_template(sspec_root: Path, name: str) -> tuple[Path, str | None]:
    """
    Create a YAML template file for sspec ask.

    Args:
        sspec_root: .sspec directory path
        name: Ask name (auto-converted to Python-safe identifier)

    Returns:
        Tuple of (Path to created .yml file, warning message if name was converted)

    Raises:
        ValueError: If name is invalid
    """
    normalized, warning = normalize_ask_name(name)

    asks_dir = sspec_root / 'asks'
    asks_dir.mkdir(parents=True, exist_ok=True)

    dt = datetime.now()
    timestamp = dt.isoformat(timespec='seconds')
    timeprefix = dt.strftime('%y%m%d%H%M%S')

    base = f'{timeprefix}_{normalized}'
    yml_path = asks_dir / f'{base}.yml'

    # Handle filename conflicts
    if yml_path.exists():
        counter = 1
        while yml_path.exists():
            yml_path = asks_dir / f'{base}_{counter}.yml'
            counter += 1

        template = f'''created: "{timestamp}"

# EDIT: Why are you asking this question?
reason: |-
  Ask user for <brief_reason>

# EDIT: The question to ask
question: |-
  <YOUR_QUESTION_HERE>

# === NOTE: AGENT SHOULD NOT EDIT BELOW THIS LINE ===
# User can pre-fill answer here to skip terminal input during execution.
user_answer: |
  USER_FILL_HERE
'''

    yml_path.write_text(template, encoding='utf-8')
    return yml_path, warning


def _load_ask_yaml(ask_file_path: Path) -> dict[str, Any]:
    data = yaml.safe_load(ask_file_path.read_text(encoding='utf-8')) or {}
    if not isinstance(data, dict):
        raise AttributeError('Ask YAML must contain a mapping object at top level')
    return data


def _load_ask_py(ask_file_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location('ask_module', ask_file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f'Cannot load ask file: {ask_file_path}')

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def execute_ask_prompt(ask_file_path: Path) -> str:
    """
    Execute an ask prompt from YAML (preferred) or Python (legacy) ask file.

    Args:
        ask_file_path: Path to .yml or .py ask template file

    Returns:
        User's answer string

    Raises:
        FileNotFoundError: If ask file doesn't exist
        AttributeError: If file doesn't have REASON/QUESTION
    """
    if not ask_file_path.exists():
        md_file_path = ask_file_path.with_suffix('.md')
        if md_file_path.exists():
            return (
                f'Warning: Ask already completed and converted to MD: {md_file_path}.'
                ' See that file if needed.'
            )
        else:
            raise FileNotFoundError(f'Ask file not found: {ask_file_path}')

    reason: str
    question: str
    user_answer: str = ''

    if ask_file_path.suffix == '.yml':
        data = _load_ask_yaml(ask_file_path)
        reason = str(data.get('reason', '') or '').strip()
        question = str(data.get('question', '') or '').strip()
        user_answer = str(data.get('user_answer', '') or '').strip()
        if not reason or not question:
            raise AttributeError('Ask YAML must define non-empty reason and question')
    elif ask_file_path.suffix == '.py':
        module = _load_ask_py(ask_file_path)
        if not hasattr(module, 'REASON') or not hasattr(module, 'QUESTION'):
            raise AttributeError('Ask file must define REASON and QUESTION')
        reason = module.REASON.strip()
        question = module.QUESTION.strip()
        if hasattr(module, 'USER_ANSWER'):
            user_answer = module.USER_ANSWER.strip()
    else:
        raise AttributeError(f'Unsupported ask file type: {ask_file_path.suffix}')

    if user_answer:
        return user_answer

    prompt_text = f'**Why**: {reason}\n\n{question}'
    answer = collect_multiline_input(prompt=prompt_text)

    return answer


def save_ask_answer(ask_file_path: Path, answer: str) -> None:
    """
    Persist answer to ask file (.yml preferred, .py legacy).

    Args:
        ask_file_path: Path to .yml or .py ask file
        answer: User's answer to persist
    """
    if ask_file_path.suffix == '.yml':
        data = _load_ask_yaml(ask_file_path)
        data['answer'] = answer
        ask_file_path.write_text(
            yaml.dump(data, allow_unicode=True, sort_keys=False),
            encoding='utf-8',
        )
        return

    if ask_file_path.suffix != '.py':
        raise AttributeError(f'Unsupported ask file type: {ask_file_path.suffix}')

    answer_block = f'\nANSWER = r"""\n{answer}\n"""\n'

    with ask_file_path.open('a', encoding='utf-8') as f:
        f.write(answer_block)


def convert_ask_to_md(ask_path: Path) -> Path:
    """
    Convert ask pending file (.yml/.py) to .md format and delete source file.

    Args:
        ask_path: Path to .yml/.py ask file

    Returns:
        Path to created .md file

    Raises:
        AttributeError: If required attributes missing
    """
    created: str
    reason: str
    question: str
    answer: str

    if ask_path.suffix == '.yml':
        data = _load_ask_yaml(ask_path)
        required_keys = ['created', 'reason', 'question', 'answer']
        for key in required_keys:
            if not data.get(key):
                raise AttributeError(f'Ask YAML missing required key: {key}')
        created = str(data['created'])
        reason = str(data['reason']).strip()
        question = str(data['question']).strip()
        answer = str(data['answer']).strip()
    elif ask_path.suffix == '.py':
        module = _load_ask_py(ask_path)
        required_attrs = ['CREATED', 'REASON', 'QUESTION', 'ANSWER']
        for attr in required_attrs:
            if not hasattr(module, attr):
                raise AttributeError(f'Ask file missing required attribute: {attr}')
        created = module.CREATED
        reason = module.REASON.strip()
        question = module.QUESTION.strip()
        answer = module.ANSWER.strip()
    else:
        raise AttributeError(f'Unsupported ask file type: {ask_path.suffix}')

    name = ask_path.stem.split('_', 1)[1] if '_' in ask_path.stem else ask_path.stem

    # Build .md content
    meta = {
        'created': created,
        'name': name,
        'why': reason,
    }
    yaml_text = yaml.dump(meta, allow_unicode=True, sort_keys=False)

    body_parts = [
        f'**Ask**: {name}',
        '',
        '# User Answer #',
        '',
        answer,
        '',
        '# Agent Question History #',
        '',
        question,
    ]

    content = f'---\n{yaml_text}---\n\n' + '\n'.join(body_parts)

    # Write .md file
    md_path = ask_path.with_suffix('.md')
    md_path.write_text(content, encoding='utf-8')

    ask_path.unlink()

    return md_path
