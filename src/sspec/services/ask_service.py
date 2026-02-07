from __future__ import annotations

import importlib.util
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
        raise ValueError(
            f'Invalid ask name: "{name}". ' 'Must contain at least one letter or number.'
        )

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
        f"\n{'='*60}\n  🤖 sspec ask\n{'='*60}\n\n{prompt}\n",
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
    print(f"\n✓ Received ({len(result)} chars)\n{'='*60}\n", file=output_stream)
    return result


def create_ask_template(sspec_root: Path, name: str) -> tuple[Path, str | None]:
    """
    Create a Python template file for sspec ask.

    Args:
        sspec_root: .sspec directory path
        name: Ask name (auto-converted to Python-safe identifier)

    Returns:
        Tuple of (Path to created .py file, warning message if name was converted)

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
    py_path = asks_dir / f'{base}.py'

    # Handle filename conflicts
    if py_path.exists():
        counter = 1
        while py_path.exists():
            py_path = asks_dir / f'{base}_{counter}.py'
            counter += 1

    template = f'''CREATED = "{timestamp}"

# EDIT: Why are you asking this question?
REASON = r"""
Ask user for <brief_reason>
"""

# EDIT: The question to ask
QUESTION = r"""
<YOUR_QUESTION_HERE>
"""

# ==========
# AGENT SHOULD NOT EDIT THIS SECTION!
# User can pre-fill answer here to skip terminal input during execution.
# If this field has content, it will be used directly without prompting.
USER_ANSWER = r""""""
'''

    py_path.write_text(template, encoding='utf-8')
    return py_path, warning


def execute_ask_prompt(ask_file_path: Path) -> str:
    """
    Execute an ask prompt by dynamically importing the Python file.

    Args:
        ask_file_path: Path to .py ask template file

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

    # Dynamically import the module
    spec = importlib.util.spec_from_file_location('ask_module', ask_file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f'Cannot load ask file: {ask_file_path}')

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Extract required attributes
    if not hasattr(module, 'REASON') or not hasattr(module, 'QUESTION'):
        raise AttributeError('Ask file must define REASON and QUESTION')

    reason = module.REASON.strip()
    question = module.QUESTION.strip()

    # Check if user pre-filled the answer
    if hasattr(module, 'USER_ANSWER'):
        user_answer = module.USER_ANSWER.strip()
        if user_answer:
            # User provided answer in file, use it directly
            return user_answer

    # No pre-filled answer, prompt user interactively
    prompt_text = f'**Why**: {reason}\n\n{question}'
    answer = collect_multiline_input(prompt=prompt_text)

    return answer


def save_ask_answer(ask_file_path: Path, answer: str) -> None:
    """
    Append ANSWER variable to the ask .py file.

    Args:
        ask_file_path: Path to .py ask file
        answer: User's answer to append
    """
    answer_block = f'\nANSWER = r"""\n{answer}\n"""\n'

    with ask_file_path.open('a', encoding='utf-8') as f:
        f.write(answer_block)


def convert_ask_to_md(py_path: Path) -> Path:
    """
    Convert ask .py file to .md format and delete the .py file.

    Args:
        py_path: Path to .py ask file (must have CREATED, REASON, QUESTION, ANSWER)

    Returns:
        Path to created .md file

    Raises:
        AttributeError: If required attributes missing
    """
    # Import and extract data
    spec = importlib.util.spec_from_file_location('ask_module', py_path)
    if spec is None or spec.loader is None:
        raise ImportError(f'Cannot load ask file: {py_path}')

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    required_attrs = ['CREATED', 'REASON', 'QUESTION', 'ANSWER']
    for attr in required_attrs:
        if not hasattr(module, attr):
            raise AttributeError(f'Ask file missing required attribute: {attr}')

    created = module.CREATED
    reason = module.REASON.strip()
    question = module.QUESTION.strip()
    answer = module.ANSWER.strip()

    # Extract name from filename (format: <timestamp>_<name>.py)
    name = py_path.stem.split('_', 1)[1] if '_' in py_path.stem else py_path.stem

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
    md_path = py_path.with_suffix('.md')
    md_path.write_text(content, encoding='utf-8')

    # Delete .py file
    py_path.unlink()

    return md_path
