"""sspec archive command."""

import click
from rich.console import Console

from sspec.core import archive_change, get_sspec_root, list_changes

console = Console()


@click.command()
@click.argument("name", required=False)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def archive(name: str, yes: bool) -> None:
    """Archive a completed change."""
    sspec_root = get_sspec_root()

    # If no name provided, try to auto-select
    if not name:
        changes = list_changes(sspec_root)
        active = [c for c in changes if not c["archived"]]

        if not active:
            raise click.ClickException("No active changes to archive")
        elif len(active) == 1:
            name = active[0]["name"]
            console.print(f"[dim]Auto-selected: {name}[/dim]")
        else:
            console.print("[cyan]Active changes:[/cyan]")
            for c in active:
                console.print(f"  - {c['name']}")
            name = click.prompt("Which change to archive?")

    # Confirm
    if not yes:
        if not click.confirm(f"Archive '{name}'?"):
            console.print("[yellow]Cancelled[/yellow]")
            return

    try:
        archive_path = archive_change(sspec_root, name)
    except ValueError as e:
        raise click.ClickException(str(e))

    rel_path = archive_path.relative_to(sspec_root.parent)
    console.print(f"[green]✓[/green] Archived to: {rel_path}")
