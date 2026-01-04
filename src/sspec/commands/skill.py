"""sspec skill command - skill management operations."""

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from sspec.core import (
    SCHEMA_VERSION,
    SspecNotFoundError,
    get_sspec_root,
    list_skills,
)

console = Console()


@click.group()
def skill() -> None:
    """Skill management operations (list, new)."""
    pass


@skill.command(name='list')
def list_skills_cmd() -> None:
    """List all skills."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    _list_skills(sspec_root)


def _list_skills(sspec_root: Path) -> None:
    """List skills."""
    skills = list_skills(sspec_root)

    if not skills:
        console.print('[dim]No skills found.[/dim]')
        console.print()
        console.print('Create one with: sspec skill new <skill-name>')
        return

    console.print()
    console.print('[bold]Skills[/bold]')
    table = Table(show_header=True, header_style='bold')
    table.add_column('Skill')
    table.add_column('Description')
    table.add_column('File')

    for skill in skills:
        table.add_row(
            skill['skill'],
            skill['description'],
            skill['file'],
        )

    console.print(table)
    console.print()
    console.print(f'[dim]Total: {len(skills)}[/dim]')


@skill.command()
@click.argument('name')
@click.option(
    '--mode',
    type=click.Choice(['simple', 'complex'], case_sensitive=False),
    default='simple',
    help='Creation mode: simple (single .md file) or complex (directory with SKILL.md)',
)
def new(name: str, mode: str) -> None:
    """Create a new skill file or directory.

    Simple mode: Creates <name>.md in .sspec/skills/
    Complex mode: Creates .sspec/skills/<name>/SKILL.md
    """
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    skills_dir = sspec_root / 'skills'
    skills_dir.mkdir(parents=True, exist_ok=True)

    if mode == 'simple':
        # Create single markdown file
        skill_file = skills_dir / f'{name}.md'
        if skill_file.exists():
            raise click.ClickException(f"Skill file '{skill_file.name}' already exists")

        template_content = f"""---
skill: {name}
version: 1.0.0
schema: {SCHEMA_VERSION}
---

# {name}

## Purpose

<!-- Describe what this skill helps the AI to accomplish -->

## Context

<!-- Provide relevant background information -->

## Guidelines

<!-- Provide specific instructions for using this skill -->

## Examples

<!-- Optional: Show example usage patterns -->

## Related

<!-- Optional: Link to related skills or resources -->
"""
        skill_file.write_text(template_content, encoding='utf-8')

        console.print(f'[green]✓[/green] Created skill: {skill_file.name}')
        console.print()
        console.print(f'  {skill_file.relative_to(sspec_root.parent)}')
        console.print()
        console.print('[yellow]Next:[/yellow] Edit the file to define your skill')

    else:  # complex mode
        # Create directory with SKILL.md
        skill_dir = skills_dir / name
        if skill_dir.exists():
            raise click.ClickException(f"Skill directory '{name}' already exists")

        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / 'SKILL.md'

        template_content = f"""---
skill: {name}
version: 1.0.0
schema: {SCHEMA_VERSION}
---

# {name}

## Purpose

<!-- Describe what this skill helps the AI to accomplish -->

## Context

<!-- Provide relevant background information -->

## Guidelines

<!-- Provide specific instructions for using this skill -->

## Structure

<!-- Describe additional files in this skill directory -->

This skill uses multiple files:
- `SKILL.md` - Main skill definition (this file)
- Add other files as needed for examples, templates, etc.

## Examples

<!-- Optional: Show example usage patterns or link to example files -->

## Related

<!-- Optional: Link to related skills or resources -->
"""
        skill_file.write_text(template_content, encoding='utf-8')

        console.print(f'[green]✓[/green] Created skill directory: {name}/')
        console.print()
        console.print(f'  {skill_dir.relative_to(sspec_root.parent)}/')
        console.print('  └── SKILL.md')
        console.print()
        console.print('[yellow]Next:[/yellow]')
        console.print('  1. Edit SKILL.md to define your skill')
        console.print('  2. Add additional files (examples, templates) as needed')
