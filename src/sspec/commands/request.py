"""sspec request command."""

import os
import subprocess
from datetime import datetime
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
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

    # Replace {file} placeholder or append file path
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
    import re

    name = re.sub(r'\s+', '-', name.strip().lower())
    name = re.sub(r'[^a-z0-9\-]', '', name)
    return name


@click.command()
@click.argument('name', required=False)
@click.option('--list', '-l', 'list_requests', is_flag=True, help='List all requests')
@click.option('--show', '-s', 'show_name', help='Show specific request')
@click.option('--link', 'link_change', help='Link request to a change')
@click.option('--all', '-a', 'show_all', is_flag=True, help='Include done requests in list')
def request(
    name: str | None,
    list_requests: bool,
    show_name: str | None,
    link_change: str | None,
    show_all: bool,
) -> None:
    """Create or manage user requests.

    Examples:
        sspec request                     # Create with timestamp name
        sspec request add-dark-mode       # Create with custom name
        sspec request --list              # List open requests
        sspec request --show <name>       # Show request content
        sspec request <name> --link <change>  # Link request to change
    """
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec init' first.") from None
    requests_dir = sspec_root / 'requests'
    requests_dir.mkdir(exist_ok=True)

    if list_requests:
        _list_requests(requests_dir, show_all)
        return

    if show_name:
        _show_request(requests_dir, show_name)
        return

    if link_change:
        if not name:
            raise click.ClickException('Request name required for --link')
        _link_request_to_change(requests_dir, name, link_change, sspec_root)
        return

    # Create mode
    if not name:
        name = datetime.now().strftime('%Y%m%d-%H%M%S')
    else:
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


def _list_requests(requests_dir: Path, show_all: bool) -> None:
    """List all requests grouped by status."""
    import yaml

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
                    # Use tldr field if available, otherwise extract from body
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

                    requests.append(
                        {
                            'name': f.stem,
                            'status': normalized_status,
                            'created': meta.get('created', ''),
                            'changes': [meta.get('attach-change')] if meta.get('attach-change') else [],
                            'tldr': tldr,
                        }
                    )
                except yaml.YAMLError:
                    pass

    if not requests:
        console.print('[dim]No requests found.[/dim]')
        console.print()
        console.print('Create one with: sspec request <name>')
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

    console.print()


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
        style = 'dim' if dim else ''

        row = [f"[{style}]{r['name']}[/{style}]", created]
        if show_changes:
            changes = ', '.join(r['changes']) if r['changes'] else '-'
            row.append(changes)
        row.append(r['tldr'])

        table.add_row(*row)

    console.print(table)


def _find_request_file(requests_dir: Path, name: str) -> Path:
    """Find request file by exact or fuzzy match."""

    exact_path = requests_dir / f'{name}.md'
    if exact_path.exists():
        return exact_path

    matches = list(requests_dir.glob(f'*-{name}.md'))
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise click.ClickException(f"Multiple matches for '{name}':\n" + '\n'.join(f'  - {m.stem}' for m in matches))

    contains = [f for f in requests_dir.glob('*.md') if name in f.stem]
    if len(contains) == 1:
        return contains[0]
    if len(contains) > 1:
        raise click.ClickException(f"Multiple matches for '{name}':\n" + '\n'.join(f'  - {m.stem}' for m in contains))

    raise click.ClickException(f"Request '{name}' not found")


def _show_request(requests_dir: Path, name: str) -> None:
    """Show a specific request."""

    request_path = _find_request_file(requests_dir, name)

    from rich.markdown import Markdown
    from rich.panel import Panel

    content = request_path.read_text(encoding='utf-8')
    console.print()
    console.print(Panel(Markdown(content), title=f'Request: {request_path.stem}', border_style='cyan'))
    console.print()


def _link_request_to_change(requests_dir: Path, request_name: str, change_name: str, sspec_root: Path) -> None:
    """Link a request to a change and update status."""

    import yaml

    request_path = _find_request_file(requests_dir, request_name)
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
