"""sspec request command."""

import os
import subprocess
from datetime import datetime
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from sspec.core import get_sspec_root

console = Console()

REQUEST_TEMPLATE = """---
created: {timestamp}
status: open
changes: []
tldr: ''
---

# Request: {name}

## What I Want

<!-- Describe what you want to accomplish -->

## Why

<!-- Why is this needed? What problem does it solve? -->

## Additional Context

<!-- Any constraints, preferences, references -->

"""


def _extract_summary(body: str) -> str:
    """Extract summary from body as fallback."""
    for line in body.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('<!--'):
            return line[:50] + ('...' if len(line) > 50 else '')
    return ''


def get_editor_command() -> str | None:
    """Get editor command from environment or .env file."""
    # Check environment first
    editor = os.environ.get('SSPEC_EDITOR')
    if editor:
        return editor

    # Try loading .env
    env_path = Path.cwd() / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        editor = os.environ.get('SSPEC_EDITOR')
        if editor:
            return editor

    # Fall back to $EDITOR
    return os.environ.get('EDITOR')


def open_in_editor(file_path: Path) -> bool:
    """Open file in editor. Returns True if editor was launched."""
    editor_cmd = get_editor_command()

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
@click.option(
    '--all', '-a', 'show_all', is_flag=True, help='Include done requests in list'
)
def request(
    name: str | None, list_requests: bool, show_name: str | None, show_all: bool
) -> None:
    """Create or manage user requests.

    Examples:
        sspec request                     # Create with timestamp name
        sspec request add-dark-mode       # Create with custom name
        sspec request --list              # List open requests
        sspec request --show <name>       # Show request content
    """
    sspec_root = get_sspec_root()
    requests_dir = sspec_root / 'requests'
    requests_dir.mkdir(exist_ok=True)

    # List mode
    if list_requests:
        _list_requests(requests_dir, show_all)
        return

    # Show mode
    if show_name:
        _show_request(requests_dir, show_name)
        return

    # Create mode
    if not name:
        name = datetime.now().strftime('%Y%m%d-%H%M%S')
    else:
        name = normalize_name(name)

    if not name:
        raise click.ClickException('Invalid request name')

    request_path = requests_dir / f'{name}.md'
    if request_path.exists():
        raise click.ClickException(f"Request '{name}' already exists")

    # Create file
    timestamp = datetime.now().isoformat(timespec='seconds')
    content = REQUEST_TEMPLATE.format(timestamp=timestamp, name=name)
    request_path.write_text(content, encoding='utf-8')

    console.print(f'[green]✓[/green] Created request: {name}')
    console.print(f'  [dim]{request_path.relative_to(sspec_root.parent)}[/dim]')
    console.print()

    # Try to open in editor
    if open_in_editor(request_path):
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

                    requests.append(
                        {
                            'name': f.stem,
                            'status': meta.get('status', 'open'),
                            'created': meta.get('created', ''),
                            'changes': meta.get('changes', []),
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

    # Group by status
    open_reqs = [r for r in requests if r['status'] == 'open']
    in_progress = [r for r in requests if r['status'] == 'in-progress']
    done = [r for r in requests if r['status'] == 'done']

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


def _print_request_table(
    requests: list, show_changes: bool = False, dim: bool = False
) -> None:
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


def _show_request(requests_dir: Path, name: str) -> None:
    """Show a specific request."""
    request_path = requests_dir / f'{name}.md'
    if not request_path.exists():
        raise click.ClickException(f"Request '{name}' not found")

    from rich.markdown import Markdown
    from rich.panel import Panel

    content = request_path.read_text(encoding='utf-8')
    console.print()
    console.print(Panel(Markdown(content), title=f'Request: {name}', border_style='cyan'))
    console.print()
