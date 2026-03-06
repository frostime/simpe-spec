"""sspec ask command - two-step Q&A with file-based workflow."""

from __future__ import annotations

from pathlib import Path

import click
import questionary
from rich.console import Console

from sspec.core import ARCHIVE_DIR, SspecNotFoundError, get_sspec_root
from sspec.services.ask_service import (archive_ask, convert_ask_to_md,
                                        create_ask_template,
                                        execute_ask_prompt,
                                        extract_ask_name_from_filename,
                                        find_ask_matches, save_ask_answer)
from sspec.services.editor_service import open_in_editor

console = Console()


@click.group(name='ask')
def ask_group() -> None:
    """Manage ask prompts for mid-execution user consultation."""
    pass


def _resolve_ask_file(asks_dir: Path, name: str, interactive: bool) -> Path:
    """Resolve an ask name to a single file path."""
    matches = find_ask_matches(asks_dir, name)
    if not matches:
        raise click.ClickException(f"Ask '{name}' not found")
    if len(matches) == 1:
        return matches[0]
    if interactive:
        return _interactive_select_ask(matches, name)

    match_lines = '\n'.join(f'  - {m.stem}' for m in matches)
    raise click.ClickException(f"Multiple matches for '{name}':\n{match_lines}")


def _interactive_select_ask(matches: list[Path], name: str) -> Path:
    """Interactive selection when multiple ask matches found."""
    choices = [questionary.Choice(title=m.stem, value=m) for m in matches]

    click.echo(f"\nMultiple matches for '{name}':")
    selected = questionary.select('Select ask:', choices=choices).ask()

    if selected is None:
        raise click.ClickException('Cancelled')
    return selected


@ask_group.command(name='create')
@click.argument('name')
def ask_create(name: str) -> None:
    """Create a new ask template (.yml file) for editing."""

    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    try:
        ask_path, warning = create_ask_template(sspec_root=sspec_root, name=name)
    except ValueError as e:
        raise click.ClickException(str(e)) from None

    try:
        rel = ask_path.relative_to(sspec_root.parent)
        rel_str = str(rel).replace('\\', '/')
    except ValueError:
        rel_str = str(ask_path)

    # Show warning if name was converted
    if warning:
        click.echo(f'WARNING: {warning}', err=True)

    click.echo(f'[OK] Created ask template: {rel_str}')
    click.echo('')
    click.echo('Next steps:')
    click.echo(f'  1. Edit reason and question in {rel_str}')
    click.echo(f'  2. Run: sspec ask prompt {rel_str}')
    click.echo("  3. Agent will get user's answer from `sspec ask prompt`.")
    click.echo('Note:')
    click.echo('  - Simple/Complex question -> write in QUESTION fields.')
    click.echo(
        '  - Attached reusable long design/research content -> '
        'dump it in standalone file under .sspec/tmp and links in QUESTION.'
    )

    open_in_editor(file_path=ask_path, sspec_root=sspec_root)


@ask_group.command(name='prompt')
@click.argument('ask_file', type=click.Path(exists=False, path_type=Path))
def ask_prompt(ask_file: Path) -> None:
    """Execute ask prompt from .yml/.py, collect answer, and convert to .md."""

    if ask_file.suffix not in {'.yml', '.py'}:
        raise click.ClickException(f'Ask file must be .yml or .py file, got: {ask_file.suffix}')

    if not ask_file.exists():
        md_file = ask_file.with_suffix('.md')
        if md_file.exists():
            click.echo(f'[OK] Ask already completed, see record file: {md_file}')
            return

    try:
        # Execute prompt and get answer
        answer = execute_ask_prompt(ask_file_path=ask_file)

        # Save answer to pending ask file
        save_ask_answer(ask_file_path=ask_file, answer=answer)

        # Convert to .md and cleanup pending ask file
        md_path = convert_ask_to_md(ask_path=ask_file)

        try:
            sspec_root = get_sspec_root()
            rel = md_path.relative_to(sspec_root.parent)
            rel_str = str(rel).replace('\\', '/')
        except (SspecNotFoundError, ValueError):
            rel_str = str(md_path)

        click.echo('')
        click.echo(f'[OK] Ask recorded to: {rel_str}')
        click.echo('')
        click.echo('Answer:')
        click.echo(answer)

    except (FileNotFoundError, AttributeError, ImportError) as e:
        raise click.ClickException(str(e)) from None


@ask_group.command(name='list')
@click.option('--all', '-a', 'include_all', is_flag=True, help='Include archived asks')
def ask_list(include_all: bool) -> None:
    """List all asks (pending and completed)."""

    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    asks_dir = sspec_root / 'asks'
    if not asks_dir.exists():
        console.print('[dim]No asks found.[/dim]')
        return

    pending_files = sorted(list(asks_dir.glob('*.yml')) + list(asks_dir.glob('*.py')))
    completed_files = sorted(asks_dir.glob('*.md'))

    archive_dir = asks_dir / ARCHIVE_DIR
    archived_files = []
    if archive_dir.exists():
        archived_files = sorted(archive_dir.glob('*.md'))

    if not pending_files and not completed_files and not archived_files:
        console.print('[dim]No asks found.[/dim]')
        return

    console.print()

    if pending_files:
        console.print('[bold]Pending Questions (unanswered)[/bold]')
        for f in pending_files:
            _display_ask(f, icon='?', color='yellow')
        console.print()

    if completed_files:
        console.print('[bold]Completed[/bold]')
        for f in completed_files:
            _display_ask(f, icon='+', color='green')
        console.print()

    if archived_files and include_all:
        console.print('[bold dim]Archived[/bold dim]')
        for f in archived_files:
            _display_ask(f, icon='A', color='dim', dim=True)
        # console.print()
    elif archived_files:
        console.print(f'[dim]Archived: {len(archived_files)} (use --all to show)[/dim]')

    console.print()
    console.print(
        f'[dim]Pending: {len(pending_files)} | '
        f'Completed: {len(completed_files)} | '
        f'Archived: {len(archived_files)}[/dim]'
    )


def _display_ask(path: Path, icon: str, color: str, dim: bool = False) -> None:
    """Display a single ask in list format."""
    name = extract_ask_name_from_filename(path.stem)
    if dim:
        name = f'[dim]{name}[/dim]'

    # Line 1: Icon Name
    console.print(f'[{color}]{icon}[/{color}] [bold]{name}[/bold]')

    # Indented Metadata
    path_rel = path.relative_to(Path.cwd())
    console.print(f'  [dim]Path:[/dim] [dim]{path_rel}[/dim]')


@ask_group.command(name='archive')
@click.argument('name', required=False)
@click.option('--yes', '-y', 'auto_yes', is_flag=True, help='Skip confirmation prompts')
def ask_archive(name: str | None, auto_yes: bool) -> None:
    """Archive completed asks.

    Without arguments, shows interactive multi-select for archivable asks.
    With name argument, archives a single ask.
    """
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    asks_dir = sspec_root / 'asks'

    if not name:
        _archive_asks_interactive(sspec_root)
        return

    ask_path = _resolve_ask_file(asks_dir, name, interactive=not auto_yes)
    _archive_single_ask(sspec_root, ask_path, auto_yes)


def _archive_asks_interactive(sspec_root: Path) -> None:
    """Interactive multi-select for archiving asks."""
    asks_dir = sspec_root / 'asks'
    active = sorted(asks_dir.glob('*.md')) if asks_dir.exists() else []

    if not active:
        click.echo('No asks to archive')
        return

    if len(active) == 1:
        ask_path = active[0]
        ask_name = extract_ask_name_from_filename(ask_path.stem)
        if questionary.confirm(f"Archive '{ask_name}'?", default=True).ask():
            _archive_single_ask(sspec_root, ask_path, auto_yes=True)
        else:
            click.echo('Cancelled')
        return

    choices = [
        questionary.Choice(
            title=f'{extract_ask_name_from_filename(p.stem)} ({p.stem})',
            value=p,
        )
        for p in active
    ]

    click.echo('')
    click.echo('Select asks to archive:')
    click.echo('(Use arrow keys, space to toggle, enter to confirm)')
    click.echo('')

    selected = questionary.checkbox('', choices=choices).ask()

    if selected is None:
        click.echo('Cancelled')
        return

    if not selected:
        click.echo('No asks selected')
        return

    archived_count = 0
    for ask_path in selected:
        try:
            _archive_single_ask(sspec_root, ask_path, auto_yes=True)
            archived_count += 1
        except Exception as e:
            click.echo(f'Failed to archive {ask_path.stem}: {e}')

    click.echo('')
    click.echo(f'Archived {archived_count}/{len(selected)} ask(s)')


def _archive_single_ask(sspec_root: Path, ask_path: Path, auto_yes: bool) -> None:
    """Archive a single ask."""
    ask_name = extract_ask_name_from_filename(ask_path.stem)

    if not auto_yes:
        if not questionary.confirm(f"Archive '{ask_name}'?", default=True).ask():
            click.echo('Cancelled')
            return

    dest_path = archive_ask(sspec_root, sspec_root / 'asks', ask_path)
    rel_path = dest_path.relative_to(sspec_root.parent)
    click.echo(f'Archived to: {rel_path}')
