"""sspec doc command - project specification document management."""

from datetime import datetime
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.table import Table

from sspec.core import (
    SspecNotFoundError,
    get_sspec_root,
    get_template_dir,
    render_template,
)

console = Console()

SPEC_DIR = 'spec-docs'


@click.group()
def doc() -> None:
    """Project specification document management (list, new)."""
    pass


@doc.command(name='list')
def list_specs() -> None:
    """List all project specification documents."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    spec_dir = sspec_root / SPEC_DIR
    if not spec_dir.exists():
        console.print('[dim]No spec-docs/ directory found.[/dim]')
        console.print()
        console.print('Create one with: sspec doc new <name>')
        return

    specs = _collect_specs(spec_dir)

    if not specs:
        console.print('[dim]No specification documents found.[/dim]')
        console.print()
        console.print('Create one with: sspec doc new <name>')
        return

    table = Table(show_header=True, header_style='bold')
    table.add_column('Name', style='cyan')
    table.add_column('Description')
    table.add_column('Updated', style='dim')
    table.add_column('Type', style='dim')

    for s in specs:
        updated = s.get('updated', '')
        if updated and not isinstance(updated, str):
            updated = str(updated)
        table.add_row(
            s['name'],
            s.get('description', '') or '',
            updated,
            s['type'],
        )

    console.print()
    console.print('[bold]Project Specifications[/bold]')
    console.print(table)


def _collect_specs(spec_dir: Path) -> list[dict]:
    """Collect all specifications from spec directory."""
    specs = []

    for item in spec_dir.iterdir():
        if item.name == 'README.md':
            continue

        if item.is_file() and item.suffix == '.md':
            # Single file spec
            meta = _parse_spec_frontmatter(item)
            if meta:
                meta['type'] = 'file'
                meta['path'] = item.name
                specs.append(meta)
        elif item.is_dir():
            # Directory spec - look for index.md
            index_file = item / 'index.md'
            if index_file.exists():
                meta = _parse_spec_frontmatter(index_file)
                if meta:
                    meta['type'] = 'dir'
                    meta['path'] = item.name
                    specs.append(meta)

    return sorted(specs, key=lambda x: x.get('name', ''))


def _parse_spec_frontmatter(file_path: Path) -> dict | None:
    """Parse YAML frontmatter from a spec file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        if not content.startswith('---'):
            return {'name': file_path.stem}

        # Find end of frontmatter
        end_idx = content.find('---', 3)
        if end_idx == -1:
            return {'name': file_path.stem}

        frontmatter = content[3:end_idx].strip()
        meta = yaml.safe_load(frontmatter) or {}

        # Ensure name exists
        if 'name' not in meta:
            meta['name'] = file_path.stem

        return meta
    except Exception:
        return {'name': file_path.stem}


@doc.command()
@click.argument('name')
@click.option('--dir', 'is_dir', is_flag=True, help='Create as directory with index.md')
def new(name: str, is_dir: bool) -> None:
    """Create a new project specification document."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    spec_dir = sspec_root / SPEC_DIR
    spec_dir.mkdir(exist_ok=True)

    # Sanitize name for filename
    safe_name = name.lower().replace(' ', '-')
    today = datetime.now().strftime('%Y-%m-%d')

    template_dir = get_template_dir() / 'spec-docs'
    replacements = {
        'SPEC_NAME': name,
        'DATE': today,
    }

    if is_dir:
        # Create directory with index.md
        target_dir = spec_dir / safe_name
        if target_dir.exists():
            raise click.ClickException(f"Specification document '{safe_name}/' already exists.")

        target_dir.mkdir()
        template_file = template_dir / 'index.md'
        target_file = target_dir / 'index.md'

        content = template_file.read_text(encoding='utf-8')
        content = render_template(content, replacements)
        target_file.write_text(content, encoding='utf-8')

        rel_path = target_dir.relative_to(sspec_root.parent)
        console.print(f'[green]✓[/green] Created specification document: {rel_path}/')
        console.print()
        console.print('[cyan]Structure:[/cyan]')
        console.print(f'  {rel_path}/')
        console.print('  └── index.md    # Entry point with frontmatter')
        console.print()
        console.print('[yellow]Next:[/yellow]')
        console.print('  1. Edit index.md (add description)')
        console.print('  2. Add related files to the directory')
        console.print("  3. Update 'files' list in frontmatter")
    else:
        # Create single file
        target_file = spec_dir / f'{safe_name}.md'
        if target_file.exists():
            raise click.ClickException(f"Specification document '{safe_name}.md' already exists.")

        template_file = template_dir / 'template.md'
        content = template_file.read_text(encoding='utf-8')
        content = render_template(content, replacements)
        target_file.write_text(content, encoding='utf-8')

        rel_path = target_file.relative_to(sspec_root.parent)
        console.print(f'[green]✓[/green] Created specification document: {rel_path}')
        console.print()
        console.print('[yellow]Next:[/yellow]')
        console.print('  1. Add description in frontmatter')
        console.print('  2. Write specification content')
        console.print('  3. Update "updated" field when modifying')
