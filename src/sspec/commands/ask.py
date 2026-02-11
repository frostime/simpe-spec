"""sspec ask command - two-step Q&A with file-based workflow."""

from __future__ import annotations

from pathlib import Path

import click
import questionary

from sspec.core import SspecNotFoundError, get_sspec_root
from sspec.services.ask_service import (
    archive_ask,
    convert_ask_to_md,
    create_ask_template,
    execute_ask_prompt,
    extract_ask_name_from_filename,
    find_ask_matches,
    save_ask_answer,
)


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
    """Create a new ask template (.py file) for editing."""

    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    try:
        py_path, warning = create_ask_template(sspec_root=sspec_root, name=name)
    except ValueError as e:
        raise click.ClickException(str(e)) from None

    try:
        rel = py_path.relative_to(sspec_root.parent)
        rel_str = str(rel).replace('\\', '/')
    except ValueError:
        rel_str = str(py_path)

    # Show warning if name was converted
    if warning:
        click.echo(f'⚠️  {warning}', err=True)

    click.echo(f'✓ Created ask template: {rel_str}')
    click.echo('')
    click.echo('Next steps:')
    click.echo(f'  1. Edit REASON and QUESTION in {rel_str}')
    click.echo(f'  2. Run: sspec ask prompt {rel_str}')
    click.echo('  3. Agent will get user\'s answer from `sspec ask prompt`.')
    click.echo('Note:')
    click.echo('  - Simple/Complex question -> write in QUESTION fields.')
    click.echo(
        '  - Attached reusable long design/research content -> '
        'dump it in standalone file under <change>/reference and links in QUESTION.'
    )


@ask_group.command(name='prompt')
@click.argument('ask_file', type=click.Path(exists=False, path_type=Path))
def ask_prompt(ask_file: Path) -> None:
    """Execute ask prompt, collect answer, and convert to .md."""

    if ask_file.suffix != '.py':
        raise click.ClickException(f'Ask file must be .py file, got: {ask_file.suffix}')

    if not ask_file.exists():
        md_file = ask_file.with_suffix('.md')
        if md_file.exists():
            click.echo(f'✓ Ask already completed, see record file: {md_file}')
            return

    try:
        # Execute prompt and get answer
        answer = execute_ask_prompt(ask_file_path=ask_file)

        # Save answer to .py file
        save_ask_answer(ask_file_path=ask_file, answer=answer)

        # Convert to .md and cleanup .py
        md_path = convert_ask_to_md(py_path=ask_file)

        try:
            sspec_root = get_sspec_root()
            rel = md_path.relative_to(sspec_root.parent)
            rel_str = str(rel).replace('\\', '/')
        except (SspecNotFoundError, ValueError):
            rel_str = str(md_path)

        click.echo('')
        click.echo(f'✓ Ask recorded to: {rel_str}')
        click.echo('')
        click.echo('Answer:')
        click.echo(answer)

    except (FileNotFoundError, AttributeError, ImportError) as e:
        raise click.ClickException(str(e)) from None


@ask_group.command(name='list')
def ask_list() -> None:
    """List all asks (pending and completed)."""

    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    asks_dir = sspec_root / 'asks'
    if not asks_dir.exists():
        click.echo('No asks found.')
        return

    pending = sorted(asks_dir.glob('*.py'))
    completed = sorted(asks_dir.glob('*.md'))

    if not pending and not completed:
        click.echo('No asks found.')
        return

    if pending:
        click.echo('📝 Pending (unanswered):')
        for f in pending:
            click.echo(f'  {f.name}')

    if completed:
        click.echo('✅ Completed:')
        for f in completed:
            click.echo(f'  {f.name}')

    click.echo()
    click.echo(f'Total: {len(pending)} pending, {len(completed)} completed')


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

    dest_path = archive_ask(sspec_root / 'asks', ask_path)
    rel_path = dest_path.relative_to(sspec_root.parent)
    click.echo(f'Archived to: {rel_path}')
