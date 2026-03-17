"""File writing helper for agent-friendly create/append/overwrite flows."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import click

__all__ = [
    'TOOL_NAME',
    'TOOL_DESCRIPTION',
    'TOOL_PROMPT',
    'register_command',
]

TOOL_NAME = 'write'
TOOL_DESCRIPTION = 'Write file content from pipe or text argument'

TOOL_PROMPT = """
# write - Explicit File Writing Helper

## Purpose

Write full file content with explicit modes:
- `create` - create a new file, fail if it already exists
- `append` - append to an existing file, fail if it does not exist
- `overwrite` - replace an existing file, fail if it does not exist

Works in any directory. It does not require an `.sspec/` project.
Both relative and absolute paths are supported.

## Input Modes

Use exactly one of:
- `--stdin` - recommended for multi-line content
- `--text` - short inline text only

### Recommended: pipe multi-line content

```bash
cat <<'EOF' | sspec tool write notes.md --mode create --stdin
line 1
line 2
EOF
```

```powershell
@'
line 1
line 2
'@ | sspec tool write notes.md --mode create --stdin
```

### Short inline text

```bash
sspec tool write note.txt --mode overwrite --text "hello"
```

## Notes

- For multi-line or quote-heavy content, prefer `--stdin`
- `--text` depends on shell escaping rules and is best for short content
- Existing files keep their current newline style during `append` and `overwrite`
- Use `--parents` to create missing parent directories
""".strip()


def _resolve_target_path(target: Path) -> Path:
    """Resolve relative and absolute target paths without requiring sspec."""
    target = target.expanduser()
    if target.is_absolute():
        return target.resolve(strict=False)
    return (Path.cwd() / target).resolve(strict=False)


def _detect_newline_style(text: str) -> str:
    """Detect the dominant newline style in a text blob."""
    if '\r\n' in text:
        return '\r\n'
    if '\r' in text:
        return '\r'
    return '\n'


def _convert_newlines(text: str, newline: str) -> str:
    """Normalize newline sequences to the requested style."""
    normalized = text.replace('\r\n', '\n').replace('\r', '\n')
    return normalized.replace('\n', newline)


def _read_existing_newline_style(path: Path, encoding: str) -> str | None:
    """Read newline style from an existing text file."""
    if not path.exists() or not path.is_file():
        return None

    with path.open('r', encoding=encoding, newline='') as handle:
        text = handle.read()

    if not text:
        return None
    return _detect_newline_style(text)


def _atomic_write_text(path: Path, text: str, encoding: str) -> None:
    """Write a file atomically within the same directory."""
    original_mode = None
    try:
        original_mode = path.stat().st_mode
    except OSError:
        original_mode = None

    fd, temp_path = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w', encoding=encoding, newline='') as handle:
            handle.write(text)
        if original_mode is not None:
            try:
                os.chmod(temp_path, original_mode)
            except OSError:
                pass
        os.replace(temp_path, path)
    except Exception:
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise


def _load_input(*, use_stdin: bool, text: str | None, encoding: str) -> str:
    """Load content from stdin or a direct text argument."""
    if use_stdin:
        if sys.stdin.isatty():
            raise ValueError('No piped input detected. Use a pipe with --stdin or pass --text.')
        raw = sys.stdin.buffer.read()
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError as exc:
            raise ValueError(f'Failed to decode stdin as {encoding}: {exc}') from exc

    assert text is not None
    return text


def _prepare_content(content: str, target: Path, mode: str, encoding: str) -> str:
    """Convert incoming content to the target file newline style when possible."""
    if mode not in {'append', 'overwrite'} or not target.exists():
        return content

    newline = _read_existing_newline_style(target, encoding)
    if not newline:
        return content
    return _convert_newlines(content, newline)


def _line_count(text: str) -> int:
    """Return a stable line count for status output."""
    if not text:
        return 0
    return len(text.splitlines()) or 1


def register_command(group: click.Group) -> None:
    """Register write as a Click subcommand."""
    import click

    @group.command(name=TOOL_NAME, help=TOOL_DESCRIPTION)
    @click.argument('target', type=click.Path(path_type=Path), required=False)
    @click.option(
        '--mode',
        type=click.Choice(['append', 'create', 'overwrite']),
        help='Writing mode.',
    )
    @click.option('--stdin', 'use_stdin', is_flag=True, help='Read content from piped stdin.')
    @click.option('--text', help='Inline text content for short writes.')
    @click.option('--encoding', default='utf-8', show_default=True, help='Text encoding to use.')
    @click.option('--parents', is_flag=True, help='Create missing parent directories.')
    @click.option(
        '--prompt',
        'show_prompt',
        is_flag=True,
        help='Show agent-oriented usage guidance.',
    )
    def write_command(
        target: Path | None,
        mode: str | None,
        use_stdin: bool,
        text: str | None,
        encoding: str,
        parents: bool,
        show_prompt: bool,
    ) -> None:
        """Write file content with explicit create/append/overwrite semantics."""
        if show_prompt:
            click.echo(TOOL_PROMPT)
            return

        if target is None:
            raise click.ClickException('Missing argument: TARGET')
        if mode is None:
            raise click.ClickException('Missing option: --mode')

        if use_stdin == (text is not None):
            raise click.ClickException('Use exactly one input source: --stdin or --text.')

        resolved = _resolve_target_path(target)
        parent = resolved.parent

        if parents:
            parent.mkdir(parents=True, exist_ok=True)
        elif not parent.exists():
            raise click.ClickException(f'Parent directory does not exist: {parent}')

        try:
            content = _load_input(use_stdin=use_stdin, text=text, encoding=encoding)
            content = _prepare_content(content, resolved, mode, encoding)
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc
        except OSError as exc:
            raise click.ClickException(str(exc)) from exc

        if mode == 'create':
            if resolved.exists():
                raise click.ClickException(f'File already exists: {resolved}')
            try:
                _atomic_write_text(resolved, content, encoding)
            except OSError as exc:
                raise click.ClickException(str(exc)) from exc
        elif mode == 'overwrite':
            if not resolved.exists():
                raise click.ClickException(f'File does not exist: {resolved}')
            if not resolved.is_file():
                raise click.ClickException(f'Not a file: {resolved}')
            try:
                _atomic_write_text(resolved, content, encoding)
            except OSError as exc:
                raise click.ClickException(str(exc)) from exc
        else:
            if not resolved.exists():
                raise click.ClickException(f'File does not exist: {resolved}')
            if not resolved.is_file():
                raise click.ClickException(f'Not a file: {resolved}')
            try:
                with resolved.open('a', encoding=encoding, newline='') as handle:
                    handle.write(content)
            except OSError as exc:
                raise click.ClickException(str(exc)) from exc

        click.echo(
            f'[OK] {mode} wrote {resolved} '
            f'({len(content)} chars, {_line_count(content)} lines, encoding={encoding})'
        )
