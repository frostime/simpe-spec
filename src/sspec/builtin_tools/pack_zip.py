"""Project packaging tool with .gitignore support."""

from __future__ import annotations

import zipfile
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pathspec

__all__ = [
    'TOOL_NAME',
    'TOOL_DESCRIPTION',
    'TOOL_PROMPT',
    'register_command',
]

TOOL_NAME = 'pack-zip'
TOOL_DESCRIPTION = 'Package project into zip with .gitignore support'

# Default patterns to exclude
DEFAULT_EXCLUDE_PATTERNS = [
    '.git',
    '.sspec/archive',
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.Python',
    'node_modules',
    '.DS_Store',
    'Thumbs.db',
]


# ============================================================================
# Gitignore Parser
# ============================================================================


class GitignoreParser:
    """Parse and apply .gitignore rules."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.specs: dict[Path, pathspec.PathSpec] = {}
        self.has_pathspec = False

        # Try to import pathspec
        try:
            import pathspec

            self.pathspec = pathspec
            self.has_pathspec = True
            self._load_gitignores()
        except ImportError:
            # Fallback to simple pattern matching
            self.patterns: list[str] = []
            self._load_simple_patterns()

    def _load_gitignores(self) -> None:
        """Load all .gitignore files recursively (pathspec mode)."""
        if not self.has_pathspec:
            return

        for gitignore_path in self.root.rglob('.gitignore'):
            try:
                patterns = gitignore_path.read_text(encoding='utf-8').splitlines()
                # Filter out comments and empty lines
                patterns = [p.strip() for p in patterns if p.strip() and not p.startswith('#')]

                if patterns:
                    parent = gitignore_path.parent
                    self.specs[parent] = self.pathspec.PathSpec.from_lines('gitwildmatch', patterns)
            except Exception:
                continue

    def _load_simple_patterns(self) -> None:
        """Load .gitignore as simple patterns (fallback mode)."""
        gitignore_path = self.root / '.gitignore'
        if not gitignore_path.exists():
            return

        try:
            lines = gitignore_path.read_text(encoding='utf-8').splitlines()
            self.patterns = [
                line.strip() for line in lines if line.strip() and not line.startswith('#')
            ]
        except Exception:
            self.patterns = []

    def should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        if self.has_pathspec:
            return self._should_ignore_pathspec(path)
        else:
            return self._should_ignore_simple(path)

    def _should_ignore_pathspec(self, path: Path) -> bool:
        """Check using pathspec library."""
        try:
            path.relative_to(self.root)
        except ValueError:
            return True

        # Check all applicable .gitignore files
        for spec_dir, spec in self.specs.items():
            try:
                if path.is_relative_to(spec_dir):
                    check_path = path.relative_to(spec_dir)
                    if spec.match_file(str(check_path)):
                        return True
            except ValueError:
                continue

        return False

    def _should_ignore_simple(self, path: Path) -> bool:
        """Simple pattern matching fallback."""
        try:
            rel_path = path.relative_to(self.root)
            path_str = str(rel_path).replace('\\', '/')

            for pattern in self.patterns:
                # Very basic matching
                if pattern.endswith('/'):
                    # Directory pattern
                    if path_str.startswith(pattern[:-1] + '/') or path_str == pattern[:-1]:
                        return True
                elif '*' in pattern:
                    # Wildcard pattern (simplified)
                    pattern_clean = pattern.replace('*', '')
                    if pattern_clean in path_str:
                        return True
                else:
                    # Exact match
                    if path_str == pattern or path_str.startswith(pattern + '/'):
                        return True

        except ValueError:
            return True

        return False


# ============================================================================
# Pattern Matcher (for --exclude and --include)
# ============================================================================


class PatternMatcher:
    """Simple pattern matcher for additional exclude/include rules."""

    def __init__(self, patterns: list[str]):
        self.patterns = patterns
        self.has_pathspec = False

        try:
            import pathspec

            self.spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)
            self.has_pathspec = True
        except ImportError:
            # Fallback mode
            pass

    def matches(self, path: Path, root: Path) -> bool:
        """Check if path matches any pattern."""
        try:
            rel_path = path.relative_to(root)
            path_str = str(rel_path).replace('\\', '/')

            if self.has_pathspec:
                return self.spec.match_file(path_str)
            else:
                # Simple fallback
                for pattern in self.patterns:
                    if pattern in path_str or path_str.endswith(pattern):
                        return True
                return False

        except ValueError:
            return False


# ============================================================================
# Pack Function
# ============================================================================


def pack_zip(
    root: Path,
    output: Path,
    exclude_patterns: list[str],
    include_patterns: list[str],
    respect_gitignore: bool = True,
    include_archive: bool = False,
    exclude_defaults: bool = False,
) -> tuple[int, int]:
    """Pack directory into zip file.

    Returns (files_added, files_skipped).
    """
    root = root.resolve()

    # Build exclude list
    all_exclude = []
    if not exclude_defaults:
        all_exclude.extend(DEFAULT_EXCLUDE_PATTERNS)
    all_exclude.extend(exclude_patterns)

    # Initialize matchers
    gitignore = GitignoreParser(root) if respect_gitignore else None
    exclude_matcher = PatternMatcher(all_exclude) if all_exclude else None
    include_matcher = PatternMatcher(include_patterns) if include_patterns else None

    files_added = 0
    files_skipped = 0

    # Resolve output path to skip it during packing
    output_resolved = output.resolve()

    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in root.rglob('*'):
            if not file_path.is_file():
                continue

            # Skip the output zip file itself
            try:
                if file_path.resolve() == output_resolved:
                    continue
            except Exception:
                pass

            try:
                rel_path = file_path.relative_to(root)

                # Force include has highest priority
                if include_matcher and include_matcher.matches(file_path, root):
                    zf.write(file_path, rel_path)
                    files_added += 1
                    continue

                # Check gitignore
                if gitignore and gitignore.should_ignore(file_path):
                    files_skipped += 1
                    continue

                # Check exclude patterns
                if exclude_matcher and exclude_matcher.matches(file_path, root):
                    files_skipped += 1
                    continue

                # Add file
                zf.write(file_path, rel_path)
                files_added += 1

            except Exception:
                files_skipped += 1
                continue

    return files_added, files_skipped


# ============================================================================
# Tool Prompt
# ============================================================================

TOOL_PROMPT = """# pack-zip - Project Packaging Tool

## Purpose
Package project into zip file with automatic .gitignore support.

## Usage

### Basic
```bash
# Package to default output (project_name_timestamp.zip)
sspec tool pack-zip

# Specify output path
sspec tool pack-zip -o backup.zip

# Preview files (dry run)
sspec tool pack-zip --dry-run
```

### Exclude/Include Rules

#### Exclude additional files
```bash
# Exclude all .log files
sspec tool pack-zip --exclude "*.log"

# Exclude multiple patterns
sspec tool pack-zip --exclude "*.log" --exclude "temp/*"
```

#### Force include files (override .gitignore)
```bash
# Include .env.example even if in .gitignore
sspec tool pack-zip --include ".env.example"
```

#### Disable .gitignore
```bash
sspec tool pack-zip --no-gitignore
```

### Options
```bash
-o, --output PATH      Output zip path
--exclude PATTERN      Additional exclude pattern (repeatable)
--include PATTERN      Force include pattern (repeatable)
--no-gitignore        Don't respect .gitignore files
--include-archive     Include .sspec/archive/ directory
--exclude-defaults    Don't use default exclude patterns
--dry-run            Preview files without creating zip
--prompt             Show this help message
```

## Default Behavior

### Auto-excluded
- `.git/` directory
- `.sspec/archive/` (use --include-archive to include)
- `__pycache__/`, `*.pyc`, `*.pyo`
- `node_modules/`
- `.DS_Store`, `Thumbs.db`

### Gitignore Support
- Reads `.gitignore` in project root and all subdirectories
- Follows standard gitignore syntax (requires `pathspec` library)
- Falls back to simple matching if pathspec not installed

### Priority Order (highest to lowest)
1. `--include` patterns (force include)
2. `.gitignore` rules
3. `--exclude` patterns
4. Default exclude patterns

## Examples

### Archive project
```bash
sspec tool pack-zip -o archive/project_v1.0.zip
```

### Share code (exclude secrets)
```bash
sspec tool pack-zip --exclude ".env*" --exclude "secrets/*"
```

### Submit homework (include config examples)
```bash
sspec tool pack-zip --include ".env.example" -o submission.zip
```

## Notes
- Requires `pathspec` library for full .gitignore support
- Without pathspec: falls back to simple pattern matching
- Large projects may take time to scan
"""


# ============================================================================
# CLI Registration
# ============================================================================


def register_command(group):
    """Register pack-zip command to the tool group."""
    import click
    from rich.console import Console

    from sspec.core import find_sspec_root

    console = Console()

    @group.command(name=TOOL_NAME, help=TOOL_DESCRIPTION)
    @click.option(
        '-o',
        '--output',
        type=click.Path(path_type=Path),
        help='Output zip file path',
    )
    @click.option(
        '--exclude',
        multiple=True,
        help='Additional exclude pattern (repeatable)',
    )
    @click.option(
        '--include',
        multiple=True,
        help='Force include pattern (repeatable)',
    )
    @click.option(
        '--no-gitignore',
        is_flag=True,
        help="Don't respect .gitignore files",
    )
    @click.option(
        '--include-archive',
        is_flag=True,
        help='Include .sspec/archive/ directory',
    )
    @click.option(
        '--exclude-defaults',
        is_flag=True,
        help="Don't use default exclude patterns",
    )
    @click.option(
        '--dry-run',
        is_flag=True,
        help='Preview files without creating zip',
    )
    @click.option(
        '--prompt',
        'show_prompt',
        is_flag=True,
        help='Show tool usage guide',
    )
    def pack_zip_command(
        output: Path | None,
        exclude: tuple[str, ...],
        include: tuple[str, ...],
        no_gitignore: bool,
        include_archive: bool,
        exclude_defaults: bool,
        dry_run: bool,
        show_prompt: bool,
    ):
        """Package project into zip with .gitignore support."""

        # Show help
        if show_prompt:
            console.print(TOOL_PROMPT)
            return

        # Determine project root
        sspec_root = find_sspec_root()
        if sspec_root:
            root = sspec_root.parent
        else:
            root = Path.cwd()
            console.print(f'[yellow]Warning:[/yellow] Not in sspec project, using cwd: {root}')

        # Determine output path
        if output is None:
            project_name = root.name
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output = root / f'{project_name}_{timestamp}.zip'

        # Prepare exclude patterns
        exclude_list = list(exclude)
        if not include_archive:
            exclude_list.append('.sspec/archive')

        # Dry run: preview files
        if dry_run:
            console.print('[yellow]Dry-run mode: previewing files[/yellow]\n')
            preview_files(
                root,
                exclude_patterns=exclude_list,
                include_patterns=list(include),
                respect_gitignore=not no_gitignore,
                exclude_defaults=exclude_defaults,
            )
            return

        # Pack
        try:
            console.print(f'[cyan]Packing project:[/cyan] {root}')
            console.print(f'[cyan]Output:[/cyan] {output}\n')

            files_added, files_skipped = pack_zip(
                root=root,
                output=output,
                exclude_patterns=exclude_list,
                include_patterns=list(include),
                respect_gitignore=not no_gitignore,
                include_archive=include_archive,
                exclude_defaults=exclude_defaults,
            )

            console.print(f'[green][OK][/green] Created: {output}')
            console.print(f'  Files added: {files_added}')
            console.print(f'  Files skipped: {files_skipped}')

        except Exception as e:
            console.print(f'[red]Error:[/red] {e}')
            raise click.Abort() from e


def preview_files(
    root: Path,
    exclude_patterns: list[str],
    include_patterns: list[str],
    respect_gitignore: bool,
    exclude_defaults: bool,
):
    """Preview files that would be included."""
    from rich.console import Console

    console = Console()

    # Collect files
    all_exclude = []
    if not exclude_defaults:
        all_exclude.extend(DEFAULT_EXCLUDE_PATTERNS)
    all_exclude.extend(exclude_patterns)

    gitignore = GitignoreParser(root) if respect_gitignore else None
    exclude_matcher = PatternMatcher(all_exclude) if all_exclude else None
    include_matcher = PatternMatcher(include_patterns) if include_patterns else None

    included = []
    excluded = []

    for file_path in root.rglob('*'):
        if not file_path.is_file():
            continue

        try:
            rel_path = file_path.relative_to(root)

            # Check inclusion
            if include_matcher and include_matcher.matches(file_path, root):
                included.append(str(rel_path))
                continue

            if gitignore and gitignore.should_ignore(file_path):
                excluded.append(str(rel_path))
                continue

            if exclude_matcher and exclude_matcher.matches(file_path, root):
                excluded.append(str(rel_path))
                continue

            included.append(str(rel_path))

        except Exception:
            excluded.append(str(file_path))

    # Display
    console.print(f'[green]Files to include:[/green] {len(included)}')
    if included[:20]:
        for path in included[:20]:
            console.print(f'  + {path}')
        if len(included) > 20:
            console.print(f'  ... and {len(included) - 20} more')

    console.print(f'\n[yellow]Files to exclude:[/yellow] {len(excluded)}')
    if excluded[:10]:
        for path in excluded[:10]:
            console.print(f'  - {path}')
        if len(excluded) > 10:
            console.print(f'  ... and {len(excluded) - 10} more')
