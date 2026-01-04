"""sspec project command - project-level operations."""

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from sspec import __version__
from sspec.core import (
    SCHEMA_VERSION,
    SSPEC_DIR,
    UPDATABLE_FILES,
    USER_FILES,
    ChangeStatus,
    SspecNotFoundError,
    copy_template,
    get_sspec_root,
    get_template_dir,
    list_changes,
    render_template,
)

console = Console()


@click.group()
def project() -> None:
    """Project-level operations (init, status, update)."""
    pass


@project.command()
@click.option('--force', is_flag=True, help='Overwrite existing .sspec directory')
def init(force: bool) -> None:
    """Initialize .sspec directory in current project."""
    sspec_path = Path.cwd() / SSPEC_DIR

    if sspec_path.exists() and not force:
        raise click.ClickException(
            f'{SSPEC_DIR} already exists. Use --force to reinitialize, '
            f"or 'sspec project update' to update templates."
        )

    template_dir = get_template_dir()
    common_replacements = {'SCHEMA_VERSION': SCHEMA_VERSION, 'SCHEMA': SCHEMA_VERSION}

    # Create directory structure
    sspec_path.mkdir(parents=True, exist_ok=True)
    # Remove legacy spec folder; only create required structure
    (sspec_path / 'changes').mkdir(exist_ok=True)
    (sspec_path / 'changes' / 'archive').mkdir(exist_ok=True)
    (sspec_path / 'requests').mkdir(exist_ok=True)
    (sspec_path / 'skills').mkdir(exist_ok=True)

    # 复制 skills 模板
    skills_template_dir = template_dir / 'skills'
    if skills_template_dir.exists():
        for skill_file in skills_template_dir.glob('*.md'):
            dest_path = sspec_path / 'skills' / skill_file.name
            copy_template(skill_file, dest_path, common_replacements)

    # Initialize templates
    for file_path in [*UPDATABLE_FILES, *USER_FILES]:
        template_path = template_dir / file_path
        dest_path = sspec_path / file_path

        if not template_path.exists():
            console.print(f'[yellow]Warning: Template not found: {file_path}[/yellow]')
            continue

        dest_path.parent.mkdir(parents=True, exist_ok=True)

        copy_template(template_path, dest_path, common_replacements)

    # Create .gitignore
    gitignore_path = sspec_path / '.gitignore'
    if not gitignore_path.exists():
        gitignore_path.write_text('*', encoding='utf-8')

    # Create initial .meta.json
    meta_data = {
        'schema_version': SCHEMA_VERSION,
        'sspec_version': __version__,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'file_hashes': {},
    }

    # Compute initial hashes for updatable files
    for file_path in UPDATABLE_FILES:
        dest_path = sspec_path / file_path
        if dest_path.exists():
            content = dest_path.read_text(encoding='utf-8')
            file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
            meta_data['file_hashes'][file_path] = file_hash

    meta_path = sspec_path / '.meta.json'
    meta_path.write_text(
        json.dumps(meta_data, indent=2, ensure_ascii=False), encoding='utf-8'
    )

    # Update root AGENTS.md
    if update_root_agents_block():
        console.print('  [green]✓[/green] Created/Updated root AGENTS.md')

    rel_path = sspec_path.relative_to(Path.cwd())

    console.print()
    console.print(f'[green]✓[/green] Initialized sspec project in {rel_path}/')
    console.print()
    console.print('[cyan]Structure:[/cyan]')
    console.print('  .sspec/')
    console.print('  ├── AGENTS.md       # AI context and guidance')
    console.print('  ├── project.md      # Project overview')
    console.print('  ├── changes/        # Active change proposals')
    console.print('  ├── requests/       # Ad-hoc AI requests')
    console.print('  └── skills/         # Custom AI skills')
    console.print()
    console.print('[yellow]Next:[/yellow]')
    console.print('  1. Edit .sspec/project.md (project context)')
    console.print('  2. Create a change: sspec change new <name>')
    console.print('  3. Check status: sspec project status')


@project.command()
def status() -> None:
    """Show project overview and status."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException(
            "Not a sspec project. Run 'sspec project init' first."
        ) from None

    _show_overview(sspec_root)


def _show_overview(sspec_root: Path) -> None:
    """Show project overview."""
    changes = list_changes(sspec_root)
    active = [c for c in changes if not c['archived']]

    console.print()
    console.print('[bold]sspec Status[/bold]')
    console.print()

    if not active:
        console.print('[dim]No active changes[/dim]')
    else:
        for change in active:
            status = change.get('status', '')
            status_icon = _get_status_icon(status)
            name = change['name']

            console.print(
                f'{status_icon} [bold]{name}[/bold] [{_get_status_color(status)}]{status}[/]'
            )

            if change.get('description'):
                console.print(f'  [dim]{change["description"]}[/dim]')
            console.print()

    console.print(
        f'[dim]{len(active)} active, {len(changes) - len(active)} archived[/dim]'
    )
    console.print()


def _get_status_icon(status: str) -> str:
    """Get icon for status."""
    icons = {
        ChangeStatus.PLANNING.value: '📝',
        ChangeStatus.DOING.value: '🔄',
        ChangeStatus.BLOCKED.value: '🚧',
        ChangeStatus.REVIEW.value: '👀',
        ChangeStatus.DONE.value: '✅',
    }
    return icons.get(status, '•')


def _get_status_color(status: str) -> str:
    """Get color for status."""
    colors = {
        ChangeStatus.PLANNING.value: 'yellow',
        ChangeStatus.DOING.value: 'cyan',
        ChangeStatus.BLOCKED.value: 'red',
        ChangeStatus.REVIEW.value: 'magenta',
        ChangeStatus.DONE.value: 'green',
    }
    return colors.get(status, 'white')


META_FILE = '.meta.json'


def compute_hash(content: str) -> str:
    """Compute SHA256 hash of content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]


def compute_file_hash(path: Path) -> str | None:
    """Compute hash of file content."""
    if not path.exists():
        return None
    return compute_hash(path.read_text(encoding='utf-8'))


def load_meta(sspec_root: Path) -> dict | None:
    """Load metadata from .meta.json."""
    meta_path = sspec_root / META_FILE
    if not meta_path.exists():
        return None
    try:
        return json.loads(meta_path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return None


def save_meta(sspec_root: Path, meta: dict) -> None:
    """Save metadata to .meta.json."""
    meta_path = sspec_root / META_FILE
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8')


@project.command()
@click.option(
    '--dry-run', is_flag=True, help='Show what would be updated without making changes'
)
@click.option('--force', is_flag=True, help='Force update even if files were modified')
@click.option('--interactive', '-i', is_flag=True, help='Prompt for each file')
def update(dry_run: bool, force: bool, interactive: bool) -> None:
    """Update project templates while preserving user changes."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException(
            "Not a sspec project. Run 'sspec project init' first."
        ) from None

    template_dir = get_template_dir()
    meta = load_meta(sspec_root) or {}
    old_hashes = meta.get('file_hashes', {})

    common_replacements = {'SCHEMA_VERSION': SCHEMA_VERSION, 'SCHEMA': SCHEMA_VERSION}

    # Collect update candidates
    updates = []
    for file_path in UPDATABLE_FILES:
        is_user = False
        template_path = template_dir / file_path
        dest_path = sspec_root / file_path

        if not template_path.exists():
            continue

        # Read template content
        if template_path.suffix == '.md':
            template_content = template_path.read_text(encoding='utf-8')
            for old, new in common_replacements.items():
                template_content = template_content.replace(f'{{{{{old}}}}}', new)
        else:
            template_content = template_path.read_text(encoding='utf-8')

        new_hash = compute_hash(template_content)

        # Determine update status
        if not dest_path.exists():
            status = 'missing'
            current_hash = None
        else:
            current_hash = compute_file_hash(dest_path)
            old_hash = old_hashes.get(file_path)

            if old_hash is None:
                status = 'unknown'
            elif current_hash == new_hash:
                status = 'current'
            elif current_hash == old_hash:
                status = 'updatable'
            else:
                status = 'modified'

        updates.append(
            {
                'path': file_path,
                'is_user': is_user,
                'status': status,
                'template_path': template_path,
                'dest_path': dest_path,
                'template_content': template_content,
                'new_hash': new_hash,
                'current_hash': current_hash,
            }
        )

    # Show status table
    table = Table(title='Update Status')
    table.add_column('File', style='cyan')
    table.add_column('Status', style='yellow')
    table.add_column('Action', style='green')

    actions = []
    for upd in updates:
        status = upd['status']
        path = upd['path']

        if status == 'current':
            action = '[dim]skip[/dim]'
        elif status == 'missing':
            action = '[green]create[/green]'
            actions.append(upd)
        elif status == 'updatable':
            action = '[yellow]update[/yellow]'
            actions.append(upd)
        elif status == 'modified':
            if force:
                action = '[red]overwrite (--force)[/red]'
                actions.append(upd)
            else:
                action = '[red]skip (modified)[/red]'
        else:  # unknown
            if force:
                action = '[yellow]update (--force)[/yellow]'
                actions.append(upd)
            else:
                action = '[dim]skip (unknown)[/dim]'

        table.add_row(path, status, action)

    console.print()
    console.print(table)
    console.print()

    if not actions:
        # Check if AGENTS.md needs update
        agents_needs_update = update_root_agents_block(dry_run=True)

        if not agents_needs_update:
            console.print('[green]✓[/green] All files are up to date')
            return
    else:
        agents_needs_update = update_root_agents_block(dry_run=True)

    if dry_run:
        console.print(f'[cyan]Would update {len(actions)} file(s)[/cyan]')
        if agents_needs_update:
            console.print('[cyan]Would update root AGENTS.md block[/cyan]')
        return

    # Apply updates
    updated_count = 0
    new_hashes = old_hashes.copy()

    for upd in actions:
        path = upd['path']
        dest_path = upd['dest_path']

        if interactive:
            if not click.confirm(f'Update {path}?'):
                console.print(f'  [dim]Skipped {path}[/dim]')
                continue

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(upd['template_content'], encoding='utf-8')
        new_hashes[path] = upd['new_hash']
        updated_count += 1

        status = upd['status']
        if status == 'missing':
            console.print(f'  [green]✓[/green] Created {path}')
        else:
            console.print(f'  [green]✓[/green] Updated {path}')

    # Update metadata
    meta['file_hashes'] = new_hashes
    meta['updated_at'] = datetime.now().isoformat()
    meta['sspec_version'] = __version__
    save_meta(sspec_root, meta)

    # Update root AGENTS.md block
    if agents_needs_update:
        update_root_agents_block(dry_run=False)
        console.print('  [green]✓[/green] Updated root AGENTS.md block')

    console.print()
    console.print(
        f'[green]✓[/green] Updated {updated_count + (1 if agents_needs_update else 0)} file(s)'
    )


def update_root_agents_block(dry_run: bool = False) -> bool:
    """Update the SSPEC block in root AGENTS.md."""
    template_path = get_template_dir() / 'AGENTS.md'
    if not template_path.exists():
        return False

    root_agents = Path.cwd() / 'AGENTS.md'
    rendered = render_template(
        template_path.read_text(encoding='utf-8'),
        {'SCHEMA_VERSION': SCHEMA_VERSION, 'SCHEMA': SCHEMA_VERSION},
    )

    if not root_agents.exists():
        if not dry_run:
            root_agents.write_text(rendered, encoding='utf-8')
        return True

    content = root_agents.read_text(encoding='utf-8')

    start_marker = '<!-- SSPEC:START -->'
    end_marker = '<!-- SSPEC:END -->'

    if start_marker not in content:
        if not dry_run:
            with open(root_agents, 'a', encoding='utf-8') as f:
                f.write('\\n\\n' + rendered)
        return True

    pattern = re.compile(
        rf'{re.escape(start_marker)}.*?{re.escape(end_marker)}', re.DOTALL
    )

    new_content = pattern.sub(rendered, content)

    if new_content != content:
        if not dry_run:
            root_agents.write_text(new_content, encoding='utf-8')
        return True

    return False
