"""sspec update command - safely update templates while preserving user changes."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from sspec import __version__
from sspec.core import (
    SCHEMA_VERSION,
    UPDATABLE_FILES,
    USER_FILES,
    SspecNotFoundError,
    copy_template,
    get_sspec_root,
    get_template_dir,
    render_template,
)

console = Console()

META_FILE = '.meta.json'


def compute_hash(content: str) -> str:
    """Compute SHA256 hash of content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]


def compute_file_hash(path: Path) -> Optional[str]:
    """Compute hash of file content."""
    if not path.exists():
        return None
    return compute_hash(path.read_text(encoding='utf-8'))


def load_meta(sspec_root: Path) -> Optional[dict]:
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


def create_initial_meta(sspec_root: Path) -> dict:
    """Create initial metadata by hashing current files."""
    files = {}
    for rel_path in UPDATABLE_FILES + USER_FILES:
        file_path = sspec_root / rel_path
        if file_path.exists():
            files[rel_path] = compute_file_hash(file_path)

    return {
        'schema_version': SCHEMA_VERSION,
        'package_version': __version__,
        'initialized_at': datetime.now().isoformat(timespec='seconds'),
        'files': files,
    }


@click.command()
@click.option('--dry-run', is_flag=True, help='Show what would be updated without making changes')
@click.option('--force', is_flag=True, help='Update even modified files (creates .backup)')
@click.option(
    '--init-meta',
    is_flag=True,
    hidden=True,
    help='Initialize metadata for existing install',
)
def update(dry_run: bool, force: bool, init_meta: bool) -> None:
    """Update sspec templates to latest version.

    Only updates files that haven't been modified by the user.
    User content (knowledge/, changes/, requests/) is never touched.
    """
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec init' first.")

    template_dir = get_template_dir()
    meta = load_meta(sspec_root)

    if meta is None:
        if init_meta:
            console.print('[yellow]Creating metadata for existing installation...[/yellow]')
            meta = create_initial_meta(sspec_root)
            save_meta(sspec_root, meta)
            console.print(f'[green]✓[/green] Created {META_FILE}')
            console.print("[dim]Run 'sspec update' again to check for updates.[/dim]")
            return
        else:
            console.print('[yellow]No metadata found.[/yellow]')
            console.print()
            console.print('This installation predates the update feature.')
            console.print('Run [cyan]sspec update --init-meta[/cyan] to initialize tracking,')
            console.print('then run [cyan]sspec update[/cyan] to update.')
            return

    current_schema = meta.get('schema_version', '0.0')

    console.print()
    console.print('[bold]sspec update[/bold]')
    console.print(f'  Current schema: {current_schema}')
    console.print(f'  Latest schema:  {SCHEMA_VERSION}')
    console.print()

    if current_schema == SCHEMA_VERSION:
        console.print('[green]✓[/green] Already at latest schema version.')
        console.print()
        console.print('[dim]Checking for minor template updates...[/dim]')

    # Analyze files
    updates = []
    conflicts = []
    new_files = []

    for rel_path in UPDATABLE_FILES:
        file_path = sspec_root / rel_path
        template_path = template_dir / rel_path

        if not template_path.exists():
            continue

        template_hash = compute_file_hash(template_path)
        current_hash = compute_file_hash(file_path)
        recorded_hash = meta.get('files', {}).get(rel_path)

        if not file_path.exists():
            new_files.append(rel_path)
        elif current_hash == template_hash:
            pass
        elif recorded_hash is None:
            conflicts.append((rel_path, 'no baseline'))
        elif current_hash == recorded_hash:
            updates.append(rel_path)
        else:
            conflicts.append((rel_path, 'user modified'))

    # Report findings
    if updates or new_files:
        console.print('[cyan]Updates available:[/cyan]')
        table = Table(show_header=True, header_style='bold')
        table.add_column('File')
        table.add_column('Action')

        for f in updates:
            table.add_row(f, '[green]update[/green]')
        for f in new_files:
            table.add_row(f, '[blue]create[/blue]')

        console.print(table)
    else:
        console.print('[dim]No updates needed for unmodified files.[/dim]')

    if conflicts:
        console.print()
        console.print('[yellow]Skipped (user modified):[/yellow]')
        for f, reason in conflicts:
            console.print(f'  [dim]•[/dim] {f}')
        if not force:
            console.print()
            console.print('[dim]Use --force to update these (creates .backup files)[/dim]')

    if dry_run:
        console.print()
        console.print('[dim]Dry run - no changes made.[/dim]')
        return

    if not updates and not new_files and not (force and conflicts):
        console.print()
        return

    # Apply updates
    console.print()
    updated_files = {}

    for rel_path in updates:
        template_path = template_dir / rel_path
        dest_path = sspec_root / rel_path
        copy_template(template_path, dest_path)
        updated_files[rel_path] = compute_file_hash(dest_path)
        console.print(f'  [green]✓[/green] Updated {rel_path}')

    for rel_path in new_files:
        template_path = template_dir / rel_path
        dest_path = sspec_root / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        copy_template(template_path, dest_path)
        updated_files[rel_path] = compute_file_hash(dest_path)
        console.print(f'  [blue]✓[/blue] Created {rel_path}')

    if force:
        for rel_path, reason in conflicts:
            template_path = template_dir / rel_path
            dest_path = sspec_root / rel_path

            if dest_path.exists():
                backup_path = dest_path.with_suffix(dest_path.suffix + '.backup')
                counter = 1
                while backup_path.exists():
                    backup_path = dest_path.with_suffix(f'{dest_path.suffix}.backup.{counter}')
                    counter += 1
                dest_path.rename(backup_path)
                console.print(f'  [yellow]→[/yellow] Backed up {rel_path}')

            copy_template(template_path, dest_path)
            updated_files[rel_path] = compute_file_hash(dest_path)
            console.print(f'  [green]✓[/green] Force updated {rel_path}')

    # Update metadata
    meta['schema_version'] = SCHEMA_VERSION
    meta['package_version'] = __version__
    meta['updated_at'] = datetime.now().isoformat(timespec='seconds')
    meta['files'].update(updated_files)
    save_meta(sspec_root, meta)

    # Update root AGENTS.md block
    if update_root_agents_block():
        console.print('  [green]✓[/green] Updated root AGENTS.md block')

    console.print()
    console.print(f'[green]✓[/green] Updated to schema {SCHEMA_VERSION}')


def update_root_agents_block() -> bool:
    """Update the SSPEC block in root AGENTS.md."""
    template_path = get_template_dir() / 'Agents.md'
    if not template_path.exists():
        return False

    root_agents = Path.cwd() / 'AGENTS.md'
    rendered = render_template(
        template_path.read_text(encoding='utf-8'), {'SCHEMA_VERSION': SCHEMA_VERSION, 'SCHEMA': SCHEMA_VERSION}
    )

    if not root_agents.exists():
        root_agents.write_text(rendered, encoding='utf-8')
        return True

    content = root_agents.read_text(encoding='utf-8')

    start_marker = '<!-- SSPEC:START -->'
    end_marker = '<!-- SSPEC:END -->'

    if start_marker not in content:
        with open(root_agents, 'a', encoding='utf-8') as f:
            f.write('\n\n' + rendered)
        return True

    import re

    pattern = re.compile(rf'{re.escape(start_marker)}.*?{re.escape(end_marker)}', re.DOTALL)

    new_content = pattern.sub(rendered, content)

    if new_content != content:
        root_agents.write_text(new_content, encoding='utf-8')
        return True

    return False
