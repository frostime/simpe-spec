"""sspec change command - change management operations."""

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from sspec.core import (
    ChangeExistsError,
    ChangeInfo,
    ChangeNotFoundError,
    ChangeStatus,
    InvalidChangeNameError,
    SspecNotFoundError,
    archive_change,
    create_change,
    get_sspec_root,
    list_changes,
    parse_change,
)

console = Console()

STATUS_STYLES: dict[str, tuple[str, str]] = {
    ChangeStatus.PLANNING.value: ('yellow', '📝'),
    ChangeStatus.DOING.value: ('cyan', '🔄'),
    ChangeStatus.BLOCKED.value: ('red', '🚧'),
    ChangeStatus.REVIEW.value: ('magenta', '👀'),
    ChangeStatus.DONE.value: ('green', '✅'),
}


@click.group()
def change() -> None:
    """Change management operations (new, list, archive)."""
    pass


@change.command()
@click.argument('name')
def new(name: str) -> None:
    """Create a new change proposal (spec, tasks, handover)."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    try:
        change_path = create_change(sspec_root, name)
    except (InvalidChangeNameError, ChangeExistsError) as e:
        raise click.ClickException(str(e)) from e

    rel_path = change_path.relative_to(sspec_root.parent)

    console.print(f'[green]+[/green] Created change: {name}')
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


@change.command(name='list')
@click.option('--all', 'include_all', is_flag=True, help='Include archived changes')
def list_changes_cmd(include_all: bool = False) -> None:
    """List all changes."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    _list_changes(sspec_root, include_all)


def _list_changes(sspec_root: Path, include_all: bool) -> None:
    """List changes."""
    changes = list_changes(sspec_root, include_archived=include_all)

    if not changes:
        console.print('[dim]No changes found.[/dim]')
        console.print()
        console.print('Create one with: sspec change new <change-name>')
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


@change.command()
@click.argument('name', required=False)
def status(name: str | None = None) -> None:
    """Show detailed status of a change."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    if not name:
        # If no name, show list
        _list_changes(sspec_root, include_all=False)
        return

    change_path = sspec_root / 'changes' / name
    if not change_path.exists():
        raise click.ClickException(f"Change '{name}' not found")

    _show_change_detail(change_path)


def _show_change_detail(change_path: Path) -> None:
    """Show detailed status of a single change."""
    change = parse_change(change_path)

    spec_file = change_path / 'spec.md'
    summary = ''
    if spec_file.exists():
        content = spec_file.read_text(encoding='utf-8')
        # Extract first meaningful paragraph after ## Why
        in_why = False
        for line in content.split('\n'):
            if line.startswith('## Why'):
                in_why = True
                continue
            if in_why and line.strip() and not line.startswith('<!--'):
                summary = line.strip()[:100]
                break
            if line.startswith('## ') and in_why:
                break

    console.print()
    console.print(
        Panel(
            f"[bold]{change['name']}[/bold]\n"
            f"Status: {change['status']}\n"
            f"Progress: {change['progress']['done']}/{change['progress']['total']}\n"
            f"{summary}",
            title='Change Details',
        )
    )


@change.command()
@click.argument('name', required=False)
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@click.option('--force', '-f', is_flag=True, help='Archive even if not DONE')
def archive(name: str | None, yes: bool, force: bool) -> None:
    """Archive a completed change."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    # If no name provided, try to auto-select
    if not name:
        changes = list_changes(sspec_root)
        active = [c for c in changes if not c['archived']]

        if not active:
            raise click.ClickException('No active changes to archive')
        elif len(active) == 1:
            name = active[0]['name']
            console.print(f'[dim]Auto-selected: {name}[/dim]')
        else:
            console.print('[cyan]Active changes:[/cyan]')
            for c in active:
                console.print(f"  - {c['name']}")
            name = click.prompt('Which change to archive?')

    # Check current status
    change_path = sspec_root / 'changes' / name  # type: ignore
    if not change_path.exists():
        raise click.ClickException(f"Change '{name}' not found")

    change_info = parse_change(change_path)
    current_status = change_info['status']

    # Interactive prompt if status is not DONE and not forced
    if current_status != ChangeStatus.DONE.value and not force:
        console.print()
        console.print(f'[yellow]Warning: Change \"{name}\" status is {current_status}, not DONE[/yellow]')
        console.print()
        console.print('[cyan]Options:[/cyan]')
        console.print('  1. Force archive (keep current status)')
        console.print('  2. Mark as DONE and archive')
        console.print('  3. Cancel')
        console.print()

        choice = click.prompt(
            'Select option',
            type=click.Choice(['1', '2', '3']),
            default='3'
        )

        if choice == '3':
            console.print('[yellow]Cancelled[/yellow]')
            return
        elif choice == '1':
            force = True
        elif choice == '2':
            # Update status to DONE in spec.md
            spec_file = change_path / 'spec.md'
            if spec_file.exists():
                content = spec_file.read_text(encoding='utf-8')
                # Update YAML front matter status
                if content.startswith('---'):
                    import re
                    content = re.sub(
                        r'(status:\s*)[^\n]+',
                        r'\1DONE',
                        content,
                        count=1
                    )
                    spec_file.write_text(content, encoding='utf-8')
                    console.print('[green]OK[/green] Updated status to DONE')

    # Confirm if not --yes
    if not yes:
        if not click.confirm(f"Archive '{name}'?"):
            console.print('[yellow]Cancelled[/yellow]')
            return

    try:
        archive_path = archive_change(sspec_root, name, force=force) # type: ignore
        rel_path = archive_path.relative_to(sspec_root.parent)
        console.print(f'[green]+[/green] Archived to: {rel_path}')
    except ChangeNotFoundError as e:
        raise click.ClickException(str(e)) from e
    except ValueError as e:
        raise click.ClickException(str(e)) from e
