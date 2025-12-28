"""sspec init command."""

from pathlib import Path

import click
from rich.console import Console

from sspec.core import SSPEC_DIR, copy_template, find_sspec_root, get_template_dir

console = Console()


@click.command()
@click.option("--force", is_flag=True, help="Overwrite existing .sspec directory")
def init(force: bool) -> None:
    """Initialize .sspec directory in current project."""
    sspec_path = Path.cwd() / SSPEC_DIR

    if sspec_path.exists() and not force:
        raise click.ClickException(
            f"{SSPEC_DIR} already exists. Use --force to reinitialize."
        )

    template_dir = get_template_dir()

    # Create directory structure
    sspec_path.mkdir(parents=True, exist_ok=True)
    (sspec_path / "knowledge").mkdir(exist_ok=True)
    (sspec_path / "changes").mkdir(exist_ok=True)
    (sspec_path / "changes" / "archive").mkdir(exist_ok=True)
    (sspec_path / "prompts").mkdir(exist_ok=True)

    # Copy templates
    copy_template(template_dir / "AGENTS.md", sspec_path / "AGENTS.md")
    copy_template(template_dir / "handover.md", sspec_path / "handover.md")
    copy_template(
        template_dir / "knowledge" / "index.md",
        sspec_path / "knowledge" / "index.md",
    )

    # Copy prompt templates
    prompts_template = template_dir / "prompts"
    if prompts_template.exists():
        copy_template(prompts_template, sspec_path / "prompts")

    # Create .gitkeep
    (sspec_path / "changes" / "archive" / ".gitkeep").touch()

    console.print(f"[green]✓[/green] Initialized {SSPEC_DIR}")
    console.print()
    console.print("[cyan]Structure:[/cyan]")
    console.print(f"  {SSPEC_DIR}/")
    console.print("  ├── AGENTS.md           # AI instructions (entry point)")
    console.print("  ├── knowledge/")
    console.print("  │   └── index.md        # Project context")
    console.print("  ├── changes/")
    console.print("  │   └── archive/")
    console.print("  ├── prompts/            # Slash command definitions")
    console.print("  └── handover.md         # Global handover")
    console.print()
    console.print("[yellow]Next steps:[/yellow]")
    console.print("  1. Edit .sspec/knowledge/index.md with project info")
    console.print("  2. sspec new <change-name>")
    console.print('  3. Tell AI: "Read .sspec/AGENTS.md first"')
