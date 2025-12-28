"""sspec prompt command - show slash command content."""

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from sspec.core import get_sspec_root

console = Console()


@click.command()
@click.argument("command", required=False)
@click.option("--list", "-l", "list_prompts", is_flag=True, help="List available prompts")
@click.option("--raw", is_flag=True, help="Output raw content without formatting")
def prompt(command: str, list_prompts: bool, raw: bool) -> None:
    """Show or list slash command prompts.

    Examples:
        sspec prompt --list
        sspec prompt handover
        sspec prompt pivot --raw
    """
    sspec_root = get_sspec_root()
    prompts_dir = sspec_root / "prompts"

    if not prompts_dir.exists():
        raise click.ClickException("No prompts directory found. Run 'sspec init' again.")

    if list_prompts or not command:
        # List available prompts
        prompts = list(prompts_dir.glob("*.md"))
        if not prompts:
            console.print("[dim]No prompts defined.[/dim]")
            return

        console.print()
        console.print("[bold]Available Slash Commands[/bold]")
        console.print()
        for p in sorted(prompts):
            name = p.stem
            # Try to get description from first line
            content = p.read_text(encoding="utf-8")
            desc = ""
            for line in content.split("\n"):
                if line.strip() and not line.startswith("#") and not line.startswith("<!--"):
                    desc = line.strip()[:60]
                    if len(line.strip()) > 60:
                        desc += "..."
                    break
            console.print(f"  /{name:<15} {desc}")
        console.print()
        return

    # Show specific prompt
    prompt_file = prompts_dir / f"{command}.md"
    if not prompt_file.exists():
        raise click.ClickException(
            f"Prompt '{command}' not found. Use 'sspec prompt --list' to see available prompts."
        )

    content = prompt_file.read_text(encoding="utf-8")

    if raw:
        click.echo(content)
    else:
        console.print()
        console.print(
            Panel(
                Markdown(content),
                title=f"/{command}",
                border_style="cyan",
            )
        )
        console.print()
        console.print("[dim]Use --raw to copy this prompt[/dim]")
