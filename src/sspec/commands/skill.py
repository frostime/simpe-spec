"""sspec skill command - skill management operations."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from sspec.core import SspecNotFoundError, get_sspec_root
from sspec.services.meta_service import load_meta, save_meta
from sspec.services.skill_service import create_skill_in_hub, dominate_skills_location, list_skills

console = Console()


def _record_dominate_location(sspec_root: Path, dominate_dir: Path) -> None:
    """Record a newly dominated directory in .meta.json skill_locations."""
    project_root = sspec_root.parent
    try:
        # store the skills/ sub-path so it matches the convention used by init/sync
        location_path = (dominate_dir / 'skills').relative_to(project_root).as_posix()
    except ValueError:
        # dominate_dir is outside project_root — use absolute posix path
        location_path = (dominate_dir / 'skills').as_posix()

    try:
        meta = load_meta(sspec_root)
    except ValueError as e:
        raise click.ClickException(f'Invalid .meta.json: {e}') from None
    stored: set[str] = set(meta.get('skill_locations', []) or [])
    stored.add(location_path)
    meta['skill_locations'] = sorted(stored)
    save_meta(sspec_root, meta)


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
    except (FileExistsError, ValueError, OSError) as e:
        raise click.ClickException(str(e)) from None

    console.print(f"[green][OK][/green] Created skill '{name}'")
    console.print(f'  {result.hub_dir.relative_to(project_root)}/')
    console.print('  `-- SKILL.md')
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


@skill.command()
@click.argument('dir_path', type=click.Path(path_type=Path))
def dominate(dir_path: Path) -> None:
    """Dominate DIR by linking `DIR/skills` to `.sspec/skills`."""

    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    project_root = sspec_root.parent

    # User often passes a full ".../skills" path; normalize back to the parent directory.
    if dir_path.name == 'skills':
        if dir_path.parent == Path('.'):
            raise click.ClickException(
                "Invalid DIR. Pass the parent directory (e.g. '.claude'), not 'skills'."
            )
        dir_path = dir_path.parent

    if getattr(dir_path, 'drive', '') and not dir_path.is_absolute():
        raise click.ClickException(
            f'Invalid path: {dir_path}. Use an absolute path or a path relative to project root.'
        )
    dominate_dir = (
        (project_root / dir_path).resolve() if not dir_path.is_absolute() else dir_path.resolve()
    )

    try:
        result = dominate_skills_location(sspec_root=sspec_root, dominate_dir=dominate_dir)
    except (OSError, ValueError) as e:
        raise click.ClickException(str(e)) from None

    if result.status == 'needs_relink':
        current = result.current_target or result.target_dir.resolve(strict=False)
        if not click.confirm(
            f'{result.target_dir} points to {current}. Relink to {result.source_dir}?',
            default=False,
        ):
            console.print('[yellow]Skipped[/yellow]')
            return

        try:
            result = dominate_skills_location(
                sspec_root=sspec_root,
                dominate_dir=dominate_dir,
                force_relink=True,
            )
        except (OSError, ValueError) as e:
            raise click.ClickException(str(e)) from None

    try:
        rel_target = result.target_dir.relative_to(project_root)
    except ValueError:
        rel_target = result.target_dir

    try:
        rel_source = result.source_dir.relative_to(project_root)
    except ValueError:
        rel_source = result.source_dir

    # For all successful operations (including already-linked) record in meta.
    if result.status in {'linked', 'relinked', 'merged', 'skipped'}:
        _record_dominate_location(sspec_root, dominate_dir)

    if result.status == 'skipped':
        console.print(f'[cyan]-[/cyan] Already linked: {rel_target} -> {rel_source}')
        return

    if result.status == 'merged':
        if result.backup_path:
            try:
                rel_backup = result.backup_path.relative_to(project_root)
            except ValueError:
                rel_backup = result.backup_path
        else:
            rel_backup = None
        console.print(f'[green][OK][/green] Dominated skills directory: {rel_target}')
        if rel_backup:
            console.print(f'  [dim]Backup:[/dim] {rel_backup}')
        merged = result.merged_skills or []
        conflicts = result.conflict_skills or []
        if merged:
            console.print(f'  [dim]Merged:[/dim] {", ".join(sorted(merged))}')
        else:
            console.print('  [dim]Merged:[/dim] none')
        if conflicts:
            console.print(
                f'[yellow]Warning:[/yellow] Conflict skills kept in project hub (.sspec/skills): '
                f'{", ".join(sorted(conflicts))}'
            )
            if rel_backup:
                console.print(
                    f'[yellow]Warning:[/yellow] Review backup and merge manually: {rel_backup}'
                )
        console.print(f'  [dim]Link:[/dim] {result.link_kind}')
        return

    action = 'Relinked' if result.status == 'relinked' else 'Linked'
    console.print(f'[green][OK][/green] {action}: {rel_target} -> {rel_source}')
    console.print(f'  [dim]Link:[/dim] {result.link_kind}')
