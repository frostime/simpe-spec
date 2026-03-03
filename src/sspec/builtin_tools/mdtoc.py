"""Markdown Table of Contents (TOC) analyzer tool.

Outputs file metadata (chars, lines) and heading structure with 1-based line
numbers in L<n> format — optimized for Agent pre-scan before reading.
"""

from __future__ import annotations

import glob
from dataclasses import dataclass
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

TOOL_NAME = 'mdtoc'
TOOL_DESCRIPTION = 'Show Markdown TOC with line numbers for Agent pre-scan'

TOOL_PROMPT = """
# mdtoc — Markdown TOC Analyzer

## Purpose

Pre-scan Markdown files before reading. Outputs file size metadata and heading
structure with 1-based line numbers, so you can target specific sections with
read_file(startLine, endLine) instead of reading blindly.

## Usage

```
sspec tool mdtoc <source> [--depth N]
```

- `<source>`: file path | directory (globs all *.md) | glob pattern
- `--depth N`: limit heading depth (default: 6, shows all levels)

## Output Format

```
=== path/to/file.md ===
chars: 4523 | lines: 120

L1   # Title
L5     ## Section One
L12    ## Section Two
L18      ### Subsection
```

Each heading entry:
- `L<n>` — 1-based line number where the heading appears
- Indented by heading level (H1=0, H2=2spaces, H3=4spaces, ...)
- Heading text preserved as-is

## Typical Agent Workflow

1. Run `sspec tool mdtoc <file>` to get outline + line ranges
2. Identify sections of interest from TOC
3. Use `read_file(startLine=<Ln>, endLine=<next_Ln - 1>)` for targeted reads

## Multi-file Example

```
sspec tool mdtoc docs/          # All .md files in docs/
sspec tool mdtoc "**/*.md"      # Glob pattern
sspec tool mdtoc README.md      # Single file
```
""".strip()


# ============================================================================
# Core Logic
# ============================================================================


@dataclass
class Heading:
    """Represents a single Markdown heading."""

    level: int  # 1-6
    text: str  # stripped heading text (without leading #s)
    line_num: int  # 1-based line number


@dataclass
class FileToc:
    """TOC result for a single file."""

    path: Path
    char_count: int
    line_count: int
    headings: list[Heading]
    error: str | None = None


def _parse_headings(content: str, max_depth: int) -> list[Heading]:
    """Extract headings from Markdown content, skipping code fences."""
    headings: list[Heading] = []
    in_fence = False
    fence_char = ''

    for line_idx, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()

        # Track code fences (``` or ~~~)
        if stripped.startswith('```') or stripped.startswith('~~~'):
            fence_marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_char = fence_marker
            elif fence_marker == fence_char:
                in_fence = False
            continue

        if in_fence:
            continue

        # Match headings: must start at column 0, 1-6 # chars followed by space
        if not line.startswith('#'):
            continue

        level = 0
        for ch in line:
            if ch == '#':
                level += 1
            else:
                break

        if level > 6 or level > max_depth:
            continue

        # Text follows the # markers + optional space
        text = line[level:].lstrip()
        if not text:
            continue

        headings.append(Heading(level=level, text=text, line_num=line_idx))

    return headings


def _analyze_file(path: Path, max_depth: int) -> FileToc:
    """Analyze a single Markdown file."""
    try:
        content = path.read_text(encoding='utf-8', errors='replace')
    except OSError as e:
        return FileToc(path=path, char_count=0, line_count=0, headings=[], error=str(e))

    char_count = len(content)
    line_count = len(content.splitlines())
    headings = _parse_headings(content, max_depth)

    return FileToc(path=path, char_count=char_count, line_count=line_count, headings=headings)


def _resolve_sources(source: str) -> list[Path]:
    """Resolve source argument to a list of Markdown file paths."""
    p = Path(source)

    # Directory: glob all .md files recursively
    if p.is_dir():
        return sorted(p.rglob('*.md'))

    # Existing file
    if p.is_file():
        return [p]

    # Glob pattern
    matched = sorted(Path(f) for f in glob.glob(source, recursive=True) if Path(f).is_file())
    if matched:
        return matched

    return []


def _format_toc(toc: FileToc, base_path: Path | None = None) -> str:
    """Format a FileToc as a display string."""
    lines: list[str] = []

    # File header
    display_path = toc.path
    if base_path:
        try:
            display_path = toc.path.relative_to(base_path)
        except ValueError:
            pass

    lines.append(f'=== {display_path} ===')
    lines.append(f'chars: {toc.char_count:,} | lines: {toc.line_count:,}')

    if toc.error:
        lines.append(f'ERROR: {toc.error}')
        return '\n'.join(lines)

    if not toc.headings:
        lines.append('(no headings found)')
        return '\n'.join(lines)

    lines.append('')  # blank line before TOC

    # Determine minimum level for relative indentation
    min_level = min(h.level for h in toc.headings)

    for h in toc.headings:
        indent = '  ' * (h.level - min_level)
        hashes = '#' * h.level
        line_tag = f'L{h.line_num}'
        lines.append(f'{line_tag:<6} {indent}{hashes} {h.text}')

    return '\n'.join(lines)


# ============================================================================
# CLI Registration
# ============================================================================


def register_command(group: click.Group) -> None:
    """Register mdtoc as a Click subcommand."""
    import click
    from rich.console import Console

    console = Console()

    @group.command(name=TOOL_NAME, help=TOOL_DESCRIPTION)
    @click.argument('source', default='.', metavar='<source>')
    @click.option(
        '--depth', default=6, show_default=True, help='Maximum heading depth to include (1-6).'
    )
    @click.option(
        '--prompt',
        'show_prompt',
        is_flag=True,
        help='Show full tool specification for LLM consumption.',
    )
    def mdtoc_command(source: str, depth: int, show_prompt: bool) -> None:
        """Show Markdown TOC with line numbers.

        SOURCE can be a file path, directory, or glob pattern.
        Directories automatically glob all *.md files recursively.
        """
        if show_prompt:
            console.print(TOOL_PROMPT)
            return

        depth = max(1, min(6, depth))

        files = _resolve_sources(source)
        if not files:
            console.print(f'[yellow]No Markdown files found for: {source}[/yellow]')
            return

        # Determine a common base for relative path display
        source_path = Path(source)
        base_path = source_path if source_path.is_dir() else None

        results: list[FileToc] = []
        for f in files:
            results.append(_analyze_file(f, depth))

        # Summary header for multiple files
        if len(results) > 1:
            total_chars = sum(r.char_count for r in results)
            total_lines = sum(r.line_count for r in results)
            total_headings = sum(len(r.headings) for r in results)
            console.print(
                f'[bold]Found {len(results)} files[/bold]  '
                f'| total chars: {total_chars:,} | total lines: {total_lines:,} '
                f'| headings: {total_headings}'
            )
            console.print()

        for i, toc in enumerate(results):
            if i > 0:
                console.print()
            formatted = _format_toc(toc, base_path=base_path)
            console.print(formatted)
