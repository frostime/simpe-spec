"""sspec list command."""

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from sspec.core import (
    ChangeInfo,
    ChangeStatus,
    SkillInfo,
    SspecNotFoundError,
    get_sspec_root,
    list_changes,
    list_skills,
)

console = Console()

STATUS_STYLES: dict[str, tuple[str, str]] = {
    ChangeStatus.PLANNING.value: ('yellow', '📝'),
    ChangeStatus.DOING.value: ('cyan', '🔄'),
    ChangeStatus.BLOCKED.value: ('red', '🚧'),
    ChangeStatus.REVIEW.value: ('magenta', '👀'),
    ChangeStatus.DONE.value: ('green', '✅'),
}


@click.command('list')
@click.option('--all', 'include_all', is_flag=True, help='Include archived changes')
@click.option('--changes', is_flag=True, help='List changes (default)')
@click.option('--skills', is_flag=True, help='List skills')
def list_changes_cmd(include_all: bool, changes: bool, skills: bool) -> None:
    """List changes or skills."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec init' first.")

    if not changes and not skills:
        changes = True

    if changes:
        _list_changes(sspec_root, include_all)

    if skills:
        if changes:
            console.print()
        _list_skills(sspec_root)


def _list_changes(sspec_root: Path, include_all: bool) -> None:
    """List changes."""
    changes = list_changes(sspec_root, include_archived=include_all)

    if not changes:
        console.print('[dim]No changes found.[/dim]')
        console.print()
        console.print('Create one with: sspec change <change-name>')
        return

    active = [c for c in changes if not c['archived']]
    archived = [c for c in changes if c['archived']]

    if active:
        console.print()
        console.print('[bold]Active Changes[/bold]')
        _print_changes_table(active)

    if archived and include_all:
        console.print()
        console.print('[bold dim]Archived[/bold dim]')
        _print_changes_table(archived, dim=True)

    console.print()
    console.print(f'[dim]Active: {len(active)} | Archived: {len(archived)}[/dim]')


def _list_skills(sspec_root: Path) -> None:
    """List skills."""
    skills = list_skills(sspec_root)

    if not skills:
        console.print('[dim]No skills found.[/dim]')
        return

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
    console.print(f'[dim]Total: {len(skills)}[/dim]')


def _print_changes_table(changes: list[ChangeInfo], dim: bool = False) -> None:
    """Print changes as table."""
    table = Table(show_header=True, header_style='bold' if not dim else 'dim')
    table.add_column('Name')
    table.add_column('Status')
    table.add_column('Progress')
    table.add_column('Flags')

    for change in changes:
        status = change['status']
        color, icon = STATUS_STYLES.get(status, ('dim', '❓'))
        if dim:
            color = 'dim'

        progress = change['progress']
        progress_str = ''
        if progress['total'] > 0:
            progress_str = f"{progress['done']}/{progress['total']}"

        flags = []
        if change['has_pivot']:
            flags.append('⚡pivot')
        if change['has_blockers']:
            flags.append('🚧blocked')

        table.add_row(
            f"[{color}]{change['name']}[/{color}]",
            f'[{color}]{icon} {status}[/{color}]',
            progress_str,
            ' '.join(flags),
        )

    console.print(table)
