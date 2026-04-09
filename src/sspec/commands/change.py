"""sspec change command - change management operations."""

import sys
from pathlib import Path

import click
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

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
    scaffold_change_file,
    summarize_change,
    validate_change,
)

console = Console()

STATUS_STYLES: dict[str, tuple[str, str]] = {
    ChangeStatus.PLANNING.value: ('yellow', 'P'),
    ChangeStatus.DOING.value: ('cyan', 'W'),
    ChangeStatus.BLOCKED.value: ('red', 'B'),
    ChangeStatus.REVIEW.value: ('magenta', 'R'),
    ChangeStatus.DONE.value: ('green', 'D'),
}


def _change_tree_prefixes() -> tuple[str, str]:
    """Pick file tree prefixes compatible with current stdout encoding."""
    encoding = (getattr(sys.stdout, 'encoding', None) or '').lower()
    if encoding.startswith('utf'):
        return ('├──', '└──')
    return ('|--', '`--')


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


def _parse_scaffold_option(value: tuple[str, ...]) -> list[str]:
    """Parse --scaffold values: supports comma-separated and repeated flags."""
    result: list[str] = []
    for v in value:
        result.extend(part.strip() for part in v.split(',') if part.strip())
    return result


@change.command()
@click.argument('name', required=False)
@click.option('--from', 'from_request', help='Link to existing request (name or path)')
@click.option('--root', is_flag=True, default=False, help='Create root change for multi-change')
@click.option(
    '--scaffold',
    multiple=True,
    help='Additional files to scaffold (for example: design, revision). '
    'Comma-separated or repeated.',
)
def new(
    name: str | None = None,
    from_request: str | None = None,
    root: bool = False,
    scaffold: tuple[str, ...] = (),
) -> None:
    """Create a new change proposal.

    Creates spec.md + tasks.md + memory.md by default. Use --scaffold to add
    design/revision files as needed.

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
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

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

    scaffold_list = _parse_scaffold_option(scaffold)

    try:
        change_path = create_change(sspec_root, name, is_root=root, scaffold=scaffold_list)
    except (InvalidChangeNameError, ChangeExistsError) as e:
        raise click.ClickException(str(e)) from e

    # Link to request if --from was specified
    if request_file:
        from sspec.services.request_service import link_request_to_change

        try:
            link_request_to_change(
                sspec_root=sspec_root, request_file=request_file, change_path=change_path
            )
            console.print(f'[green][OK][/green] Linked to request: {request_file.stem}')
        except Exception as e:
            console.print(f'[yellow]Warning:[/yellow] Failed to link request: {e}')

    rel_path = change_path.relative_to(sspec_root.parent)
    change_type = 'root' if root else 'single'

    console.print(
        f'[green][OK][/green] Created {change_type} change: [bold]{change_path.name}[/bold]'
    )
    console.print()
    branch_prefix, last_prefix = _change_tree_prefixes()
    console.print('[cyan]Files:[/cyan]')
    console.print(f'  {rel_path}/')
    console.print(f'  {branch_prefix} spec.md      # Change definition')
    console.print(f'  {branch_prefix} tasks.md     # Execution plan')
    console.print(f'  {branch_prefix} memory.md    # Scoped memory')
    # Show scaffolded files (skip base files already shown above)
    extra_files = []
    for s in scaffold_list:
        if s == 'tasks':
            pass  # already shown as base file
        elif s == 'design':
            extra_files.append('design.md    # Technical design')
        elif s == 'revision':
            extra_files.append('revisions/   # Design amendments')
    for _i, ef in enumerate(extra_files):
        console.print(f'  {branch_prefix} {ef}')
    console.print(f'  {last_prefix} reference/   # Auxiliary files')
    console.print()
    console.print('[yellow]Next:[/yellow]')
    console.print('  1. Read sspec-design skill')
    console.print('  2. Fill spec.md, then @align with the user before implementation')
    console.print('  3. Use `sspec change scaffold` to add design/revision files when needed')


# ============================================================================
# Subcommand: scaffold
# ============================================================================


@change.command()
@click.argument('file_type', type=click.Choice(['spec', 'tasks', 'design', 'revision']))
@click.argument('name')
@click.option('--title', help='Title for revision file (required for revision type)')
def scaffold(file_type: str, name: str, title: str | None = None) -> None:
    """Scaffold a file into an existing change.

    FILE_TYPE: spec | tasks | design | revision
    NAME: change name (fuzzy matched)
    """
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException('Not a sspec project.') from None

    changes_dir = sspec_root / 'changes'
    matches = find_change_matches(changes_dir, name)

    if not matches:
        raise click.ClickException(f"Change '{name}' not found")

    if len(matches) > 1:
        change_path = _interactive_select_change(matches, name)
    else:
        change_path = matches[0]

    if file_type == 'revision' and not title:
        title = click.prompt('Revision title')

    try:
        created = scaffold_change_file(sspec_root, change_path, file_type, title=title)
        rel = created.relative_to(sspec_root.parent)
        console.print(f'[green][OK][/green] Scaffolded: {rel}')
    except ChangeExistsError as e:
        raise click.ClickException(str(e)) from e
    except InvalidChangeNameError as e:
        raise click.ClickException(str(e)) from e


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
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    _list_changes(sspec_root, include_all)


def _list_changes(sspec_root: Path, include_all: bool) -> None:
    """List changes."""
    changes = list_changes(sspec_root, include_archived=include_all)
    archived_total = len(list_changes(sspec_root, include_archived=True)) - len(
        list_changes(sspec_root, include_archived=False)
    )

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
    elif archived_total:
        console.print(f'[dim]Archived: {archived_total} (use --all to show)[/dim]')

    console.print()
    console.print(f'[dim]Active: {len(active)} | Archived: {archived_total}[/dim]')


def _display_change(change: ChangeInfo, dim: bool = False, in_detail: bool = False) -> None:
    """Display a single change in list format."""
    status = change.status
    color, icon = STATUS_STYLES.get(status, ('dim', '?'))
    if dim:
        color = 'dim'

    progress = change.progress
    progress_str = f'{progress["done"]}/{progress["total"]}' if progress['total'] > 0 else '0/0'

    # Line 1: Icon Name
    name_line = f'[{color}]{icon} [bold]{change.name}[/bold] [{change.status}][/{color}]'
    console.print(name_line)

    # Indented Metadata
    path_rel = change.path.relative_to(Path.cwd())
    console.print(f'  [dim]Change/Spec:[/dim] [dim]{path_rel / "spec.md"}[/dim]')
    console.print(f'  [dim]Change/Memory:[/dim] [dim]{path_rel / "memory.md"}[/dim]')
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
        reqeust = list(filter(lambda x: (rt := x.get('type', None)) and rt == 'request', reference))
        if len(reqeust) == 1:
            console.print(f'  [dim]Linked Requests:[/dim] {reqeust[0]["source"]}')
        elif len(reqeust) > 1:
            console.print(f'  [dim]Linked Requests:[/dim] {len(reqeust)} requests')

    flags = []
    if change.has_blockers:
        flags.append('blocked')

    if flags:
        flag_str = f' [yellow]{" ".join(flags)}[/yellow]'
        console.print(f'  [dim]Flags:[/dim]{flag_str}')


def _print_changes_list(changes: list[ChangeInfo], dim: bool = False) -> None:
    """Print changes as a list."""
    for change in changes:
        _display_change(change, dim=dim)
        console.print()


# ============================================================================
# Subcommand: status
# ============================================================================


@change.command()
@click.argument('name')
def status(name: str) -> None:
    """Show a local dashboard summary for one change."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    changes_dir = sspec_root / 'changes'
    matches = find_change_matches(changes_dir, name)

    if not matches:
        raise click.ClickException(f"Change '{name}' not found")

    change_path = _interactive_select_change(matches, name) if len(matches) > 1 else matches[0]
    _show_change_detail(change_path)


def _show_change_detail(change_path: Path) -> None:
    """Show detailed status of a single change."""
    summary = summarize_change(change_path, cwd=Path.cwd())
    color, _ = STATUS_STYLES.get(summary.status, ('white', '?'))

    console.print()
    console.print(
        Panel(
            f'[bold]{summary.name}[/bold]\n'
            f'Status: [{color}]{summary.status}[/]\n'
            f'Progress: {summary.tasks_done}/{summary.tasks_total}\n'
            f'Updated: {summary.updated or "(not set)"}',
            title='Change Status',
        )
    )

    console.print(f'[dim]Change:[/dim] {summary.path}')
    if summary.change_type:
        console.print(f'[dim]Change Type:[/dim] {summary.change_type}')

    if summary.linked_requests:
        console.print('[dim]Linked Requests:[/dim]')
        for request_path in summary.linked_requests:
            console.print(f'  - {request_path}')

    console.print('[dim]Source Files:[/dim]')
    for label, path in summary.source_links.items():
        console.print(f'  - {label}: {path}')

    console.print()
    if summary.memory_exists:
        console.print('[bold]Current State[/bold]')
        if summary.state_lines:
            for line in summary.state_lines:
                console.print(f'- {line}')
        else:
            console.print('[dim]not recorded[/dim]')

        console.print()
        console.print('[bold]Latest Milestone[/bold]')
        if summary.latest_milestone:
            console.print(f'- {summary.latest_milestone}')
        else:
            console.print('[dim]not recorded[/dim]')

        if summary.coordination_rows:
            table = Table(title='Coordination')
            table.add_column('Phase')
            table.add_column('Sub-Change')
            table.add_column('Status')
            table.add_column('Blocker')
            for row in summary.coordination_rows:
                table.add_row(
                    row.get('Phase', ''),
                    row.get('Sub-Change', ''),
                    row.get('Status', ''),
                    row.get('Blocker', ''),
                )
            console.print()
            console.print(table)
    else:
        console.print('[bold]Memory[/bold]')
        console.print('[yellow]unsupported or missing (`memory.md` not found)[/yellow]')
        console.print()
        console.print('[bold]Current State[/bold]')
        console.print('[dim]not recorded[/dim]')
        console.print()
        console.print('[bold]Latest Milestone[/bold]')
        console.print('[dim]not recorded[/dim]')


@change.command()
@click.argument('query')
def find(query: str) -> None:
    """Find changes by name (fuzzy matching)."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

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
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

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
    console.print(f'[green][OK][/green] Archived {archived_count}/{len(selected)} change(s)')


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
                        f'{request_info.name} -> {request_rel_path}'
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
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

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
        console.print(f'[green][OK][/green] Change [bold]{change_path.name}[/bold] looks good!')
    else:
        console.print(
            f'[yellow][WARN][/yellow] Change [bold]{change_path.name}[/bold] '
            f'has {len(issues)} issue(s):'
        )
        console.print()
        for issue in issues:
            console.print(f'  [yellow]-[/yellow] {issue}')
        console.print()
        console.print('[dim]Fix issues above, then run validate again.[/dim]')
