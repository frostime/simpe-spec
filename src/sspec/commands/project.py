"""sspec project command - project-level operations."""

import json
from datetime import datetime
from pathlib import Path

import click
import questionary
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
    list_template_skills,
)
from sspec.services.agents_service import update_root_agents_block
from sspec.services.meta_service import load_meta, save_meta
from sspec.services.project_init_service import (
    ProjectAlreadyInitializedError,
    get_skill_targets_from_locations,
    initialize_project,
)
from sspec.services.project_update_service import collect_update_candidates

console = Console()


DEFAULT_GITIGNORE = """
!spec-docs/**
!project.md
changes/**
requests/**
skills/**
asks/**
.meta.json
""".strip()


def _interactive_skill_selection(project_root: Path) -> list[str]:
    """Interactive skill location selection.

    Detects existing workspace directories and prompts user to select skill
    installation locations.
    """
    available_locations = ['.claude', '.github', '.agent']
    existing_dirs = [loc for loc in available_locations if (project_root / loc).is_dir()]

    console.print()
    console.print('[bold cyan]Skill Installation Location Selection[/bold cyan]')
    console.print()

    choices = [
        questionary.Choice(
            title=f"{loc} {' (existing)' if loc in existing_dirs else ''}",
            value=loc,
            checked=loc in existing_dirs,
        )
        for loc in available_locations
    ]

    selected = questionary.checkbox(
        'Select skill installation locations:',
        choices=choices,
        instruction='(Use arrow keys, space to toggle, enter to confirm)',
    ).ask()

    if selected is None:  # User cancelled
        console.print('[yellow]Selection cancelled, using default (.claude)[/yellow]')
        return ['.claude']

    if not selected:
        # If nothing selected, fallback to detected existing or .claude
        fallback = existing_dirs if existing_dirs else ['.claude']
        fallback_str = ', '.join(fallback)
        console.print(f'[yellow]No locations selected, using fallback: {fallback_str}[/yellow]')
        return fallback

    return selected


@click.group()
def project() -> None:
    """Project-level operations (init, status, update)."""
    pass


@project.command()
@click.option('--force', is_flag=True, help='Overwrite existing .sspec directory')
@click.option(
    '--skill-loc',
    multiple=True,
    type=click.Choice(['.claude', '.github', '.agent'], case_sensitive=False),
    help='Skill installation locations (can specify multiple, or use interactive mode)',
)
def init(force: bool, skill_loc: tuple[str, ...]) -> None:
    """Initialize .sspec directory in current project."""
    project_root = Path.cwd()
    # Interactive skill location selection if not specified via CLI
    skill_locations = list(skill_loc) if skill_loc else _interactive_skill_selection(project_root)

    try:
        result = initialize_project(
            project_root=project_root,
            force=force,
            skill_locations=skill_locations,
            default_gitignore=DEFAULT_GITIGNORE,
            prefer_symlink=True,
        )
    except ProjectAlreadyInitializedError as e:
        raise click.ClickException(
            f"{e} Or run 'sspec project update' to update templates."
        ) from None

    # Print skill installation locations
    template_skills = list_template_skills()
    skill_targets = get_skill_targets_from_locations(
        project_root=project_root,
        locations=skill_locations,
        sspec_dir=SSPEC_DIR,
    )

    if template_skills:
        for target_dir in skill_targets:
            if not target_dir.exists():
                continue
            rel_target = target_dir.relative_to(project_root)
            location_key = str(rel_target)
            strategy = result.skill_install_strategies.get(location_key, 'copy')
            console.print(f'  [green]+[/green] Installed skills to {rel_target}/ ({strategy})')

    if result.created_or_updated_agents:
        console.print('  [green]+[/green] Created/Updated root AGENTS.md')

    rel_path = result.sspec_path.relative_to(Path.cwd())

    console.print()
    console.print(f'[green]+[/green] Initialized sspec project in {rel_path}/')
    console.print()
    console.print('[cyan]Structure:[/cyan]')
    console.print('  .sspec/')
    console.print('  ├── project.md      # Project overview')
    console.print('  ├── spec-docs/      # Project-level specification documents')
    console.print('  ├── changes/        # Active change proposals')
    console.print('  └── requests/       # Ad-hoc AI requests')
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
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

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
                f'{status_icon} [bold]{name}[/bold] ' f'[{_get_status_color(status)}]{status}[/]'
            )

            if change.get('description'):
                console.print(f'  [dim]{change["description"]}[/dim]')
            console.print()

    console.print(f'[dim]{len(active)} active, {len(changes) - len(active)} archived[/dim]')
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


@project.command()
@click.option('--dry-run', is_flag=True, help='Show what would be updated without making changes')
@click.option('--force', is_flag=True, help='Force update even if files were modified')
@click.option('--interactive', '-i', is_flag=True, help='Prompt for each file')
def update(dry_run: bool, force: bool, interactive: bool) -> None:
    """Update project templates while preserving user changes."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    template_dir = get_template_dir()
    meta = load_meta(sspec_root)
    old_hashes = meta.get('file_hashes', {}) or {}

    common_replacements = {'SCHEMA_VERSION': SCHEMA_VERSION, 'SCHEMA': SCHEMA_VERSION}

    updates = collect_update_candidates(
        sspec_root=sspec_root,
        template_dir=template_dir,
        meta=meta,
        common_replacements=common_replacements,
    )

    # Show status table
    table = Table(title='Update Status')
    table.add_column('File', style='cyan')
    table.add_column('Status', style='yellow')
    table.add_column('Action', style='green')

    actions = []
    for upd in updates:
        status = upd.status
        path = upd.display_path

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
    agents_needs_update = update_root_agents_block(
        project_root=sspec_root.parent,
        template_agents_path=get_template_dir() / 'AGENTS.md',
        replacements={'SCHEMA_VERSION': SCHEMA_VERSION, 'SCHEMA': SCHEMA_VERSION},
        dry_run=True,
    )

    if not actions and not agents_needs_update:
        console.print('[green]+[/green] All files are up to date')
        return

    if dry_run:
        console.print(f'[cyan]Would update {len(actions)} file(s)[/cyan]')
        if agents_needs_update:
            console.print('[cyan]Would update root AGENTS.md block[/cyan]')
        return

    # Apply updates
    updated_count = 0
    skill_updated_count = 0
    new_hashes = old_hashes.copy()

    from sspec.skill_installer import SkillInstaller

    for upd in actions:
        path = upd.display_path
        dest_path = upd.dest_path

        if interactive:
            if not questionary.confirm(f'Update {path}?', default=True).ask():
                console.print(f'  [dim]Skipped {path}[/dim]')
                continue

        # Handle skills (symlink/copy) vs regular files
        if upd.strategy == 'symlink':
            SkillInstaller.update_skill(
                source_dir=upd.template_path, target_dir=upd.dest_path, strategy='symlink'
            )
            skill_updated_count += 1
            console.print(f'  [green]+[/green] Updated symlink {path}')
        elif upd.strategy == 'copy':
            SkillInstaller.update_skill(
                source_dir=upd.template_path, target_dir=upd.dest_path, strategy='copy'
            )
            skill_updated_count += 1
            if upd.status == 'missing':
                console.print(f'  [green]+[/green] Created skill {path}')
            else:
                console.print(f'  [green]+[/green] Updated skill {path}')
        else:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_text(upd.template_content, encoding='utf-8')
            updated_count += 1
            if upd.status == 'missing':
                console.print(f'  [green]+[/green] Created {path}')
            else:
                console.print(f'  [green]+[/green] Updated {path}')

        # Update hashes for non-symlink files
        if not upd.is_symlink:
            new_hashes[upd.hash_key] = upd.new_hash

    # Update metadata
    if updated_count or skill_updated_count:
        meta['file_hashes'] = new_hashes
        meta['updated_at'] = datetime.now().isoformat()
        meta['sspec_version'] = __version__
        save_meta(sspec_root, meta)

    # Update root AGENTS.md block
    if agents_needs_update:
        update_root_agents_block(
            project_root=sspec_root.parent,
            template_agents_path=get_template_dir() / 'AGENTS.md',
            replacements={'SCHEMA_VERSION': SCHEMA_VERSION, 'SCHEMA': SCHEMA_VERSION},
            dry_run=False,
        )
        console.print('  [green]+[/green] Updated root AGENTS.md block')

    console.print()
    total_updated = updated_count + skill_updated_count
    if agents_needs_update:
        total_updated += 1
    console.print(f'[green]+[/green] Updated {total_updated} item(s)')
