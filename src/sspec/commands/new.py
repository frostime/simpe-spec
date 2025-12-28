"""sspec new command."""

import click
from rich.console import Console

from sspec.core import create_change, get_sspec_root

console = Console()


@click.command()
@click.argument("name")
def new(name: str) -> None:
    """Create a new change proposal."""
    sspec_root = get_sspec_root()

    try:
        change_path = create_change(sspec_root, name)
    except ValueError as e:
        raise click.ClickException(str(e))

    rel_path = change_path.relative_to(sspec_root.parent)

    console.print(f"[green]✓[/green] Created change: {name}")
    console.print()
    console.print("[cyan]Files:[/cyan]")
    console.print(f"  {rel_path}/")
    console.print("  ├── proposal.md   # Why and what")
    console.print("  ├── tasks.md      # Plan, progress, decisions")
    console.print("  └── handover.md   # Session handover")
    console.print()
    console.print("[yellow]Next:[/yellow] Edit proposal.md and tasks.md")
