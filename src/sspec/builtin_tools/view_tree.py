"""Project directory tree visualization tool."""

from __future__ import annotations

from pathlib import Path

__all__ = [
    'TOOL_NAME',
    'TOOL_DESCRIPTION',
    'TOOL_PROMPT',
    'register_command',
]

TOOL_NAME = 'view-tree'
TOOL_DESCRIPTION = 'Visualize project directory structure'

# Always skip these directory NAMES regardless of .gitignore
# These are universally unwanted in tree views
ALWAYS_SKIP_NAMES = {
    '.git',
    '__pycache__',
    'node_modules',
    '.pytest_cache',
    '.mypy_cache',
}

# Additional skip directory names when no .gitignore / pathspec is available
FALLBACK_SKIP_NAMES = ALWAYS_SKIP_NAMES | {
    '.ruff_cache',
    '.venv',
    'venv',
    '.env',
    'dist',
    '.tox',
    '.eggs',
    '*.egg-info',
}


# ============================================================================
# Find project root for gitignore
# ============================================================================


def _find_project_root(start: Path) -> Path | None:
    """Walk up from `start` to find the nearest directory containing .gitignore or .sspec/.

    Returns the project root path (resolved), or None.
    """
    current = start.resolve()
    for _ in range(100):  # safety limit
        if (current / '.gitignore').exists() or (current / '.sspec').is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


# ============================================================================
# Gitignore Integration
# ============================================================================


class TreeGitignoreFilter:
    """Filter paths based on .gitignore rules for tree display.

    `gitignore_root` is the directory from which .gitignore files are loaded
    (typically the project root). This can differ from the directory being
    viewed — e.g. the user views ``src/`` but gitignore is at project root.

    All paths passed to should_ignore* methods MUST be resolved (absolute).
    """

    def __init__(self, gitignore_root: Path):
        self.root = gitignore_root.resolve()
        self._parser = None
        self._has_parser = False

        try:
            from sspec.builtin_tools.pack_zip import GitignoreParser

            self._parser = GitignoreParser(self.root)
            self._has_parser = True
        except ImportError:
            pass

    # ------------------------------------------------------------------

    def _is_under_root(self, path: Path) -> bool:
        """Check whether *path* lives under our gitignore root."""
        try:
            path.relative_to(self.root)
            return True
        except ValueError:
            return False

    # ------------------------------------------------------------------

    def should_ignore(self, path: Path) -> bool:
        """Decide whether *path* (resolved) should be hidden in the tree."""
        name = path.name

        # 1) Universal name-based filter (always applied)
        if name in ALWAYS_SKIP_NAMES:
            return True

        # 2) Gitignore rules — only when path is under the gitignore root
        if self._has_parser and self._parser is not None and self._is_under_root(path):
            return self._parser.should_ignore(path)

        # 3) Fallback name-based filter (no pathspec available)
        if not self._has_parser and path.is_dir() and name in FALLBACK_SKIP_NAMES:
            return True

        return False

    def should_ignore_dir(self, dir_path: Path) -> bool:
        """Convenience alias — semantically the same as should_ignore for dirs."""
        return self.should_ignore(dir_path)


# ============================================================================
# File Stats
# ============================================================================


def count_file_stats(file_path: Path) -> tuple[int, int]:
    """Count lines and characters in a text file.

    Returns (line_count, char_count) or (0, 0) if file cannot be read as text.
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.count('\n') + (1 if content and not content.endswith('\n') else 0)
        chars = len(content)
        return lines, chars
    except Exception:
        return 0, 0


def format_size(size: float) -> str:
    """Format byte size to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f'{size:.1f}{unit}'
        size /= 1024
    return f'{size:.1f}TB'


# ============================================================================
# Tree Builder
# ============================================================================


def _make_file_label(item: Path, show_size: bool, show_detail: bool) -> str:
    """Build the display label for a file node."""
    label = item.name

    if show_detail:
        lines, chars = count_file_stats(item)
        if lines > 0:
            label += f' [dim]({lines} lines, {chars} chars)[/dim]'
        else:
            try:
                size = item.stat().st_size
                label += f' [dim]({format_size(size)})[/dim]'
            except Exception:
                pass
    elif show_size:
        try:
            size = item.stat().st_size
            label += f' [dim]({format_size(size)})[/dim]'
        except Exception:
            pass

    return label


def build_tree(
    root: Path,
    *,
    max_depth: int | None = None,
    dirs_only: bool = False,
    show_size: bool = False,
    show_detail: bool = False,
    no_gitignore: bool = False,
    gitignore_root: Path | None = None,
    # -- internal recursion state --
    _current_depth: int = 0,
    _filter: TreeGitignoreFilter | None = None,
):
    """Build a Rich ``Tree`` representing the directory structure of *root*.

    Parameters
    ----------
    root:
        Directory to display.
    gitignore_root:
        Project root used for loading ``.gitignore`` files. If ``None``,
        the function tries ``_find_project_root(root)`` and falls back to
        *root* itself.
    """
    from rich.tree import Tree

    # Resolve to absolute — critical for gitignore path matching
    root = root.resolve()

    # Create the filter **once** at top-level
    if _filter is None and not no_gitignore:
        effective_root = (gitignore_root or _find_project_root(root) or root).resolve()
        _filter = TreeGitignoreFilter(effective_root)

    tree = Tree(f'[bold cyan]{root.name}/[/bold cyan]')

    # Collect & sort: directories first, then files, case-insensitive
    try:
        items = sorted(root.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        tree.add('[dim]Permission denied[/dim]')
        return tree

    for item in items:
        item_abs = item.resolve()

        # -- filter -------------------------------------------------------
        if _filter is not None:
            if item_abs.is_dir() and _filter.should_ignore_dir(item_abs):
                continue
            elif item_abs.is_file() and _filter.should_ignore(item_abs):
                continue

        # -- depth limit --------------------------------------------------
        if max_depth is not None and _current_depth >= max_depth:
            continue

        # -- directory ----------------------------------------------------
        if item_abs.is_dir():
            if max_depth is None or _current_depth < max_depth - 1:
                subtree = build_tree(
                    item_abs,
                    max_depth=max_depth,
                    dirs_only=dirs_only,
                    show_size=show_size,
                    show_detail=show_detail,
                    no_gitignore=no_gitignore,
                    _current_depth=_current_depth + 1,
                    _filter=_filter,
                )
                tree.add(subtree)
            else:
                tree.add(f'[bold blue]{item.name}/[/bold blue]')

        # -- file ---------------------------------------------------------
        elif not dirs_only:
            label = _make_file_label(item_abs, show_size, show_detail)
            tree.add(label)

    return tree


def collect_stats(
    root: Path,
    no_gitignore: bool,
    gitignore_root: Path | None = None,
) -> tuple[int, int, int]:
    """Collect file/directory count and total size under *root*.

    Returns ``(file_count, dir_count, total_size)``.
    """
    root = root.resolve()
    _filter: TreeGitignoreFilter | None = None
    if not no_gitignore:
        effective_root = (gitignore_root or _find_project_root(root) or root).resolve()
        _filter = TreeGitignoreFilter(effective_root)

    file_count = 0
    dir_count = 0
    total_size = 0

    for item in root.rglob('*'):
        item_abs = item.resolve()
        if _filter is not None and _filter.should_ignore(item_abs):
            continue

        if item_abs.is_file():
            file_count += 1
            try:
                total_size += item_abs.stat().st_size
            except Exception:
                pass
        elif item_abs.is_dir():
            dir_count += 1

    return file_count, dir_count, total_size


# ============================================================================
# Tool Prompt
# ============================================================================

TOOL_PROMPT = """# view-tree - Directory Tree Visualization

## Purpose
Display project directory structure in tree format.

## Usage

### Basic
```bash
# View current directory (project root)
sspec tool view-tree

# View specific subdirectory
sspec tool view-tree src/

# Limit depth
sspec tool view-tree -d 2
```

### Options
```bash
-d, --depth INTEGER    Maximum depth (default: unlimited)
--no-gitignore        Don't filter gitignored files
--dirs-only           Show only directories
--show-size           Display file sizes
--detail              Show detailed file info (lines, chars)
-o, --output PATH     Save to file (text or markdown)
--format [text|md]    Output format (default: text)
--prompt             Show this help message
```

### Detail Mode
With `--detail`, text files show line and character counts:
```
src/
├── core.py (317 lines, 8456 chars)
├── cli.py (38 lines, 892 chars)
└── README.md (284 lines, 6372 chars)
```

### Gitignore Support
- Reads `.gitignore` from **project root** (auto-detected), not just the viewed directory
- So `sspec tool view-tree src/` still respects the project root's .gitignore
- Uses `pathspec` library for accurate matching (via pack-zip module)
- Always filters: `.git/`, `__pycache__/`, `node_modules/`
- Fallback filters (no pathspec): `.venv/`, `.ruff_cache/`, `dist/`, etc.
- Use `--no-gitignore` to show everything

## Examples

```bash
sspec tool view-tree -d 3             # Quick overview
sspec tool view-tree --detail         # Detailed with line counts
sspec tool view-tree -o tree.md --format md   # Save to markdown
sspec tool view-tree --no-gitignore   # Show all files
```

## Notes
- Large projects may take time to scan with --detail
- Stats at bottom also respect gitignore filtering
"""


# ============================================================================
# CLI Registration
# ============================================================================


def register_command(group):
    """Register view-tree command to the tool group."""
    import click
    from rich.console import Console

    from sspec.core import find_sspec_root

    console = Console()

    @group.command(name=TOOL_NAME, help=TOOL_DESCRIPTION)
    @click.argument(
        'path',
        type=click.Path(exists=True, file_okay=False, path_type=Path),
        required=False,
    )
    @click.option('-d', '--depth', type=int, help='Maximum depth')
    @click.option('--no-gitignore', is_flag=True, help="Don't filter gitignored files")
    @click.option('--dirs-only', is_flag=True, help='Show only directories')
    @click.option('--show-size', is_flag=True, help='Display file sizes')
    @click.option('--detail', is_flag=True, help='Show detailed file info (lines, chars)')
    @click.option('-o', '--output', type=click.Path(path_type=Path), help='Save to file')
    @click.option(
        '--format',
        'output_format',
        type=click.Choice(['text', 'md']),
        default='text',
        help='Output format',
    )
    @click.option('--prompt', 'show_prompt', is_flag=True, help='Show tool usage guide')
    def view_tree_command(
        path: Path | None,
        depth: int | None,
        no_gitignore: bool,
        dirs_only: bool,
        show_size: bool,
        detail: bool,
        output: Path | None,
        output_format: str,
        show_prompt: bool,
    ):
        """Visualize project directory structure."""

        if show_prompt:
            console.print(TOOL_PROMPT)
            return

        # -- resolve target path & gitignore root -------------------------
        sspec_root = find_sspec_root()
        project_root = sspec_root.parent if sspec_root else None

        if path is None:
            path = project_root or Path.cwd()

        # gitignore_root: always use project root so subdir views still
        # respect the project-level .gitignore
        gitignore_root = project_root

        # -- build tree ----------------------------------------------------
        tree = build_tree(
            path,
            max_depth=depth,
            dirs_only=dirs_only,
            show_size=show_size,
            show_detail=detail,
            no_gitignore=no_gitignore,
            gitignore_root=gitignore_root,
        )

        # -- statistics ----------------------------------------------------
        file_count, dir_count, total_size = collect_stats(
            path, no_gitignore, gitignore_root=gitignore_root,
        )
        stats_line = (
            f'Files: {file_count} | Directories: {dir_count}'
            f' | Total size: {format_size(total_size)}'
        )

        # -- output --------------------------------------------------------
        if output:
            from rich.console import Console as RichConsole

            with open(output, 'w', encoding='utf-8') as f:
                text_console = RichConsole(file=f, width=120)
                if output_format == 'md':
                    text_console.print(f'# Directory Structure: {path.name}\n')
                text_console.print(tree)
                text_console.print(f'\n{stats_line}')

            console.print(f'[green]✓[/green] Saved to: {output}')
        else:
            console.print(tree)
            console.print()
            console.print(stats_line)
