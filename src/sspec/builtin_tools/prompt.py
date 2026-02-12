"""Interactive prompt editor with file path completion and command mode."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

__all__ = [
    'TOOL_NAME',
    'TOOL_DESCRIPTION',
    'TOOL_PROMPT',
    'register_command',
]

TOOL_NAME = 'prompt'
TOOL_DESCRIPTION = 'Interactive command editor with file path completion'


# ============================================================================
# Editor State
# ============================================================================


@dataclass
class EditorState:
    """Mutable state shared between the editing loop and key bindings."""

    output_path: Path | None = None
    enter_command_mode: bool = False
    pending_text: str = ''


# ============================================================================
# File Path Completer
# ============================================================================


class FilePathCompleter(Completer):
    """Completer that triggers on ``@`` symbol for fuzzy file path matching."""

    def __init__(self, root_dir: Path, max_results: int = 50):
        self.root_dir = root_dir.resolve()
        self.max_results = max_results
        self._file_cache: list[Path] = []
        self._cache_populated = False

    def _populate_cache(self) -> None:
        """Lazy-load file list into cache."""
        if self._cache_populated:
            return

        try:
            self._file_cache = []
            for item in self.root_dir.rglob('*'):
                if item.is_file() and not self._should_skip(item):
                    self._file_cache.append(item)
            self._cache_populated = True
        except Exception:
            self._file_cache = []
            self._cache_populated = True

    def _should_skip(self, path: Path) -> bool:
        """Quick filter for common unwanted files."""
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.sspec'}
        if any(part in skip_dirs for part in path.parts):
            return True

        skip_exts = {'.pyc', '.pyo', '.so', '.dylib', '.dll'}
        if path.suffix in skip_exts:
            return True

        return False

    def _fuzzy_match(self, query: str) -> list[Path]:
        """Substring search sorted by match position (earlier = better)."""
        query_lower = query.lower()
        matches: list[tuple[int, Path]] = []

        for path in self._file_cache:
            try:
                rel_path = path.relative_to(self.root_dir)
                path_str = str(rel_path).replace('\\', '/').lower()

                if query_lower in path_str:
                    score = path_str.index(query_lower)
                    matches.append((score, rel_path))
            except ValueError:
                continue

        matches.sort(key=lambda x: x[0])
        return [path for _, path in matches[: self.max_results]]

    def get_completions(
        self, document: Document, complete_event
    ) -> Iterable[Completion]:
        """Generate completions when ``@`` is detected on the current line."""
        # Use CURRENT LINE only — prevents cross-line false matches
        text = document.current_line_before_cursor

        # Find the last @ symbol on the current line
        at_pos = text.rfind('@')
        if at_pos == -1:
            return

        # Extract query after @
        query = text[at_pos + 1 :]

        # Skip if query contains spaces (not a file path)
        if ' ' in query:
            return

        # Populate cache on first use
        self._populate_cache()

        # Find matches
        if not query:
            matches = self._file_cache[: self.max_results]
            # Show relative paths
            rel_matches = []
            for m in matches:
                try:
                    rel_matches.append(m.relative_to(self.root_dir))
                except ValueError:
                    pass
            matches = rel_matches
        else:
            matches = self._fuzzy_match(query)

        # Generate completions
        for match in matches:
            path_str = str(match).replace('\\', '/')
            yield Completion(
                path_str,
                start_position=-len(query),
                display=path_str,
            )


# ============================================================================
# Command Processing
# ============================================================================


# ANSI helpers (stderr output)
_YELLOW = '\x1b[33m'
_GREEN = '\x1b[32m'
_RED = '\x1b[31m'
_DIM = '\x1b[2m'
_RESET = '\x1b[0m'


def _process_command(raw: str, state: EditorState) -> bool:
    """Process a ``/command`` string.  Returns True to signal exit."""
    cmd = raw.strip().lstrip('/')
    if not cmd:
        return False

    parts = cmd.split(None, 1)
    action = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ''

    if action in ('exit', 'quit', 'q'):
        return True

    elif action == 'clear':
        state.pending_text = ''
        print(f'{_GREEN}✓ Buffer cleared{_RESET}', file=sys.stderr)

    elif action == 'output':
        if arg:
            state.output_path = Path(arg)
            print(f'{_GREEN}✓ Output → {arg}{_RESET}', file=sys.stderr)
        else:
            if state.output_path:
                print(f'Current output: {state.output_path}', file=sys.stderr)
            else:
                print(f'{_DIM}No output path set. Usage: /output <path>{_RESET}', file=sys.stderr)

    elif action == 'help':
        print(f'{_YELLOW}Commands:{_RESET}', file=sys.stderr)
        print(f'  /exit            Finish editing and output text', file=sys.stderr)
        print(f'  /clear           Clear the buffer', file=sys.stderr)
        print(f'  /output <path>   Set output file path', file=sys.stderr)
        print(f'  /help            Show this help', file=sys.stderr)

    else:
        print(f'{_RED}Unknown command: /{action}{_RESET}', file=sys.stderr)
        print(f'{_DIM}Type /help for available commands{_RESET}', file=sys.stderr)

    return False


# ============================================================================
# Key Bindings
# ============================================================================


def _build_key_bindings(state: EditorState) -> KeyBindings:
    """Create key bindings with Esc → command-mode support."""
    kb = KeyBindings()

    @kb.add('escape')
    def _enter_command_mode(event):
        """Esc (alone, after timeout) → enter command mode.

        Esc+Enter (Meta+Enter) is handled separately by prompt_toolkit's
        default multiline bindings and is NOT affected.
        """
        state.enter_command_mode = True
        state.pending_text = event.app.current_buffer.text
        event.app.exit(result=None)

    return kb


def _build_toolbar(state: EditorState):
    """Bottom toolbar showing hints and current output path."""
    parts = [
        '<b>Esc</b> /cmd',
        '<b>Esc+Enter</b> submit',
        '<b>@</b> files',
    ]
    if state.output_path:
        parts.append(f'Output: <b>{state.output_path}</b>')
    return HTML(' │ '.join(parts))


# ============================================================================
# Interactive Editor
# ============================================================================


def run_interactive_editor(
    root_dir: Path,
    single_line: bool = False,
    initial_output: Path | None = None,
) -> tuple[str, Path | None]:
    """Run the interactive editor and return ``(text, output_path)``.

    The output_path may be set dynamically via the ``/output`` command
    during editing.
    """
    if single_line:
        session: PromptSession = PromptSession()
        text = session.prompt('> ')
        return text, initial_output

    state = EditorState(output_path=initial_output)
    completer = FilePathCompleter(root_dir)
    buffer_text = ''

    # Show banner once
    print(f'{_YELLOW}=== Interactive Editor ==={_RESET}', file=sys.stderr)
    print(f'  @       file path completion', file=sys.stderr)
    print(f'  Esc     command mode (/exit, /clear, /output, /help)', file=sys.stderr)
    print(f'  Esc+Enter  finish editing', file=sys.stderr)
    print(file=sys.stderr)

    while True:
        state.enter_command_mode = False
        kb = _build_key_bindings(state)

        session = PromptSession(
            completer=completer,
            multiline=True,
            complete_while_typing=True,
            key_bindings=kb,
            bottom_toolbar=lambda: _build_toolbar(state),
        )

        try:
            result = session.prompt('> ', default=buffer_text, multiline=True)
        except KeyboardInterrupt:
            raise
        except EOFError:
            # Ctrl+D on empty buffer → finish with current text
            return buffer_text, state.output_path

        # -- Esc was pressed (result is None) → command mode ----------------
        if result is None and state.enter_command_mode:
            buffer_text = state.pending_text

            # Show command prompt (regular input, outside prompt_toolkit)
            try:
                print(file=sys.stderr)
                raw = input(f'{_YELLOW}/ {_RESET}')
            except (EOFError, KeyboardInterrupt):
                # Cancel command mode → resume editing
                continue

            should_exit = _process_command(raw, state)
            if should_exit:
                return buffer_text, state.output_path

            # /clear may have reset pending_text
            buffer_text = state.pending_text
            print(file=sys.stderr)
            continue

        # -- Normal submit (Esc+Enter or Ctrl+D on non-empty) ---------------
        if result is not None:
            return result, state.output_path

        # Defensive fallback
        return buffer_text, state.output_path


# ============================================================================
# Tool Prompt
# ============================================================================

TOOL_PROMPT = """# prompt - Interactive Command Editor

## Purpose
Edit multi-line text with file path auto-completion and command mode.

## Usage

### Basic
```bash
# Output to stdout
sspec tool prompt

# Save to file
sspec tool prompt -o instruction.md
```

### File Path Completion
Type `@` to trigger file path completion:
- `@src` → shows files matching "src"
- `@util` → fuzzy matches files containing "util"
- Use arrow keys to navigate, Tab/Enter to confirm

### Command Mode
Press **Esc** (alone) to enter command mode, then type a command:

| Command | Description |
|---------|-------------|
| `/exit` | Finish editing and output text |
| `/clear` | Clear the editing buffer |
| `/output <path>` | Set/change output file path |
| `/help` | Show available commands |

### Keybindings
- **Esc + Enter**: Finish editing and output (submit)
- **Esc** (alone): Enter command mode
- **Ctrl+C**: Cancel
- **Ctrl+D**: EOF (finish on empty buffer)

### Options
```bash
--output, -o PATH   Save to file (default: stdout)
--root PATH         Project root for file completion
--single-line       Single-line mode (no @ completion, no commands)
--prompt           Show this help message
```

## Examples

### Write instruction for AI
```bash
sspec tool prompt -o .sspec/asks/new-feature.md
# Type: Please implement @src/auth.py with ...
# Press Esc+Enter to save
```

### Dynamic output
```bash
sspec tool prompt
# Type some text...
# Press Esc → /output notes.md
# Continue typing...
# Press Esc+Enter to save to notes.md
```

## Notes
- File paths are relative to project root
- Completion skips .git, __pycache__, node_modules, .sspec
- Works best in terminals with UTF-8 support
- The Esc key has a brief delay (terminal escape sequence timeout)
"""


# ============================================================================
# CLI Registration
# ============================================================================


def register_command(group):
    """Register prompt command to the tool group."""
    import click
    from rich.console import Console

    from sspec.core import find_sspec_root

    console = Console()

    @group.command(name=TOOL_NAME, help=TOOL_DESCRIPTION)
    @click.option(
        '-o', '--output',
        type=click.Path(path_type=Path),
        help='Save to file (default: stdout)',
    )
    @click.option(
        '--root',
        type=click.Path(exists=True, file_okay=False, path_type=Path),
        help='Project root directory (default: current sspec project or cwd)',
    )
    @click.option(
        '--single-line',
        is_flag=True,
        help='Single-line mode (no file completion, no commands)',
    )
    @click.option(
        '--prompt',
        'show_prompt',
        is_flag=True,
        help='Show tool usage guide',
    )
    def prompt_command(
        output: Path | None,
        root: Path | None,
        single_line: bool,
        show_prompt: bool,
    ):
        """Interactive command editor with file path completion."""

        if show_prompt:
            console.print(TOOL_PROMPT)
            return

        # Determine root directory
        if root is None:
            sspec_root = find_sspec_root()
            if sspec_root:
                root = sspec_root.parent
            else:
                root = Path.cwd()

        # Run editor
        try:
            text, dynamic_output = run_interactive_editor(
                root_dir=root,
                single_line=single_line,
                initial_output=output,
            )
        except KeyboardInterrupt:
            console.print('[yellow]\nCancelled.[/yellow]')
            raise click.Abort()

        # Dynamic /output command overrides -o flag
        final_output = dynamic_output or output

        if final_output:
            final_output.parent.mkdir(parents=True, exist_ok=True)
            final_output.write_text(text, encoding='utf-8')
            console.print(f'[green]✓[/green] Saved to: {final_output}')
        else:
            print(text)
