"""sspec project command - project-level operations."""

from datetime import datetime
from pathlib import Path

import click
import questionary
from rich.console import Console
from rich.table import Table

from sspec import __version__
from sspec.core import (
    SCHEMA_VERSION,
    ChangeStatus,
    SspecNotFoundError,
    get_sspec_root,
    get_template_dir,
    list_template_skills,
)
from sspec.services.agents_service import update_root_agents_block
from sspec.services.change_service import list_changes
from sspec.services.meta_service import load_meta, save_meta
from sspec.services.project_init_service import (
    ProjectAlreadyInitializedError,
    initialize_project,
    sync_skill_locations,
)
from sspec.services.project_update_service import (
    collect_orphaned_skills,
    collect_update_candidates,
    remove_orphaned_skill,
)

console = Console()


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
        console.print('[yellow]Selection cancelled, skip external skill sync[/yellow]')
        return []

    if not selected:
        console.print('[yellow]No locations selected, skip external skill sync[/yellow]')
        return []

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

    try:
        result = initialize_project(
            project_root=project_root,
            force=force,
            skill_locations=[],
            prefer_symlink=True,
        )
    except ProjectAlreadyInitializedError as e:
        raise click.ClickException(
            f"{e} Or run 'sspec project update' to update templates."
        ) from None

    rel_path = result.sspec_path.relative_to(Path.cwd())

    console.print()
    console.print(f'[green]+[/green] Initialized sspec project in {rel_path}/')
    console.print('  [green]+[/green] Installed core skills to .sspec/skills/ (copy)')

    if result.created_or_updated_agents:
        console.print('  [green]+[/green] Created/Updated root AGENTS.md')

    # Resolve requested external locations after core init
    skill_locations = list(skill_loc) if skill_loc else _interactive_skill_selection(project_root)
    if skill_locations:
        sync_result = sync_skill_locations(
            project_root=project_root,
            locations=skill_locations,
            prefer_symlink=True,
        )

        for target_dir in sync_result.skill_targets:
            if not target_dir.exists():
                continue
            rel_target = target_dir.relative_to(project_root)
            location_key = rel_target.as_posix()
            strategy = sync_result.skill_install_strategies.get(location_key, 'copy')
            console.print(f'  [green]+[/green] Synced skills to {rel_target}/ ({strategy})')

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
    active = [c for c in changes if not c.archived]

    console.print()
    console.print('[bold]sspec Status[/bold]')
    console.print()

    if not active:
        console.print('[dim]No active changes[/dim]')
    else:
        for change in active:
            # status = change.get('status', '')
            status = change.status or ''
            status_icon = _get_status_icon(status)
            # name = change['name']
            name = change.name

            console.print(
                f'{status_icon} [bold]{name}[/bold] ' f'[{_get_status_color(status)}]{status}[/]'
            )

            # if change.get('description'):
            #     console.print(f'  [dim]{change["description"]}[/dim]')
            console.print(f'  [dim]{change.description}[/dim]')
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
    project_root = sspec_root.parent

    common_replacements = {'SCHEMA_VERSION': SCHEMA_VERSION, 'SCHEMA': SCHEMA_VERSION}

    # -----------------------------------------------------------------
    # Phase 1: Detect orphaned skills (renamed/removed from templates)
    # -----------------------------------------------------------------
    orphans = collect_orphaned_skills(project_root=project_root, meta=meta)

    if orphans:
        console.print()
        orphan_table = Table(title='Orphaned Skills (no longer in templates)')
        orphan_table.add_column('Skill', style='red')
        orphan_table.add_column('Locations', style='dim')
        for orphan in orphans:
            locs = ', '.join(str(p.relative_to(project_root)) for p in orphan.paths)
            orphan_table.add_row(orphan.skill_name, locs)
        console.print(orphan_table)

        if not dry_run:
            for orphan in orphans:
                if interactive:
                    if not questionary.confirm(
                        f'Remove orphaned skill "{orphan.skill_name}"?', default=True
                    ).ask():
                        console.print(f'  [dim]Skipped {orphan.skill_name}[/dim]')
                        continue

                count = remove_orphaned_skill(orphan)
                console.print(
                    f'  [red]-[/red] Removed orphaned skill '
                    f'"{orphan.skill_name}" ({count} location(s))'
                )

                # Clean up legacy hash entries
                for key in list(old_hashes.keys()):
                    if key.startswith(f'skills/{orphan.skill_name}'):
                        del old_hashes[key]
        else:
            console.print(f'[cyan]Would remove {len(orphans)} orphaned skill(s)[/cyan]')

    # -----------------------------------------------------------------
    # Phase 2: Collect and apply updates (existing logic, enhanced)
    # -----------------------------------------------------------------
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

    if not actions and not agents_needs_update and not orphans:
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

        # 区分 skill 和普通文件的更新
        if upd.strategy in ('symlink', 'copy'):
            # Skill 更新
            SkillInstaller._get_installer().update_skill(
                source=upd.template_path,
                target=upd.dest_path,
                strategy=upd.strategy,
            )
            skill_updated_count += 1

            # 输出信息
            if upd.status == 'missing':
                action = 'Created'
            elif upd.strategy == 'symlink':
                action = 'Updated symlink'
            else:
                action = 'Updated'
            console.print(f'  [green]+[/green] {action} {path}')
        else:
            # 普通文件更新
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_text(upd.template_content, encoding='utf-8')
            updated_count += 1

            action = 'Created' if upd.status == 'missing' else 'Updated'
            console.print(f'  [green]+[/green] {action} {path}')

        # Update hashes
        if not upd.is_symlink and upd.new_hash:
            new_hashes[upd.hash_key] = upd.new_hash

    # Update metadata
    if updated_count or skill_updated_count or orphans:
        meta['file_hashes'] = new_hashes
        meta['managed_skills'] = sorted(d.name for d in list_template_skills())
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
    if orphans:
        console.print(f'[red]-[/red] Removed {len(orphans)} orphaned skill(s)')
    console.print(f'[green]+[/green] Updated {total_updated} item(s)')
