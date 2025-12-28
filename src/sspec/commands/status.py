"""sspec status command."""

from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

from sspec.core import get_sspec_root, list_changes, parse_change

console = Console()


@click.command()
@click.argument("name", required=False)
def status(name: Optional[str] = None) -> None:
    """Show status summary."""
    sspec_root = get_sspec_root()

    if name:
        # Show specific change status
        change_path = sspec_root / "changes" / name
        if not change_path.exists():
            raise click.ClickException(f"Change '{name}' not found")
        _show_change_detail(change_path)
    else:
        # Show overview
        _show_overview(sspec_root)


def _show_overview(sspec_root) -> None:
    """Show project overview."""
    changes = list_changes(sspec_root)
    active = [c for c in changes if not c["archived"]]

    console.print()
    console.print("[bold]sspec Status[/bold]")
    console.print()

    if not active:
        console.print("[dim]No active changes[/dim]")
    else:
        for change in active:
            status = change["status"]
            progress = change["progress"]
            
            status_icon = {
                "PLANNING": "📝",
                "IN_PROGRESS": "🔄",
                "BLOCKED": "🚧",
                "REVIEW": "👀",
                "DONE": "✅",
            }.get(status, "❓")

            progress_str = ""
            if progress["total"] > 0:
                progress_str = f" [{progress['done']}/{progress['total']}]"

            flags = ""
            if change["has_pivot"]:
                flags += " ⚡"
            if change["has_blockers"]:
                flags += " 🚧"

            console.print(f"  {status_icon} {change['name']} {status}{progress_str}{flags}")

    # Knowledge files count
    knowledge_dir = sspec_root / "knowledge"
    if knowledge_dir.exists():
        knowledge_count = len(list(knowledge_dir.glob("*.md")))
        console.print()
        console.print(f"[dim]Knowledge files: {knowledge_count}[/dim]")

    # Archived count
    archive_dir = sspec_root / "changes" / "archive"
    if archive_dir.exists():
        archived_count = len([d for d in archive_dir.iterdir() if d.is_dir()])
        console.print(f"[dim]Archived changes: {archived_count}[/dim]")

    console.print()


def _show_change_detail(change_path) -> None:
    """Show detailed status of a single change."""
    change = parse_change(change_path)

    # Read tasks.md for details
    tasks_file = change_path / "tasks.md"
    tasks_content = ""
    if tasks_file.exists():
        tasks_content = tasks_file.read_text(encoding="utf-8")

    # Read proposal.md for summary
    proposal_file = change_path / "proposal.md"
    proposal_summary = ""
    if proposal_file.exists():
        proposal_content = proposal_file.read_text(encoding="utf-8")
        # Extract first meaningful paragraph
        lines = proposal_content.split("\n")
        for line in lines:
            if line.strip() and not line.startswith("#") and not line.startswith("<!--"):
                proposal_summary = line.strip()[:100]
                break

    console.print()
    console.print(Panel(
        f"[bold]{change['name']}[/bold]\n"
        f"Status: {change['status']}\n"
        f"Progress: {change['progress']['done']}/{change['progress']['total']}\n"
        f"{proposal_summary}",
        title="Change Details",
    ))
