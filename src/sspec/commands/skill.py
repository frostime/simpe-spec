"""sspec skill command - skill management operations."""

from __future__ import annotations

from pathlib import Path

import click
import questionary
from rich.console import Console

from sspec.core import SSPEC_DIR, SspecNotFoundError, get_sspec_root
from sspec.services.meta_service import load_meta
from sspec.services.skill_service import (
    create_skill_in_hub_and_install_to_linked_locations,
    get_linked_skill_locations,
    reinit_template_skills,
)

console = Console()


@click.group()
def skill() -> None:
    """Skill management operations (new, re-init)."""
    pass


def _existing_workspace_dirs(project_root: Path) -> set[str]:
    locs = {'.claude', '.github', '.agent'}
    return {loc for loc in locs if (project_root / loc).is_dir()}


def _installed_workspace_dirs_from_meta(sspec_root: Path) -> set[str]:
    meta = load_meta(sspec_root)
    skill_locations: list[str] = meta.get('skill_locations', []) or []
    installed: set[str] = set()
    for loc_str in skill_locations:
        loc_path = Path(loc_str)
        if not loc_path.parts:
            continue
        base = loc_path.parts[0]
        if base == SSPEC_DIR:
            continue
        if base in {'.claude', '.github', '.agent'}:
            installed.add(base)
    return installed


def _print_existing_skill_dirs(*, project_root: Path, sspec_root: Path) -> None:
    meta = load_meta(sspec_root)
    skill_locations: list[str] = meta.get('skill_locations', []) or []

    console.print()
    console.print('[bold cyan]Existing skill locations[/bold cyan]')
    if not skill_locations:
        console.print('  [dim](none in .meta.json)[/dim]')
        return

    for loc_str in skill_locations:
        p = project_root / loc_str
        exists = p.exists()
        status = '[green]exists[/green]' if exists else '[dim]missing[/dim]'
        if exists and p.is_dir():
            try:
                count = sum(1 for d in p.iterdir() if d.is_dir())
                console.print(f'  - {loc_str} ({status}, {count} dirs)')
            except OSError:
                console.print(f'  - {loc_str} ({status})')
        else:
            console.print(f'  - {loc_str} ({status})')


def _interactive_skill_location_selection(*, project_root: Path, sspec_root: Path) -> list[str]:
    available_locations = ['.claude', '.github', '.agent']
    existing_dirs = _existing_workspace_dirs(project_root)
    installed_dirs = _installed_workspace_dirs_from_meta(sspec_root)

    console.print()
    console.print('[bold cyan]Skill Location Selection (re-init)[/bold cyan]')
    console.print('[dim]Default selection follows locations already installed in .meta.json[/dim]')
    console.print()

    choices = []
    for loc in available_locations:
        flags: list[str] = []
        if loc in installed_dirs:
            flags.append('installed')
        if loc in existing_dirs:
            flags.append('existing')
        suffix = f" ({', '.join(flags)})" if flags else ''

        choices.append(
            questionary.Choice(
                title=f'{loc}{suffix}',
                value=loc,
                checked=loc in installed_dirs,
            )
        )

    selected = questionary.checkbox(
        'Select skill installation locations:',
        choices=choices,
        instruction='(Use arrow keys, space to toggle, enter to confirm)',
    ).ask()

    if selected is None:
        console.print('[yellow]Selection cancelled, keeping previous meta locations[/yellow]')
        return sorted(installed_dirs) if installed_dirs else ['.claude']

    if not selected:
        fallback = (
            sorted(installed_dirs) if installed_dirs else (sorted(existing_dirs) or ['.claude'])
        )
        console.print(
            f"[yellow]No locations selected, using fallback: {', '.join(fallback)}[/yellow]"
        )
        return list(fallback)

    return list(selected)


@skill.command()
@click.argument('name')
def new(name: str) -> None:
    """Create a new skill under `.sspec/skills`, and install to already-linked locations."""

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

## Purpose

<!-- Describe what this skill helps the AI to accomplish -->

## Guidelines

<!-- Provide specific instructions -->

## Examples

<!-- Show example usage patterns -->
"""

    try:
        result = create_skill_in_hub_and_install_to_linked_locations(
            sspec_root=sspec_root,
            name=name,
            template_content=template_content,
            prefer_symlink=True,
        )
    except FileExistsError as e:
        raise click.ClickException(str(e)) from None

    console.print(f"[green]✓[/green] Created skill '{name}'")
    console.print(f'  {result.hub_dir.relative_to(project_root)}/')
    console.print('  └── SKILL.md')

    if result.installed_to:
        for target_dir, strategy in result.installed_to:
            rel_target = target_dir.relative_to(project_root)
            console.print(f'  [green]+[/green] Installed to {rel_target}/ ({strategy})')
    else:
        linked = get_linked_skill_locations(sspec_root=sspec_root)
        if not linked:
            console.print('[yellow]No linked skill locations found in .meta.json[/yellow]')
            console.print("[dim]Tip: run 'sspec skill re-init' to (re)select locations.[/dim]")
    console.print()
    console.print('[yellow]Next:[/yellow]')
    console.print('  1. Edit SKILL.md to define your skill')
    console.print('  2. Add additional files (examples, templates) as needed')


@skill.command(name='re-init')
@click.option(
    '--skill-loc',
    multiple=True,
    type=click.Choice(['.claude', '.github', '.agent'], case_sensitive=False),
    help='Skill installation locations (can specify multiple, or use interactive mode)',
)
def re_init(skill_loc: tuple[str, ...]) -> None:
    """Re-install latest template skills into `.sspec/skills` and linked locations."""

    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    project_root = sspec_root.parent

    _print_existing_skill_dirs(project_root=project_root, sspec_root=sspec_root)

    skill_locations = (
        list(skill_loc)
        if skill_loc
        else _interactive_skill_location_selection(
            project_root=project_root,
            sspec_root=sspec_root,
        )
    )

    console.print()
    console.print('[dim]Re-initializing skills...[/dim]')

    result = reinit_template_skills(
        project_root=project_root,
        sspec_root=sspec_root,
        skill_locations=skill_locations,
        prefer_symlink=True,
    )

    console.print()
    for target_dir in result.skill_targets:
        if not target_dir.exists():
            continue
        rel_target = target_dir.relative_to(project_root)
        strategy = result.skill_install_strategies.get(str(rel_target), 'copy')
        console.print(f'  [green]+[/green] Installed skills to {rel_target}/ ({strategy})')

    console.print()
    console.print(f'[green]✓[/green] Re-initialized {len(result.managed_skills)} template skill(s)')
