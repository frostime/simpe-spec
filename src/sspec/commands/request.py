"""sspec request command - request management with subcommands."""

from pathlib import Path

import click
import questionary
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from sspec.core import (
    RequestStatus,
    SspecNotFoundError,
    get_sspec_root,
    get_template_dir,
)
from sspec.services.change_service import find_change_matches
from sspec.services.editor_service import open_in_editor
from sspec.services.request_service import (
    RequestInfo,
    archive_request,
    create_request,
    find_request_matches,
    link_request_to_change,
    list_requests,
    normalize_request_name,
    parse_request_file,
)

console = Console()


# ============================================================================
# Helpers
# ============================================================================


def _resolve_request_file(requests_dir: Path, name: str, interactive: bool) -> Path:
    """Resolve a request name to a single file path."""
    matches = find_request_matches(requests_dir, name)
    if not matches:
        raise click.ClickException(f"Request '{name}' not found")
    if len(matches) == 1:
        return matches[0]
    if interactive:
        return _interactive_select_request(matches, name)

    match_lines = '\n'.join(f'  - {m.stem}' for m in matches)
    raise click.ClickException(f"Multiple matches for '{name}':\n{match_lines}")


def _interactive_select_request(matches: list[Path], name: str) -> Path:
    """Interactive selection when multiple matches found."""
    choices = [questionary.Choice(title=m.stem, value=m) for m in matches]

    console.print(f"\n[yellow]Multiple matches for '{name}':[/yellow]")
    selected = questionary.select('Select request:', choices=choices).ask()

    if selected is None:
        raise click.ClickException('Cancelled')
    return selected


# ============================================================================
# Command group
# ============================================================================


@click.group()
def request() -> None:
    """Request management operations (new, list, show, link, archive)."""
    pass


# ============================================================================
# Subcommand: new
# ============================================================================


@request.command()
@click.argument('name')
def new(name: str) -> None:
    """Create a new request."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    normalized = normalize_request_name(name)
    if not normalized:
        raise click.ClickException('Invalid request name')

    template_path = get_template_dir() / 'requests' / 'requests.md'
    try:
        request_path = create_request(
            sspec_root=sspec_root,
            name=normalized,
            template_path=template_path,
        )
    except FileExistsError:
        raise click.ClickException(f"Request '{normalized}' already exists") from None
    except ValueError as e:
        raise click.ClickException(str(e)) from None

    console.print(f'[green]✓[/green] Created request: {normalized}')
    console.print(f'  [dim]{request_path.relative_to(sspec_root.parent)}[/dim]')
    console.print()

    if open_in_editor(file_path=request_path, sspec_root=sspec_root):
        console.print('[dim]Opened in editor[/dim]')
    else:
        console.print('[yellow]Tip:[/yellow] Set SSPEC_EDITOR in .env to auto-open')
        console.print("  Example: SSPEC_EDITOR='code {file}'")


# ============================================================================
# Subcommand: list
# ============================================================================


@request.command(name='list')
@click.option('--all', '-a', 'show_all', is_flag=True, help='Include done requests')
def list_requests_cmd(show_all: bool) -> None:
    """List all requests."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    _list_requests(sspec_root, show_all)


def _list_requests(sspec_root: Path, show_all: bool) -> None:
    """List all requests grouped by status."""
    items = list_requests(sspec_root)

    if not items:
        console.print('[dim]No requests found.[/dim]')
        console.print()
        console.print('Create one with: sspec request new <name>')
        return

    open_reqs = [r for r in items if r.status == RequestStatus.OPEN.value]
    in_progress = [r for r in items if r.status == RequestStatus.DOING.value]
    done = [r for r in items if r.status == RequestStatus.DONE.value]

    console.print()

    if open_reqs:
        console.print('[bold]Open Requests[/bold]')
        _print_request_table(open_reqs)

    if in_progress:
        console.print('[bold]In Progress[/bold]')
        _print_request_table(in_progress, show_changes=True)

    if done and show_all:
        console.print('[bold dim]Done[/bold dim]')
        _print_request_table(done, dim=True)
    elif done:
        console.print(f'[dim]Done: {len(done)} (use --all to show)[/dim]')


def _print_request_table(
    requests: list[RequestInfo],
    show_changes: bool = False,
    dim: bool = False,
) -> None:
    """Print requests as table."""
    table = Table(show_header=True, header_style='bold' if not dim else 'dim')
    table.add_column('Name')
    table.add_column('Created')
    if show_changes:
        table.add_column('Changes')
    table.add_column('Path')
    table.add_column('Summary')

    for r in sorted(requests, key=lambda x: x.created, reverse=True):
        created = r.created[:10] if r.created else ''
        name = f'[dim]{r.name}[/dim]' if dim else r.name

        row = [name, created]
        if show_changes:
            changes = r.attach_change or '-'
            row.append(changes)
        row.append(str(r.path.relative_to(Path.cwd())))
        row.append(r.tldr)

        table.add_row(*row)

    console.print(table)


# ============================================================================
# Subcommand: show
# ============================================================================


@request.command(name='show')
@click.argument('name')
def show_request(name: str) -> None:
    """Show a specific request."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    requests_dir = sspec_root / 'requests'
    request_path = _resolve_request_file(requests_dir, name, interactive=False)
    content = request_path.read_text(encoding='utf-8')

    console.print()
    console.print(
        Panel(
            Markdown(content),
            title=f'Request: {request_path.stem}',
            border_style='cyan',
        )
    )
    console.print()


# ============================================================================
# Subcommand: link
# ============================================================================


@request.command(name='link')
@click.argument('request_name')
@click.argument('change_name')
def link_request_cmd(request_name: str, change_name: str) -> None:
    """Link a request to a change."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    requests_dir = sspec_root / 'requests'
    request_path = _resolve_request_file(requests_dir, request_name, interactive=False)
    # change = find_change_matches(sspec_root / 'changes', change_name)

    try:
        link_request_to_change(
            sspec_root=sspec_root,
            request_file=request_path,
            change_name=change_name,
        )
    except FileNotFoundError as e:
        raise click.ClickException(str(e)) from None
    except ValueError as e:
        raise click.ClickException(str(e)) from None

    console.print(f'[green]✓[/green] Linked {request_path.stem} → {change_name}')


# ============================================================================
# Subcommand: archive
# ============================================================================


@request.command(name='archive')
@click.argument('name', required=False)
@click.option('--yes', '-y', 'auto_yes', is_flag=True, help='Skip confirmation prompts')
def archive_request_cmd(name: str | None, auto_yes: bool) -> None:
    """Archive requests.

    Without arguments, shows interactive multi-select for archivable requests.
    With name argument, archives single request.
    """
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    # Multi-select mode
    if not name:
        _archive_requests_interactive(sspec_root)
        return

    # Single request mode: resolve → parse → archive
    requests_dir = sspec_root / 'requests'
    request_path = _resolve_request_file(requests_dir, name, interactive=not auto_yes)
    request_info = parse_request_file(request_path)
    if not request_info:
        raise click.ClickException(f"Cannot parse request '{name}'")

    _archive_single_request(sspec_root, request_info, auto_yes)


def _archive_requests_interactive(sspec_root: Path) -> None:
    """Interactive multi-select for archiving requests."""
    items = list_requests(sspec_root)
    active = [r for r in items if not r.archived]

    if not active:
        console.print('[dim]No requests to archive[/dim]')
        return

    if len(active) == 1:
        req = active[0]
        if questionary.confirm(f"Archive '{req.name}'?", default=True).ask():
            _archive_single_request(sspec_root, req, auto_yes=True)
        else:
            console.print('[yellow]Cancelled[/yellow]')
        return

    # Multi-select: DONE/CLOSED pre-checked
    choices = [
        questionary.Choice(
            title=f"{r.name} [{r.status}] - {r.tldr[:50]}",
            value=r,
            checked=(r.status in (RequestStatus.DONE.value, RequestStatus.CLOSED.value)),
        )
        for r in active
    ]

    console.print()
    console.print('[bold]Select requests to archive:[/bold]')
    console.print('[dim](Use arrow keys, space to toggle, enter to confirm)[/dim]')
    console.print()

    selected = questionary.checkbox('', choices=choices).ask()

    if selected is None:
        console.print('[yellow]Cancelled[/yellow]')
        return

    if not selected:
        console.print('[yellow]No requests selected[/yellow]')
        return

    # Archive selected requests
    archived_count = 0
    for req in selected:
        try:
            _archive_single_request(sspec_root, req, auto_yes=True)
            archived_count += 1
        except Exception as e:
            console.print(f'[red]Failed to archive {req.name}: {e}[/red]')

    console.print()
    console.print(f'[green]✓[/green] Archived {archived_count}/{len(selected)} request(s)')


def _archive_single_request(
    sspec_root: Path,
    request_info: RequestInfo,
    auto_yes: bool,
) -> None:
    """Archive a single request."""
    name = request_info.name

    if not auto_yes:
        if not questionary.confirm(f"Archive '{name}'?", default=True).ask():
            console.print('[yellow]Cancelled[/yellow]')
            return

    dest_path = archive_request(sspec_root, request_info)
    rel_path = dest_path.relative_to(sspec_root.parent)
    console.print(f'[green]✓[/green] Archived to: {rel_path}')
