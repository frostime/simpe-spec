"""File metadata and text-format inspection helper."""

from __future__ import annotations

import glob as globlib
import json
from collections import OrderedDict
from dataclasses import asdict, dataclass
from datetime import datetime
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

TOOL_NAME = 'fileinfo'
TOOL_DESCRIPTION = 'Inspect file size, encoding, newline style, and text/binary status'

TOOL_PROMPT = """
# fileinfo - File Metadata and Encoding Inspector

## Purpose

Inspect one or more files without requiring an `.sspec/` project.
Supports files, directories, absolute paths, relative paths, and glob patterns.

## Usage

```bash
sspec tool fileinfo README.md
sspec tool fileinfo src/
sspec tool fileinfo "src/**/*.py"
sspec tool fileinfo a.txt docs/ "**/*.md" --json
```

## Behavior

- Files are inspected directly
- Directories are expanded recursively into files
- Glob patterns use Python glob syntax and support `**`
- Duplicate matches are removed automatically

## Reported Fields

- path
- size in bytes
- modified time
- binary vs text-like
- probable encoding / BOM
- newline style
- line count for decodable text files

## Notes

- Encoding detection is heuristic and stdlib-only
- `--json` is recommended for agent consumption
- `--max-files` can limit very large directory or glob expansions
""".strip()

GLOB_CHARS = set('*?[')
TEXT_SAMPLE_BYTES = 65536
LINE_COUNT_LIMIT = 1024 * 1024

BOMS: list[tuple[bytes, str]] = [
    (b'\xef\xbb\xbf', 'utf-8-sig'),
    (b'\xff\xfe', 'utf-16-le'),
    (b'\xfe\xff', 'utf-16-be'),
]


@dataclass
class FileInfo:
    """Structured metadata for a single inspected file."""

    path: str
    size_bytes: int
    modified: str
    kind: str
    encoding: str
    bom: str
    newline: str
    line_count: int | None


def _has_glob_magic(source: str) -> bool:
    """Return whether the source contains glob syntax."""
    return any(char in source for char in GLOB_CHARS)


def _display_path(path: Path) -> str:
    """Display paths relative to cwd when possible."""
    try:
        return str(path.relative_to(Path.cwd())).replace('\\', '/')
    except ValueError:
        return str(path)


def _resolve_sources(
    sources: tuple[str, ...], max_files: int | None
) -> tuple[list[Path], list[str]]:
    """Resolve file, directory, and glob inputs into a deduplicated file list."""
    ordered: OrderedDict[str, Path] = OrderedDict()
    missing: list[str] = []
    effective_sources = sources or ('.',)

    def add_path(path: Path) -> None:
        resolved = path.expanduser().resolve(strict=False)
        key = str(resolved)
        if key not in ordered:
            ordered[key] = resolved

    for source in effective_sources:
        if max_files is not None and len(ordered) >= max_files:
            break

        source_path = Path(source).expanduser()
        if source_path.exists():
            resolved = source_path.resolve()
            if resolved.is_file():
                add_path(resolved)
            elif resolved.is_dir():
                for child in sorted(resolved.rglob('*')):
                    if child.is_file():
                        add_path(child)
                        if max_files is not None and len(ordered) >= max_files:
                            break
            continue

        if _has_glob_magic(source):
            matches = [Path(match) for match in globlib.glob(source, recursive=True)]
            for match in sorted(matches):
                if match.is_file():
                    add_path(match)
                elif match.is_dir():
                    for child in sorted(match.rglob('*')):
                        if child.is_file():
                            add_path(child)
                            if max_files is not None and len(ordered) >= max_files:
                                break
                if max_files is not None and len(ordered) >= max_files:
                    break
            continue

        missing.append(source)

    return list(ordered.values()), missing


def _detect_bom(data: bytes) -> tuple[str, str | None]:
    """Return BOM name and implied encoding when present."""
    for marker, encoding in BOMS:
        if data.startswith(marker):
            return encoding, encoding
    return 'none', None


def _is_binary_data(data: bytes, bom_encoding: str | None) -> bool:
    """Heuristic binary detector that stays conservative for BOM-tagged text."""
    if not data:
        return False
    if bom_encoding is not None:
        return False
    if b'\x00' in data:
        return True

    disallowed = 0
    for byte in data:
        if byte in {9, 10, 13}:
            continue
        if 32 <= byte <= 126:
            continue
        if byte >= 128:
            continue
        disallowed += 1

    return disallowed / max(len(data), 1) > 0.30


def _guess_encoding(data: bytes, bom_encoding: str | None, is_binary: bool) -> str:
    """Guess a text encoding using stdlib-only checks."""
    if bom_encoding is not None:
        return bom_encoding
    if is_binary:
        return 'binary'

    for encoding in ('utf-8', 'gbk', 'cp936', 'latin1'):
        try:
            data.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    return 'unknown'


def _detect_newline(data: bytes, is_binary: bool) -> str:
    """Detect newline style from raw bytes."""
    if is_binary or not data:
        return 'unknown'

    has_crlf = b'\r\n' in data
    stripped = data.replace(b'\r\n', b'')
    has_lf = b'\n' in stripped
    has_cr = b'\r' in stripped

    if has_crlf and not has_lf and not has_cr:
        return 'crlf'
    if has_lf and not has_crlf and not has_cr:
        return 'lf'
    if has_cr and not has_crlf and not has_lf:
        return 'cr'
    if has_crlf or has_lf or has_cr:
        return 'mixed'
    return 'none'


def _count_lines(path: Path, encoding: str, size_bytes: int, is_binary: bool) -> int | None:
    """Return line count for manageable text files."""
    if is_binary or encoding in {'binary', 'unknown'} or size_bytes > LINE_COUNT_LIMIT:
        return None

    try:
        with path.open('r', encoding=encoding, errors='strict', newline='') as handle:
            text = handle.read()
    except (OSError, UnicodeDecodeError, LookupError):
        return None

    if not text:
        return 0
    return len(text.splitlines())


def _inspect_file(path: Path) -> FileInfo:
    """Inspect a single file and return metadata plus text-format hints."""
    stat = path.stat()
    sample_size = min(stat.st_size, TEXT_SAMPLE_BYTES)

    with path.open('rb') as handle:
        sample = handle.read(sample_size)

    bom, bom_encoding = _detect_bom(sample)
    is_binary = _is_binary_data(sample, bom_encoding)
    encoding = _guess_encoding(sample, bom_encoding, is_binary)
    newline = _detect_newline(sample, is_binary)
    line_count = _count_lines(path, encoding, stat.st_size, is_binary)

    return FileInfo(
        path=_display_path(path),
        size_bytes=stat.st_size,
        modified=datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec='seconds'),
        kind='binary' if is_binary else 'text',
        encoding=encoding,
        bom=bom,
        newline=newline,
        line_count=line_count,
    )


def register_command(group: click.Group) -> None:
    """Register fileinfo as a Click subcommand."""
    import click
    from rich.console import Console
    from rich.table import Table

    console = Console()

    @group.command(name=TOOL_NAME, help=TOOL_DESCRIPTION)
    @click.argument('sources', nargs=-1)
    @click.option('--json', 'json_output', is_flag=True, help='Show JSON output.')
    @click.option('--max-files', type=int, help='Maximum number of files to inspect.')
    @click.option(
        '--prompt',
        'show_prompt',
        is_flag=True,
        help='Show agent-oriented usage guidance.',
    )
    def fileinfo_command(
        sources: tuple[str, ...], json_output: bool, max_files: int | None, show_prompt: bool
    ) -> None:
        """Inspect file size, encoding, newline style, and text/binary status."""
        if show_prompt:
            console.print(TOOL_PROMPT)
            return

        if max_files is not None and max_files < 1:
            raise click.ClickException('--max-files must be >= 1')

        paths, missing = _resolve_sources(sources, max_files)
        if not paths and missing:
            raise click.ClickException('No files found for the provided inputs.')
        if not paths:
            console.print('[yellow]No files found.[/yellow]')
            return

        infos = [_inspect_file(path) for path in paths]

        if json_output:
            payload = {
                'files': [asdict(info) for info in infos],
                'count': len(infos),
                'missing_sources': missing,
            }
            click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
            return

        table = Table(title=f'File Info ({len(infos)} file(s))', show_lines=False)
        table.add_column('Path', style='cyan')
        table.add_column('Kind', style='green', no_wrap=True)
        table.add_column('Size', justify='right', no_wrap=True)
        table.add_column('Encoding', no_wrap=True)
        table.add_column('BOM', no_wrap=True)
        table.add_column('Newline', no_wrap=True)
        table.add_column('Lines', justify='right', no_wrap=True)

        for info in infos:
            table.add_row(
                info.path,
                info.kind,
                str(info.size_bytes),
                info.encoding,
                info.bom,
                info.newline,
                '-' if info.line_count is None else str(info.line_count),
            )

        console.print(table)
        if missing:
            console.print(f'[yellow]Missing sources:[/yellow] {", ".join(missing)}')
