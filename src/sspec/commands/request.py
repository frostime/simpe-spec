"""sspec request command - request management with subcommands."""

import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import click
import questionary
import yaml
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from sspec.config import get_config
from sspec.core import (
    RequestStatus,
    SspecNotFoundError,
    get_sspec_root,
    get_template_dir,
    render_template,
)

console = Console()


def _extract_summary(body: str) -> str:
    """Extract summary from body as fallback."""
    for line in body.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('<!--'):
            return line[:50] + ('...' if len(line) > 50 else '')
    return ''


def get_editor_command(sspec_root: Path) -> str | None:
    """Get editor command from config, environment, or .env file."""
    config = get_config(sspec_root)
    if config.editor:
        return config.editor

    editor = os.environ.get('SSPEC_EDITOR')
    if editor:
        return editor

    env_path = Path.cwd() / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        editor = os.environ.get('SSPEC_EDITOR')
        if editor:
            return editor

    return os.environ.get('EDITOR')


def open_in_editor(file_path: Path, sspec_root: Path) -> bool:
    """Open file in editor. Returns True if editor was launched."""
    editor_cmd = get_editor_command(sspec_root)

    if not editor_cmd:
        return False

    if '{file}' in editor_cmd:
        cmd = editor_cmd.replace('{file}', str(file_path))
    else:
        cmd = f'{editor_cmd} {file_path}'

    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def normalize_name(name: str) -> str:
    """Normalize request name to kebab-case."""
    name = re.sub(r'\s+', '-', name.strip().lower())
    name = re.sub(r'[^a-z0-9\-]', '', name)
    return name


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

    requests_dir = sspec_root / 'requests'
    requests_dir.mkdir(exist_ok=True)

    name = normalize_name(name)
    if not name:
        raise click.ClickException('Invalid request name')

    now = datetime.now()
    timestamp = now.isoformat(timespec='seconds')
    timeprefix = now.strftime('%y%m%d%H%M%S')
    request_path = requests_dir / f'{timeprefix}-{name}.md'

    if request_path.exists():
        raise click.ClickException(f"Request '{name}' already exists")

    # Create file
    template_path = get_template_dir() / 'requests' / 'requests.md'
    replacements = {'TIME': timestamp, 'NAME': name}

    if template_path.exists():
        template_content = template_path.read_text(encoding='utf-8')
        content = render_template(template_content, replacements)
    else:
        content = (
            '---\n'
            f'created: {timestamp}\n'
            f'status: {RequestStatus.OPEN.value}\n'
            'attach-change: null\n'
            "tldr: ''\n"
            '---\n\n'
            f'# Request: {name}\n\n'
            '## What I Want\n\n'
            '<!-- Describe what you want to accomplish -->\n\n'
            '## Why\n\n'
            '<!-- Why is this needed? What problem does it solve? -->\n\n'
            '## Additional Context\n\n'
            '<!-- Any constraints, preferences, references -->\n\n'
        )

    request_path.write_text(content, encoding='utf-8')

    console.print(f'[green]✓[/green] Created request: {name}')
    console.print(f'  [dim]{request_path.relative_to(sspec_root.parent)}[/dim]')
    console.print()

    if open_in_editor(request_path, sspec_root):
        console.print('[dim]Opened in editor[/dim]')
    else:
        console.print('[yellow]Tip:[/yellow] Set SSPEC_EDITOR in .env to auto-open')
        console.print("  Example: SSPEC_EDITOR='code {file}'")


# ============================================================================
# Subcommand: list
# ============================================================================

@request.command(name='list')
@click.option('--all', '-a', 'show_all', is_flag=True, help='Include done requests')
def list_requests(show_all: bool) -> None:
    """List all requests."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    requests_dir = sspec_root / 'requests'
    _list_requests(requests_dir, show_all)


def _list_requests(requests_dir: Path, show_all: bool) -> None:
    """List all requests grouped by status."""
    requests = []
    for f in requests_dir.glob('*.md'):
        content = f.read_text(encoding='utf-8')

        # Parse frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    meta = yaml.safe_load(parts[1])
                    body = parts[2].strip()
                    tldr = meta.get('tldr', '')
                    if not tldr:
                        tldr = _extract_summary(body)

                    raw_status = str(meta.get('status', RequestStatus.OPEN.value)).strip().upper()
                    normalized_status = {
                        'DOING': RequestStatus.DOING.value,
                        'IN_PROGRESS': RequestStatus.DOING.value,
                        'IN-PROGRESS': RequestStatus.DOING.value,
                        'TODO': RequestStatus.OPEN.value,
                        'CLOSED': RequestStatus.DONE.value,
                    }.get(raw_status, raw_status or RequestStatus.OPEN.value)

                    requests.append({
                        'name': f.stem,
                        'status': normalized_status,
                        'created': str(meta.get('created', '')),
                        'changes': [meta.get('attach-change')] if meta.get('attach-change') else [],
                        'tldr': tldr,
                    })
                except yaml.YAMLError:
                    pass

    if not requests:
        console.print('[dim]No requests found.[/dim]')
        console.print()
        console.print('Create one with: sspec request new <name>')
        return

    open_reqs = [r for r in requests if r['status'] == RequestStatus.OPEN.value]
    in_progress = [r for r in requests if r['status'] == RequestStatus.DOING.value]
    done = [r for r in requests if r['status'] == RequestStatus.DONE.value]

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


def _print_request_table(requests: list, show_changes: bool = False, dim: bool = False) -> None:
    """Print requests as table."""
    table = Table(show_header=True, header_style='bold' if not dim else 'dim')
    table.add_column('Name')
    table.add_column('Created')
    if show_changes:
        table.add_column('Changes')
    table.add_column('Summary')

    for r in sorted(requests, key=lambda x: x['created'], reverse=True):
        created = r['created'][:10] if r['created'] else ''
        name = f"[dim]{r['name']}[/dim]" if dim else r['name']

        row = [name, created]
        if show_changes:
            changes = ', '.join(r['changes']) if r['changes'] else '-'
            row.append(changes)
        row.append(r['tldr'])

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
    _show_request(requests_dir, name)


def _find_request_file(requests_dir: Path, name: str, interactive: bool = False) -> Path:
    """Find request file by exact or fuzzy match."""
    exact_path = requests_dir / f'{name}.md'
    if exact_path.exists():
        return exact_path

    matches = list(requests_dir.glob(f'*-{name}.md'))
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        if interactive:
            return _interactive_select_request(matches, name)
        raise click.ClickException(
            f"Multiple matches for '{name}':\n" + '\n'.join(f'  - {m.stem}' for m in matches)
        )

    contains = [f for f in requests_dir.glob('*.md') if name in f.stem]
    if len(contains) == 1:
        return contains[0]
    if len(contains) > 1:
        if interactive:
            return _interactive_select_request(contains, name)
        raise click.ClickException(
            f"Multiple matches for '{name}':\n" + '\n'.join(f'  - {m.stem}' for m in contains)
        )

    raise click.ClickException(f"Request '{name}' not found")


def _interactive_select_request(matches: list[Path], name: str) -> Path:
    """Interactive selection when multiple matches found."""
    choices = [
        questionary.Choice(
            title=f"{m.stem}",
            value=m
        )
        for m in matches
    ]

    console.print()
    console.print(f"[yellow]Multiple matches for '{name}':[/yellow]")
    console.print("[dim](Use arrow keys, enter to select)[/dim]")
    console.print()

    selected = questionary.select('', choices=choices).ask()

    if selected is None:
        raise click.ClickException('Cancelled')

    return selected


def _show_request(requests_dir: Path, name: str) -> None:
    """Show a specific request."""
    request_path = _find_request_file(requests_dir, name, interactive=False)
    content = request_path.read_text(encoding='utf-8')

    console.print()
    console.print(Panel(Markdown(content), title=f'Request: {request_path.stem}', border_style='cyan'))
    console.print()


# ============================================================================
# Subcommand: link
# ============================================================================

@request.command(name='link')
@click.argument('request_name')
@click.argument('change_name')
def link_request(request_name: str, change_name: str) -> None:
    """Link a request to a change."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    requests_dir = sspec_root / 'requests'
    _link_request_to_change(requests_dir, request_name, change_name, sspec_root)


def _link_request_to_change(requests_dir: Path, request_name: str, change_name: str, sspec_root: Path) -> None:
    """Link a request to a change and update status."""
    request_path = _find_request_file(requests_dir, request_name, interactive=False)
    change_path = sspec_root / 'changes' / change_name

    if not change_path.exists():
        raise click.ClickException(f"Change '{change_name}' not found")

    content = request_path.read_text(encoding='utf-8')

    if not content.startswith('---'):
        raise click.ClickException('Request file missing front yaml')

    parts = content.split('---', 2)
    if len(parts) < 3:
        raise click.ClickException('Invalid request file format')

    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        raise click.ClickException(f'Invalid yaml: {e}') from e

    meta['attach-change'] = change_name
    meta['status'] = RequestStatus.DOING.value

    new_yaml = yaml.dump(meta, default_flow_style=False, allow_unicode=True)
    new_content = f'---\n{new_yaml}---{parts[2]}'
    request_path.write_text(new_content, encoding='utf-8')

    console.print(f'[green]✓[/green] Linked {request_path.stem} → {change_name}')


# ============================================================================
# Subcommand: archive
# ============================================================================

@request.command(name='archive')
@click.argument('name', required=False)
@click.option('--yes', '-y', 'auto_yes', is_flag=True, help='Skip confirmation prompts')
@click.option('--force', '-f', 'force_archive', is_flag=True, help='Archive all requests regardless of status')
def archive_request(name: str | None, auto_yes: bool, force_archive: bool) -> None:
    """Archive requests.

    Without arguments, shows interactive multi-select for archivable requests.
    With name argument, archives single request.
    Use --force to archive done requests.
    """
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    requests_dir = sspec_root / 'requests'

    # Single request mode
    if name:
        _archive_single_request(requests_dir, name, auto_yes, force_archive)
        return

    # Multi-select mode
    _archive_requests_interactive(requests_dir, auto_yes, force_archive)


def _archive_requests_interactive(requests_dir: Path, auto_yes: bool, force_archive: bool) -> None:
    """Interactive multi-select for archiving requests."""
    archivable = []
    for f in requests_dir.glob('*.md'):
        content = f.read_text(encoding='utf-8')
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    meta = yaml.safe_load(parts[1])
                    status = str(meta.get('status', RequestStatus.OPEN.value)).strip().upper()
                    normalized = {
                        'DOING': RequestStatus.DOING.value,
                        'IN_PROGRESS': RequestStatus.DOING.value,
                        'TODO': RequestStatus.OPEN.value,
                    }.get(status, status)

                    if force_archive:
                        # Archive all regardless of status
                        archivable.append({
                            'path': f,
                            'name': f.stem,
                            'status': normalized,
                            'tldr': meta.get('tldr', _extract_summary(parts[2]))
                        })
                    elif normalized in [RequestStatus.OPEN.value, RequestStatus.DOING.value]:
                        archivable.append({
                            'path': f,
                            'name': f.stem,
                            'status': normalized,
                            'tldr': meta.get('tldr', _extract_summary(parts[2]))
                        })
                except yaml.YAMLError:
                    pass

    if not archivable:
        console.print('[dim]No requests to archive[/dim]')
        return

    # Use questionary for multi-select
    choices = [
        questionary.Choice(
            title=f"{r['name']} [{r['status']}] - {r['tldr'][:50]}",
            value=r,
            checked=True
        )
        for r in archivable
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
        _archive_single_request(requests_dir, req['name'], auto_yes=True, force_archive=force_archive)
        archived_count += 1

    console.print()
    console.print(f'[green]✓[/green] Archived {archived_count} request(s)')


def _archive_single_request(requests_dir: Path, name: str, auto_yes: bool, force_archive: bool = False) -> None:
    """Archive a single request."""
    try:
        # Use interactive mode when not auto_yes
        request_path = _find_request_file(requests_dir, name, interactive=not auto_yes)
    except click.ClickException as e:
        raise e

    if not auto_yes:
        if not questionary.confirm(f"Archive '{name}'?", default=True).ask():
            console.print('[yellow]Cancelled[/yellow]')
            return

    # Create archive directory
    archive_dir = requests_dir / 'archive'
    archive_dir.mkdir(exist_ok=True)

    dest_path = archive_dir / request_path.name

    # Handle name conflicts
    if dest_path.exists():
        counter = 1
        stem = dest_path.stem
        while dest_path.exists():
            dest_path = archive_dir / f'{stem}_{counter}.md'
            counter += 1

    shutil.move(str(request_path), str(dest_path))

    rel_path = dest_path.relative_to(requests_dir.parent)
    console.print(f'[green]✓[/green] Archived to: {rel_path}')
