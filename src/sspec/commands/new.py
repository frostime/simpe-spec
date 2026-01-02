"""sspec new command."""

import click
from rich.console import Console

from sspec.core import SspecNotFoundError, create_change, get_sspec_root

console = Console()


@click.command(name='change')
@click.argument('name')
def change(name: str) -> None:
    """Create a new change proposal (spec, tasks, handover)."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec init' first.")

    try:
        change_path = create_change(sspec_root, name)
    except ValueError as e:
        raise click.ClickException(str(e))

    rel_path = change_path.relative_to(sspec_root.parent)

    console.print(f'[green]✓[/green] Created change: {name}')
    console.print()
    console.print('[cyan]Files:[/cyan]')
    console.print(f'  {rel_path}/')
    console.print('  ├── spec.md      # Proposal and context')
    console.print('  ├── tasks.md     # Executable tasks and progress')
    console.print('  └── handover.md  # Session continuity (update every session!)')
    console.print()
    console.print('[yellow]Next:[/yellow]')
    console.print('  1. Fill in spec.md (proposal) and tasks.md (plan)')
    console.print('  2. Review with AI before implementation')
    console.print('  3. Update handover.md at end of each session')
