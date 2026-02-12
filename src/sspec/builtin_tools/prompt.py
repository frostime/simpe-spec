"""Interactive prompt editor with file path completion and command mode.

Design goal: a clean, "Vim-like" TUI where the editor and command line are
separate fixed regions (no awkward newline + input for command mode).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from prompt_toolkit import PromptSession
from prompt_toolkit.application import Application
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.filters import Condition, has_focus
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    Float,
    FloatContainer,
    Window,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.widgets import Frame, TextArea

__all__ = ['TOOL_NAME', 'TOOL_DESCRIPTION', 'TOOL_PROMPT', 'register_command']

TOOL_NAME = 'prompt'
TOOL_DESCRIPTION = 'Interactive command editor with file path completion'


# ============================================================================
# Editor State
# ============================================================================


@dataclass
class EditorState:
    """Mutable state shared between the editing loop and key bindings."""

    output_path: Path | None = None
    in_command_mode: bool = False
    status: str = ''


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

    def get_completions(self, document: Document, complete_event) -> Iterable[Completion]:
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
            yield Completion(path_str, start_position=-len(query), display=path_str)


# ============================================================================
# Command Processing
# ============================================================================


def _process_command(raw: str, state: EditorState) -> tuple[bool, str | None]:
    """Process a ``/command`` string.

    Returns (should_exit, editor_op).

    This function updates ``state`` (status/output_path) instead of printing,
    so it can be used inside a full-screen prompt_toolkit Application.
    """
    cmd = raw.strip()
    if cmd.startswith('/'):
        cmd = cmd[1:]
    if not cmd:
        state.status = 'No command'
        return False, None

    parts = cmd.split(None, 1)
    action = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ''

    if action in ('exit', 'quit', 'q'):
        state.status = 'Exit'
        return True, None

    elif action == 'clear':
        state.status = '✓ Buffer cleared'
        return False, 'clear'

    elif action == 'output':
        if arg:
            state.output_path = Path(arg)
            state.status = f'✓ Output → {arg}'
        else:
            if state.output_path:
                state.status = f'Current output: {state.output_path}'
            else:
                state.status = 'No output path set. Usage: /output <path>'

    elif action == 'help':
        state.status = 'Commands: /exit /clear /output <path> /help'

    else:
        state.status = f'Unknown command: /{action} (type /help)'

    return False, None


# ==========================================================================
# Full-screen TUI
# ==========================================================================


def _build_status_bar(state: EditorState) -> AnyFormattedText:
    """Build a safe status bar.

    IMPORTANT: Do not use HTML() here.
    Status text may contain characters like `<path>` which would be interpreted
    as markup and crash the renderer.
    """

    def sep() -> list[tuple[str, str]]:
        return [('', ' │ ')]

    fragments: list[tuple[str, str]] = []

    fragments += [('bold', 'Esc'), ('', ' cmd')]
    fragments += sep() + [('bold', 'Esc+Enter'), ('', ' submit')]
    fragments += sep() + [('bold', '@'), ('', ' files')]
    fragments += sep() + [('bold', '/help'), ('', ' cmds')]

    if state.output_path:
        fragments += sep() + [('', 'Output: '), ('bold', str(state.output_path))]

    if state.status:
        fragments += sep() + [('bold', state.status)]

    return cast(AnyFormattedText, fragments)


def _run_fullscreen_editor(
    root_dir: Path, *, state: EditorState, initial_text: str
) -> tuple[str, Path | None]:
    """Run a clean full-screen editor with a fixed bottom command line."""

    completer = FilePathCompleter(root_dir)

    editor = TextArea(
        text=initial_text,
        multiline=True,
        wrap_lines=False,
        completer=completer,
        complete_while_typing=True,
        scrollbar=True,
    )

    command_line = TextArea(
        text='', multiline=False, height=1, prompt=':', wrap_lines=False
    )

    @Condition
    def _is_command_mode() -> bool:
        return state.in_command_mode

    editor_focused = has_focus(editor)

    status_window = Window(
        content=FormattedTextControl(lambda: _build_status_bar(state)),
        height=1,
        style='class:status',
    )

    # A custom Application+Layout does NOT auto-include a completions
    # popup (unlike PromptSession which adds one by default).
    # Without this Float, the completer generates results but there is
    # no widget to render the dropdown — Tab falls back to inline-
    # completing the first match with no visible list to choose from.
    editor_with_completions = FloatContainer(
        content=Frame(editor, title='prompt'),
        floats=[
            Float(
                xcursor=True,
                ycursor=True,
                content=CompletionsMenu(max_height=12, scroll_offset=1),
            ),
        ],
    )

    root_container = HSplit(
        [
            editor_with_completions,
            ConditionalContainer(
                content=Frame(command_line, title='command'), filter=_is_command_mode
            ),
            status_window,
        ]
    )

    kb = KeyBindings()

    @kb.add('escape')
    def _enter_command_mode(event):
        """Esc (alone, after timeout) enters command mode (like Vim ':')."""
        state.in_command_mode = True
        state.status = ''
        command_line.text = ''
        event.app.layout.focus(command_line)

    @kb.add('enter', filter=editor_focused & ~_is_command_mode)
    def _insert_newline_no_indent(event):
        """Insert a literal newline without auto-indentation.

        This keeps pasted multi-line text stable (no cumulative indentation).
        """
        event.app.current_buffer.insert_text('\n')

    @kb.add('escape', 'enter')
    def _submit(event):
        """Esc+Enter submits the editor content."""
        if state.in_command_mode:
            return
        event.app.exit(result=editor.text)

    @kb.add('c-c')
    def _cancel(event):
        raise KeyboardInterrupt

    @kb.add('enter', filter=_is_command_mode)
    def _run_command(event):
        raw = command_line.text
        should_exit, editor_op = _process_command(raw, state)
        if editor_op == 'clear':
            editor.text = ''
        if should_exit:
            event.app.exit(result=editor.text)
            return

        state.in_command_mode = False
        event.app.layout.focus(editor)

    @kb.add('escape', filter=_is_command_mode)
    def _cancel_command_mode(event):
        state.in_command_mode = False
        state.status = ''
        event.app.layout.focus(editor)

    app = Application(
        layout=Layout(root_container, focused_element=editor),
        key_bindings=kb,
        full_screen=True,
        mouse_support=True,
    )

    app.timeoutlen = 0.1

    result_text = app.run()
    return result_text, state.output_path


# ============================================================================
# Interactive Editor
# ============================================================================


def run_interactive_editor(
    root_dir: Path, single_line: bool = False, initial_output: Path | None = None
) -> tuple[str, Path | None]:
    """Run the interactive editor and return ``(text, output_path)``.

    The output_path may be set dynamically via the ``/output`` command
    during editing.
    """
    if single_line:
        session: PromptSession = PromptSession()
        text = session.prompt('')
        return text, initial_output

    state = EditorState(output_path=initial_output)
    try:
        return _run_fullscreen_editor(root_dir, state=state, initial_text='')
    except KeyboardInterrupt:
        raise


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
Press **Esc** (alone) to open the bottom command line (Vim-like),
then type a command and press Enter:

| Command | Description |
|---------|-------------|
| `/exit` | Finish editing and output text |
| `/clear` | Clear the editing buffer |
| `/output <path>` | Set/change output file path |
| `/help` | Show available commands |

### Keybindings
- **Esc + Enter**: Submit editor content
- **Esc** (alone): Open command line
- **Enter** (in command line): Run command
- **Ctrl+C**: Cancel

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
- The Esc key may have a brief delay (terminal escape sequence timeout)
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
        '-o',
        '--output',
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
    @click.option('--prompt', 'show_prompt', is_flag=True, help='Show tool usage guide')
    def prompt_command(
        output: Path | None, root: Path | None, single_line: bool, show_prompt: bool
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
                root_dir=root, single_line=single_line, initial_output=output
            )
        except KeyboardInterrupt:
            console.print('[yellow]\nCancelled.[/yellow]')
            raise click.Abort() from None

        # Dynamic /output command overrides -o flag
        final_output = dynamic_output or output

        if final_output:
            final_output.parent.mkdir(parents=True, exist_ok=True)
            final_output.write_text(text, encoding='utf-8')
            console.print(f'[green]✓[/green] Saved to: {final_output}')
        else:
            print(text)
