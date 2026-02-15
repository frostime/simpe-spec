"""sspec tmp command - temporary workspace helpers."""

from __future__ import annotations

import click
from rich.console import Console

from sspec.core import SspecNotFoundError, get_sspec_root
from sspec.services.editor_service import open_in_editor
from sspec.services.tmp_service import create_tmp_entry

console = Console()


@click.group()
def tmp() -> None:
    """Temporary workspace operations."""
    pass


@tmp.command()
@click.argument('name', required=False)
@click.option('--dir', 'is_dir', is_flag=True, help='Create a directory instead of a file')
def new(name: str | None, is_dir: bool) -> None:
    """Create a new file/dir under `.sspec/tmp`."""

    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    try:
        result = create_tmp_entry(sspec_root=sspec_root, name=name, is_dir=is_dir)
    except (ValueError, FileExistsError) as e:
        raise click.ClickException(str(e)) from None

    rel_path = result.path.relative_to(sspec_root.parent)
    kind = 'directory' if result.is_dir else 'file'

    console.print(f'[green]✓[/green] Created tmp {kind}: {rel_path}')

    if open_in_editor(file_path=result.path, sspec_root=sspec_root):
        console.print('[dim]Opened in editor[/dim]')
