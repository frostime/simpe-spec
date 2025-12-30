"""sspec list command."""

import click
from rich.console import Console
from rich.table import Table

from sspec.core import SspecNotFoundError, get_sspec_root, list_changes

console = Console()

STATUS_COLORS = {
    'PLANNING': 'yellow',
    'IN_PROGRESS': 'cyan',
    'BLOCKED': 'red',
    'REVIEW': 'magenta',
    'DONE': 'green',
    'UNKNOWN': 'dim',
}


@click.command('list')
@click.option('--all', 'include_all', is_flag=True, help='Include archived changes')
def list_changes_cmd(include_all: bool) -> None:
    """List all changes."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec init' first.")

    changes = list_changes(sspec_root, include_archived=include_all)

    if not changes:
        console.print('[dim]No changes found.[/dim]')
        console.print()
        console.print('Create one with: sspec new <change-name>')
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


def _print_changes_table(changes: list, dim: bool = False) -> None:
    """Print changes as table."""
    table = Table(show_header=True, header_style='bold' if not dim else 'dim')
    table.add_column('Name')
    table.add_column('Status')
    table.add_column('Progress')
    table.add_column('Flags')

    for change in changes:
        status = change['status']
        color = STATUS_COLORS.get(status, 'white')
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
            f'[{color}]{status}[/{color}]',
            progress_str,
            ' '.join(flags),
        )

    console.print(table)
