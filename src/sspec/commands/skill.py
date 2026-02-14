"""sspec skill command - skill management operations."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from sspec.core import SspecNotFoundError, get_sspec_root
from sspec.services.skill_service import create_skill_in_hub, list_skills

console = Console()


@click.group()
def skill() -> None:
    """Skill management operations (new, list)."""
    pass


@skill.command()
@click.argument('name')
def new(name: str) -> None:
    """Create a new skill under `.sspec/skills/<name>`."""

    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    project_root = sspec_root.parent

    template_content = f"""---
name: {name}
description: ""
---

# {name}

"""

    try:
        result = create_skill_in_hub(
            sspec_root=sspec_root,
            name=name,
            template_content=template_content,
        )
    except FileExistsError as e:
        raise click.ClickException(str(e)) from None

    console.print(f"[green]✓[/green] Created skill '{name}'")
    console.print(f'  {result.hub_dir.relative_to(project_root)}/')
    console.print('  └── SKILL.md')
    console.print()
    console.print('[yellow]Next:[/yellow]')
    console.print('  1. Edit SKILL.md to define your skill')
    console.print('  2. Add additional files (examples, templates) as needed')


@skill.command(name='list')
def list_skills_cmd() -> None:
    """List all skills in `.sspec/skills`."""

    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    sspec_root = get_sspec_root()
    skills = list_skills(sspec_root)

    if not skills:
        console.print('[dim]No skills found in .sspec/skills[/dim]')
        return

    table = Table(title='Skills in .sspec/skills')
    table.add_column('Name', style='cyan')
    table.add_column('Description', style='dim')

    for skill_info in skills:
        table.add_row(skill_info['skill'], skill_info['description'])

    console.print(table)
    console.print(f'[dim]{len(skills)} skill(s)[/dim]')
