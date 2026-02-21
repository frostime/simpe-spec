"""sspec change command - change management operations."""

from pathlib import Path

import click
import questionary
from rich.console import Console
from rich.panel import Panel

from sspec.core import (
    ARCHIVE_DIR,
    ChangeExistsError,
    ChangeInfo,
    ChangeNotFoundError,
    ChangeStatus,
    InvalidChangeNameError,
    SspecNotFoundError,
    get_sspec_root,
)
from sspec.services.change_service import (
    archive_change,
    create_change,
    find_change_matches,
    list_changes,
    parse_change,
    validate_change,
)

console = Console()

STATUS_STYLES: dict[str, tuple[str, str]] = {
    ChangeStatus.PLANNING.value: ('yellow', '📝'),
    ChangeStatus.DOING.value: ('cyan', '🔄'),
    ChangeStatus.BLOCKED.value: ('red', '🚧'),
    ChangeStatus.REVIEW.value: ('magenta', '👀'),
    ChangeStatus.DONE.value: ('green', '✅'),
}


def _interactive_select_change(matches: list[Path], name: str) -> Path:
    """Interactive selection when multiple change matches found."""
    choices = [questionary.Choice(title=m.name, value=m) for m in matches]
    console.print(f"\n[yellow]Multiple matches for '{name}':[/yellow]")
    selected = questionary.select('Select change:', choices=choices).ask()
    if selected is None:
        raise click.ClickException('Cancelled')
    return selected


def _parse_linked_requests(sspec_root: Path, change_info: ChangeInfo):
    """Parse linked active requests from change frontmatter references."""
    from sspec.services.request_service import parse_request_file

    references = change_info.frontmatter.get('reference', [])
    if not isinstance(references, list):
        return []

    linked_requests = []
    seen_paths: set[str] = set()

    for ref in references:
        if not isinstance(ref, dict):
            continue
        if ref.get('type') != 'request':
            continue

        source = ref.get('source')
        if not isinstance(source, str) or not source:
            continue

        request_path = Path(source)
        if not request_path.is_absolute():
            request_path = sspec_root.parent / request_path

        if not request_path.exists() or request_path.parent.name == ARCHIVE_DIR:
            continue

        resolved_str = str(request_path.resolve())
        if resolved_str in seen_paths:
            continue
        seen_paths.add(resolved_str)

        info = parse_request_file(request_path)
        if info and not info.archived:
            linked_requests.append(info)

    return linked_requests


@click.group()
def change() -> None:
    """Change management operations (new, list, archive)."""
    pass


# ============================================================================
# Subcommand: new
# ============================================================================


def _resolve_from_request(sspec_root: Path, from_value: str) -> Path:
    """Resolve --from value to a request file path.

    Accepts:
    - Request name (fuzzy matched): "a", "my-feature"
    - File path (absolute or relative): ".sspec/requests/26-02-05_a.md"
    """
    from sspec.services.request_service import find_request_matches

    # Try as direct file path first
    as_path = Path(from_value)
    if as_path.exists() and as_path.suffix == '.md':
        return as_path.resolve()

    # Try relative to sspec_root
    relative_path = sspec_root / from_value
    if relative_path.exists() and relative_path.suffix == '.md':
        return relative_path

    # Fuzzy match by name
    requests_dir = sspec_root / 'requests'
    matches = find_request_matches(requests_dir, from_value)

    if not matches:
        raise click.ClickException(f"Request '{from_value}' not found")

    if len(matches) == 1:
        return matches[0]

    # Multiple matches: interactive select
    choices = [questionary.Choice(title=m.stem, value=m) for m in matches]
    console.print(f"\n[yellow]Multiple requests match '{from_value}':[/yellow]")
    selected = questionary.select('Select request:', choices=choices).ask()
    if selected is None:
        raise click.ClickException('Cancelled')
    return selected


@change.command()
@click.argument('name', required=False)
@click.option('--from', 'from_request', help='Link to existing request (name or path)')
@click.option(
    '--root', is_flag=True, default=False, help='Create root change for multi-change'
)
def new(
    name: str | None = None, from_request: str | None = None, root: bool = False
) -> None:
    """Create a new change proposal (spec, tasks, handover).

    NAME is optional when --from is provided; the change name will be
    derived from the request name.
    """
    if not name and not from_request:
        raise click.ClickException(
            'Provide a change name or use --from <request>.\n'
            '  sspec change new my-feature\n'
            '  sspec change new --from my-request\n'
            '  sspec change new my-feature --from my-request'
        )

    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException(
            "Not a sspec project. Run 'sspec project init' first."
        ) from None

    # Resolve --from request
    request_file: Path | None = None
    if from_request:
        request_file = _resolve_from_request(sspec_root, from_request)

        # Derive change name from request if not provided
        if not name:
            from sspec.services.request_service import parse_request_file

            req_info = parse_request_file(request_file)
            name = req_info.name if req_info else request_file.stem

    assert name is not None  # guaranteed by the check above

    try:
        change_path = create_change(sspec_root, name, is_root=root)
    except (InvalidChangeNameError, ChangeExistsError) as e:
        raise click.ClickException(str(e)) from e

    # Link to request if --from was specified
    if request_file:
        from sspec.services.request_service import link_request_to_change

        try:
            link_request_to_change(
                sspec_root=sspec_root, request_file=request_file, change_path=change_path
            )
            console.print(f'[green]✓[/green] Linked to request: {request_file.stem}')
        except Exception as e:
            console.print(f'[yellow]Warning:[/yellow] Failed to link request: {e}')

    rel_path = change_path.relative_to(sspec_root.parent)
    change_type = 'root' if root else 'single'

    console.print(
        f'[green]✓[/green] Created {change_type} change: [bold]{change_path.name}[/bold]'
    )
    console.print()
    console.print('[cyan]Files:[/cyan]')
    console.print(f'  {rel_path}/')
    console.print('  ├── spec.md      # Proposal and context')
    console.print('  ├── tasks.md     # Executable tasks and progress')
    console.print('  ├── handover.md  # Session continuity (update every session!)')
    console.print(
        '  └── reference/   # Use if need to keep auxiliary design/research files'
    )
    console.print()
    console.print('[yellow]Next:[/yellow]')
    console.print('  0. Read sspec-change skill (if not yet) for standards and best practices')
    console.print('  1. Read spec.md / tasks.md, follow templates format and @RULE Hints')
    console.print('  2. Fill spec.md/tasks.md, run `sspec ask create` for validation')
    console.print('  3. Update handover.md at end of each session (Consult sspec-memory skill)')


# ============================================================================
# Subcommand: list
# ============================================================================


@change.command(name='list')
@click.option('--all', 'include_all', is_flag=True, help='Include archived changes')
def list_changes_cmd(include_all: bool = False) -> None:
    """List all changes."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException(
            "Not a sspec project. Run 'sspec project init' first."
        ) from None

    _list_changes(sspec_root, include_all)


def _list_changes(sspec_root: Path, include_all: bool) -> None:
    """List changes."""
    changes = list_changes(sspec_root, include_archived=include_all)

    if not changes:
        console.print('[dim]No changes found.[/dim]')
        console.print()
        console.print('Create one with: sspec change new <change-name>')
        return

    active = [c for c in changes if not c.archived]
    archived = [c for c in changes if c.archived]

    if active:
        console.print()
        console.print('[bold]Active Changes[/bold]')
        _print_changes_list(active)

    if archived and include_all:
        console.print()
        console.print('[bold dim]Archived[/bold dim]')
        _print_changes_list(archived, dim=True)
    elif archived:
        console.print(f'[dim]Archived: {len(archived)} (use --all to show)[/dim]')

    console.print()
    console.print(f'[dim]Active: {len(active)} | Archived: {len(archived)}[/dim]')


def _display_change(
    change: ChangeInfo, dim: bool = False, in_detail: bool = False
) -> None:
    """Display a single change in list format."""
    status = change.status
    color, icon = STATUS_STYLES.get(status, ('dim', '❓'))
    if dim:
        color = 'dim'

    progress = change.progress
    progress_str = (
        f'{progress["done"]}/{progress["total"]}' if progress['total'] > 0 else '0/0'
    )

    # Line 1: Icon Name
    name_line = f'[{color}]{icon} [bold]{change.name}[/bold] [{change.status}][/{color}]'
    console.print(name_line)

    # Indented Metadata
    path_rel = change.path.relative_to(Path.cwd())
    console.print(f'  [dim]Change/Spec:[/dim] [dim]{path_rel / "spec.md"}[/dim]')
    console.print(f'  [dim]Change/Handover:[/dim] [dim]{path_rel / "handover.md"}[/dim]')
    if change.type:
        console.print(f'  [dim]Type:[/dim] [dim]{change.type}[/dim]')
    console.print(f'  [dim]Progress:[/dim] {progress_str}')
    console.print(f'  [dim]Archived:[/dim] {change.archived}')
    if in_detail and change.description:
        desc = (
            change.description
            if change.description.__len__() <= 100
            else change.description[:97] + '...'
        )
        console.print(f'  [dim]Description:[/dim] {desc}')
    if (
        (reference := change.frontmatter.get('reference', None))
        and isinstance(reference, list)
        and len(reference) > 0
    ):
        reqeust = list(filter(
            lambda x: (rt := x.get('type', None)) and rt == 'request', reference
        ))
        if len(reqeust) == 1:
            console.print(f'  [dim]Linked Requests:[/dim] {reqeust[0]["source"]}')
        elif len(reqeust) > 1:
            console.print(f'  [dim]Linked Requests:[/dim] {len(reqeust)} requests')

    flags = []
    # if change.has_pivot:
    #     flags.append('⚡pivot')
    if change.has_blockers:
        flags.append('🚧blocked')

    if flags:
        flag_str = f' [yellow]{" ".join(flags)}[/yellow]'
        console.print(f'  [dim]Flags:[/dim]{flag_str}')


def _print_changes_list(changes: list[ChangeInfo], dim: bool = False) -> None:
    """Print changes as a list."""
    for change in sorted(changes, key=lambda x: x.name):
        _display_change(change, dim=dim)
        console.print()


# ============================================================================
# Subcommand: status
# ============================================================================


# @change.command()
# @click.argument('name', required=False)
# def status(name: str | None = None) -> None:
#     """Show detailed status of a change."""
#     try:
#         sspec_root = get_sspec_root()
#     except SspecNotFoundError:
#         raise click.ClickException(
#             "Not a sspec project. Run 'sspec project init' first."
#         ) from None

#     if not name:
#         _list_changes(sspec_root, include_all=False)
#         return

#     # Fuzzy lookup
#     changes_dir = sspec_root / 'changes'
#     matches = find_change_matches(changes_dir, name)

#     if not matches:
#         raise click.ClickException(f"Change '{name}' not found")

#     if len(matches) > 1:
#         change_path = _interactive_select_change(matches, name)
#     else:
#         change_path = matches[0]

#     _show_change_detail(change_path)


def _show_change_detail(change_path: Path) -> None:
    """Show detailed status of a single change."""
    from sspec.libs.md_yaml import parse_frontmatter

    change = parse_change(change_path)

    spec_file = change_path / 'spec.md'
    summary = ''
    status = 'PLANNING'

    if spec_file.exists():
        content = spec_file.read_text(encoding='utf-8')
        meta, body = parse_frontmatter(content)
        status = meta.get('status', 'PLANNING')
        in_why = False
        for line in body.split('\n'):
            if line.startswith('## A.'):
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
            f'[bold]{change.name}[/bold]\n'
            f'Status: {change.status}\n'
            f'Progress: {change.progress["done"]}/{change.progress["total"]}\n'
            f'{summary}',
            title='Change Details',
        )
    )

    if status == 'PLANNING':
        console.print(
            '\n[dim]Next: Fill spec.md sections A/B/C, then transition to DOING[/dim]'
        )
    elif status == 'DOING':
        console.print(
            "\n[dim]Next: Continue tasks. Run 'sspec change status' for progress[/dim]"
        )
    elif status == 'REVIEW':
        console.print(
            '\n[dim]Next: Awaiting user review. After approval → DONE → archive[/dim]'
        )


@change.command()
@click.argument('query')
def find(query: str) -> None:
    """Find changes by name (fuzzy matching)."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException(
            "Not a sspec project. Run 'sspec project init' first."
        ) from None

    changes_dir = sspec_root / 'changes'
    matches = find_change_matches(changes_dir, query, include_archived=True)

    if not matches:
        console.print(f"[yellow]No changes found matching '{query}'[/yellow]")
        return

    # Exact match check
    # exact_match = next((m for m in matches if m.name.lower() == query.lower()), None)

    if len(matches) > 1:
        console.print(f'[cyan]Found {len(matches)} matches for "{query}":[/cyan]\n')
    else:
        console.print(f'[cyan]Match for "{query}":[/cyan]\n')

    for match_path in matches:
        is_archived = match_path.parent.name == ARCHIVE_DIR
        change_info = parse_change(match_path, archived=is_archived)
        _display_change(change_info, dim=is_archived, in_detail=True)
        console.print()


# ============================================================================
# Subcommand: archive
# ============================================================================


@change.command()
@click.argument('name', required=False)
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@click.option(
    '--with-request',
    is_flag=True,
    help='Archive linked request(s) together when archiving change(s)',
)
def archive(name: str | None, yes: bool, with_request: bool) -> None:
    """Archive a completed change.

    Without arguments, shows interactive multi-select for archivable changes.
    With name argument, archives single change.
    """
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException(
            "Not a sspec project. Run 'sspec project init' first."
        ) from None

    # Multi-select mode
    if not name:
        _archive_changes_interactive(sspec_root, with_request=with_request)
        return

    # Single change mode: fuzzy lookup → parse → archive
    changes_dir = sspec_root / 'changes'
    matches = find_change_matches(changes_dir, name)

    if not matches:
        raise click.ClickException(f"Change '{name}' not found")

    if len(matches) > 1:
        change_path = _interactive_select_change(matches, name)
    else:
        change_path = matches[0]

    change_info = parse_change(change_path)
    _archive_single_change(
        sspec_root,
        change_info,
        yes,
        with_request=with_request,
    )


def _archive_changes_interactive(sspec_root: Path, with_request: bool = False) -> None:
    """Interactive multi-select for archiving changes."""
    changes = list_changes(sspec_root)
    active = [c for c in changes if not c.archived]

    if not active:
        raise click.ClickException('No active changes to archive')

    if len(active) == 1:
        change_info = active[0]
        if questionary.confirm(f"Archive '{change_info.name}'?", default=True).ask():
            _archive_single_change(
                sspec_root,
                change_info,
                yes=True,
                with_request=with_request,
            )
        else:
            console.print('[yellow]Cancelled[/yellow]')
        return

    # Multi-select: DONE/CLOSED pre-checked
    choices = [
        questionary.Choice(
            title=f'{c.name} [{c.status}] - {c.progress["done"]}/{c.progress["total"]} tasks',
            value=c,
            checked=(c.status in (ChangeStatus.DONE.value, ChangeStatus.CLOSED.value)),
        )
        for c in active
    ]

    console.print()
    console.print('[bold]Select changes to archive:[/bold]')
    console.print('[dim](Use arrow keys, space to toggle, enter to confirm)[/dim]')
    console.print()

    selected = questionary.checkbox('', choices=choices).ask()

    if selected is None:
        console.print('[yellow]Cancelled[/yellow]')
        return

    if not selected:
        console.print('[yellow]No changes selected[/yellow]')
        return

    archived_count = 0
    for change_info in selected:
        try:
            _archive_single_change(
                sspec_root,
                change_info,
                yes=True,
                with_request=with_request,
            )
            archived_count += 1
        except Exception as e:
            console.print(f'[red]Failed to archive {change_info.name}: {e}[/red]')

    console.print()
    console.print(f'[green]✓[/green] Archived {archived_count}/{len(selected)} change(s)')


def _archive_single_change(
    sspec_root: Path,
    change_info: ChangeInfo,
    yes: bool,
    with_request: bool = False,
) -> None:
    """Archive a single change."""
    name = change_info.path.name
    linked_requests = _parse_linked_requests(sspec_root, change_info) if with_request else []

    if not yes:
        if not questionary.confirm(f"Archive '{name}'?", default=True).ask():
            console.print('[yellow]Cancelled[/yellow]')
            return

    try:
        archive_path = archive_change(sspec_root, change_info)
        rel_path = archive_path.relative_to(sspec_root.parent)
        console.print(f'[green]+[/green] Archived to: {rel_path}')

        if linked_requests:
            from sspec.services.request_service import archive_request

            for request_info in linked_requests:
                try:
                    request_archive_path = archive_request(sspec_root, request_info)
                    request_rel_path = request_archive_path.relative_to(sspec_root.parent)
                    console.print(
                        f'[green]+[/green] Archived linked request: '
                        f'{request_info.name} → {request_rel_path}'
                    )
                except Exception as e:
                    console.print(
                        f'[yellow]Warning:[/yellow] Failed to archive linked request '
                        f'{request_info.name}: {e}'
                    )
    except ChangeNotFoundError as e:
        raise click.ClickException(str(e)) from e
    except ValueError as e:
        raise click.ClickException(str(e)) from e


# ============================================================================
# Subcommand: validate
# ============================================================================


@change.command()
@click.argument('name')
def validate(name: str) -> None:
    """Validate a change's structure and content quality."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException(
            "Not a sspec project. Run 'sspec project init' first."
        ) from None

    changes_dir = sspec_root / 'changes'
    matches = find_change_matches(changes_dir, name)

    if not matches:
        raise click.ClickException(f"Change '{name}' not found")

    if len(matches) > 1:
        change_path = _interactive_select_change(matches, name)
    else:
        change_path = matches[0]

    issues = validate_change(change_path)

    if not issues:
        console.print(
            f'[green]✓[/green] Change [bold]{change_path.name}[/bold] looks good!'
        )
    else:
        console.print(
            f'[yellow]⚠[/yellow] Change [bold]{change_path.name}[/bold] has {len(issues)} issue(s):'
        )
        console.print()
        for issue in issues:
            console.print(f'  [yellow]•[/yellow] {issue}')
        console.print()
        console.print('[dim]Fix issues above, then run validate again.[/dim]')
