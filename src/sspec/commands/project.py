"""sspec project command - project-level operations."""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

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
from sspec.services.meta_service import META_SCHEMA, save_meta
from sspec.services.project_init_service import (
    ProjectAlreadyInitializedError,
    initialize_project,
    sync_skill_locations,
)
from sspec.services.project_update_service import (
    MetaMigrationError,
    apply_skill_update,
    collect_orphaned_skills,
    collect_update_candidates,
    migrate_legacy_skill_layouts,
    prepare_meta_for_project_update,
    recover_missing_skill_locations,
    remove_orphaned_skill,
    sync_hub_skills_gitignore,
)

console = Console()


def _validate_skill_locations(project_root: Path, locations: list[str]) -> list[str]:
    """Validate skill locations as safe, project-relative directories."""

    root = project_root.resolve()
    out: list[str] = []
    seen: set[str] = set()

    for raw in locations:
        loc = (raw or '').strip()
        if not loc:
            continue

        p = Path(loc)

        # Allow users to pass a full ".../skills" path; normalize it back to the location dir.
        if p.name == 'skills':
            p = p.parent

        if p.as_posix() in {'.', ''}:
            raise click.ClickException('Skill location must not be the project root')

        if p.is_absolute() or getattr(p, 'drive', '') or getattr(p, 'root', ''):
            raise click.ClickException(
                f'Invalid skill location (must be relative to project root): {loc!r}'
            )
        if any(part == '..' for part in p.parts):
            raise click.ClickException(f'Invalid skill location (must not contain ..): {loc!r}')

        resolved = (root / p).resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            raise click.ClickException(
                f'Invalid skill location (escapes project root): {loc!r}'
            ) from None

        normalized = p.as_posix().rstrip('/')
        if normalized in seen:
            continue
        seen.add(normalized)
        out.append(normalized)

    return out


def _interactive_skill_selection(project_root: Path) -> list[str]:
    """Interactive skill location selection.

    Detects existing workspace directories and prompts user to select skill
    installation locations.
    """
    available_locations = ['.claude', '.github', '.agents']
    existing_dirs = [loc for loc in available_locations if (project_root / loc).is_dir()]

    console.print()
    console.print('[bold cyan]Skill Installation Location Selection[/bold cyan]')
    console.print()

    choices = [
        questionary.Choice(
            title=f'{loc} {" (existing)" if loc in existing_dirs else ""}',
            value=loc,
            checked=loc in existing_dirs,
        )
        for loc in available_locations
    ]
    choices.append(questionary.Choice(title='Enter custom path…', value='__custom__'))

    try:
        selected = questionary.checkbox(
            'Select skill installation locations:',
            choices=choices,
            instruction='(Use arrow keys, space to toggle, enter to confirm)',
        ).ask()
    except Exception:
        # Non-interactive / unsupported console (e.g. Git Bash on Windows).
        selected = None

    if selected is None:  # User cancelled
        forced = project_root / '.agents'
        forced.mkdir(parents=True, exist_ok=True)
        console.print('[yellow]Selection cancelled, force fallback to .agents[/yellow]')
        console.print('[dim]You can switch to .claude/.github later by re-sync/update.[/dim]')
        return ['.agents']

    if not selected:
        forced = project_root / '.agents'
        forced.mkdir(parents=True, exist_ok=True)
        console.print('[yellow]No locations selected, force fallback to .agents[/yellow]')
        console.print('[dim]You can switch to .claude/.github later by re-sync/update.[/dim]')
        return ['.agents']

    # Handle custom path input
    result: list[str] = [loc for loc in selected if loc != '__custom__']
    if '__custom__' in selected:
        try:
            custom = questionary.text(
                'Enter custom skill location path (relative to project root):',
                instruction='e.g. .cursor or .windsurf',
            ).ask()
        except Exception:
            custom = None
        if custom and custom.strip():
            result.append(custom.strip())

    return result


@click.group()
def project() -> None:
    """Project-level operations (init, status, update)."""
    pass


@project.command()
@click.option('--force', is_flag=True, help='Overwrite existing .sspec directory')
@click.option(
    '--skill-loc',
    multiple=True,
    type=str,
    help='Skill installation location (can specify multiple). e.g. --skill-loc .claude',
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
    skill_locations = _validate_skill_locations(project_root, skill_locations)

    if skill_locations:
        try:
            sync_result = sync_skill_locations(
                project_root=project_root,
                locations=skill_locations,
                prefer_symlink=True,
            )
        except (OSError, RuntimeError, ValueError) as e:
            raise click.ClickException(str(e)) from None

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
    console.print('  ├── SSPEC.rule.md   # Managed sspec workflow rule')
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
                f'{status_icon} [bold]{name}[/bold] [{_get_status_color(status)}]{status}[/]'
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
        ChangeStatus.PLANNING.value: 'P',
        ChangeStatus.DOING.value: 'W',
        ChangeStatus.BLOCKED.value: 'B',
        ChangeStatus.REVIEW.value: 'R',
        ChangeStatus.DONE.value: 'D',
    }
    return icons.get(status, '?')


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
    try:
        meta_state = prepare_meta_for_project_update(sspec_root=sspec_root)
    except MetaMigrationError as err:
        raise click.ClickException(f'Failed to migrate .meta.json: {err}') from None

    meta: dict[str, Any] = meta_state.meta
    old_hashes = meta_state.old_hashes
    project_root = sspec_root.parent

    common_replacements = {'SCHEMA_VERSION': SCHEMA_VERSION, 'SCHEMA': SCHEMA_VERSION}
    sspec_schema_needs_update = meta.get('sspec_schema') != SCHEMA_VERSION

    # -----------------------------------------------------------------
    # Phase 0.4: Recover missing external skill locations from meta
    # -----------------------------------------------------------------
    try:
        recovered_locations = recover_missing_skill_locations(
            project_root=project_root,
            sspec_root=sspec_root,
            meta=meta,
            dry_run=dry_run,
        )
    except (OSError, RuntimeError, ValueError) as err:
        raise click.ClickException(
            f'Failed to recover missing skill locations: {err}'
        ) from None

    if recovered_locations:
        console.print()
        recover_table = Table(title='Missing Skill Location Recovery')
        recover_table.add_column('Location', style='cyan')
        recover_table.add_column('Status', style='yellow')
        recover_table.add_column('Mode', style='green')
        for rec in recovered_locations:
            mode = 'dry-run' if dry_run else rec.link_kind
            recover_table.add_row(rec.location, rec.status, mode)
        console.print(recover_table)

    if meta_state.migration_needed and dry_run:
        console.print(
            f'[cyan]Would migrate {sspec_root / ".meta.json"} to meta_schema {META_SCHEMA}[/cyan]'
        )
    if sspec_schema_needs_update and dry_run:
        console.print(f'[cyan]Would update sspec_schema to {SCHEMA_VERSION}[/cyan]')

    # -----------------------------------------------------------------
    # Phase 0.5: Keep hub managed-skill ignore list in sync
    # -----------------------------------------------------------------
    managed_skill_names = sorted(d.name for d in list_template_skills())
    hub_gitignore_synced = sync_hub_skills_gitignore(
        sspec_root=sspec_root,
        managed_skill_names=managed_skill_names,
        dry_run=dry_run,
    )

    if dry_run:
        if hub_gitignore_synced:
            console.print('[cyan]Would sync hub managed skill ignores in .sspec/.gitignore[/cyan]')
    else:
        if hub_gitignore_synced:
            console.print('[green]+[/green] Synced hub managed skill ignores in .sspec/.gitignore')

    gitignore_updated_count = int(bool(hub_gitignore_synced))

    # -----------------------------------------------------------------
    # Phase 0: Migrate legacy per-skill spoke layout to directory-level
    # -----------------------------------------------------------------
    migrations = migrate_legacy_skill_layouts(
        project_root=project_root,
        sspec_root=sspec_root,
        meta=meta,
        dry_run=dry_run,
    )

    if migrations:
        console.print()
        migration_table = Table(title='Legacy Skill Layout Migration')
        migration_table.add_column('Location', style='cyan')
        migration_table.add_column('Strategy', style='yellow')
        migration_table.add_column('Backup', style='dim')
        for migration in migrations:
            migration_table.add_row(
                migration.location,
                migration.strategy,
                str(migration.backup_path.relative_to(project_root)),
            )
        console.print(migration_table)

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
                    try:
                        confirmed = questionary.confirm(
                            f'Remove orphaned skill "{orphan.skill_name}"?',
                            default=True,
                        ).ask()
                    except Exception as e:
                        hint = 'Re-run without --interactive.'
                        if sys.platform == 'win32':
                            hint += ' Or use cmd.exe/PowerShell.'
                        else:
                            hint += ' Ensure stdin is a TTY terminal.'
                        raise click.ClickException(
                            f'Interactive prompt failed in this console: {e}. {hint}'
                        ) from None

                    if not confirmed:
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

    blockers = [upd for upd in updates if (upd.status in {'unknown', 'modified'}) and (not force)]

    # If hashes are missing/incomplete, backfill verifiably-current candidates so future
    # updates can be computed without getting stuck in 'unknown'.
    hash_backfill: dict[str, str] = {}
    for upd in updates:
        if upd.status != 'current':
            continue
        if upd.is_symlink or not upd.new_hash:
            continue
        if old_hashes.get(upd.hash_key) == upd.new_hash:
            continue
        hash_backfill[upd.hash_key] = upd.new_hash

    console.print()
    console.print(table)
    console.print()
    agents_needs_update = update_root_agents_block(
        project_root=sspec_root.parent,
        template_agents_path=get_template_dir() / 'AGENTS.md',
        replacements={'SCHEMA_VERSION': SCHEMA_VERSION, 'SCHEMA': SCHEMA_VERSION},
        dry_run=True,
    )

    if dry_run:
        recover_count = len(recovered_locations)
        console.print(
            '[cyan]Would update '
            f'{len(actions) + gitignore_updated_count + recover_count} item(s)[/cyan]'
        )
        if migrations:
            console.print(
                f'[cyan]Would migrate {len(migrations)} legacy skill location(s)[/cyan]'
            )
        if recover_count:
            console.print(
                f'[cyan]Would recover {recover_count} missing skill location(s)[/cyan]'
            )
        if agents_needs_update:
            console.print('[cyan]Would update root AGENTS.md block[/cyan]')
        if blockers:
            console.print(
                f'[yellow]Blocked:[/yellow] {len(blockers)} item(s) are modified/unknown; '
                're-run with --force to overwrite.'
            )
        return

    if (
        not actions
        and not agents_needs_update
        and not orphans
        and not migrations
        and not gitignore_updated_count
        and not recovered_locations
    ):
        if meta_state.migration_needed or hash_backfill or sspec_schema_needs_update:
            meta['file_hashes'] = {**old_hashes, **hash_backfill}
            meta['managed_skills'] = sorted(d.name for d in list_template_skills())
            meta['meta_schema'] = META_SCHEMA
            meta['sspec_schema'] = SCHEMA_VERSION
            meta['updated_at'] = datetime.now().isoformat()
            meta['sspec_version'] = __version__
            save_meta(sspec_root, meta)
            if meta_state.migration_needed:
                console.print('[green]+[/green] Migrated .meta.json to latest schema')
            if sspec_schema_needs_update:
                console.print(f'[green]+[/green] Updated sspec_schema to {SCHEMA_VERSION}')
            if hash_backfill:
                console.print(
                    f'[green]+[/green] Backfilled {len(hash_backfill)} hash(es) into .meta.json'
                )

        if blockers:
            console.print(
                f'[yellow]![/yellow] No updates applied: {len(blockers)} item(s) '
                'are modified/unknown. Re-run with --force to overwrite.'
            )
            return

        console.print('[green]+[/green] All files are up to date')
        return

    # Apply updates
    updated_count = 0
    skill_updated_count = 0
    new_hashes = old_hashes.copy()
    new_hashes.update(hash_backfill)

    for upd in actions:
        path = upd.display_path
        dest_path = upd.dest_path

        if interactive:
            try:
                confirmed = questionary.confirm(f'Update {path}?', default=True).ask()
            except Exception as e:
                hint = 'Re-run without --interactive.'
                if sys.platform == 'win32':
                    hint += ' Or use cmd.exe/PowerShell.'
                else:
                    hint += ' Ensure stdin is a TTY terminal.'
                raise click.ClickException(
                    f'Interactive prompt failed in this console: {e}. {hint}'
                ) from None

            if not confirmed:
                console.print(f'  [dim]Skipped {path}[/dim]')
                continue

        # 区分 skill 和普通文件的更新
        if upd.is_skill:
            # Skill 更新
            apply_skill_update(
                source=upd.template_path,
                target=upd.dest_path,
                strategy=upd.strategy or 'copy',
            )
            skill_updated_count += 1

            # 输出信息
            if upd.status == 'missing':
                action = 'Created'
            elif upd.strategy == 'link':
                action = 'Updated link'
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

    # Update metadata (also persist schema migrations + agents-only updates)
    if (
        updated_count
        or skill_updated_count
        or orphans
        or migrations
        or recovered_locations
        or agents_needs_update
        or meta_state.migration_needed
        or sspec_schema_needs_update
        or gitignore_updated_count
    ):
        meta['file_hashes'] = new_hashes
        meta['managed_skills'] = sorted(d.name for d in list_template_skills())
        meta['updated_at'] = datetime.now().isoformat()
        meta['sspec_version'] = __version__
        meta['sspec_schema'] = SCHEMA_VERSION
        meta['meta_schema'] = META_SCHEMA
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
    total_updated = updated_count + skill_updated_count + gitignore_updated_count
    if agents_needs_update:
        total_updated += 1
    if migrations:
        total_updated += len(migrations)
    if recovered_locations:
        total_updated += len(recovered_locations)
    if orphans:
        console.print(f'[red]-[/red] Removed {len(orphans)} orphaned skill(s)')
    if migrations:
        console.print(f'[green]+[/green] Migrated {len(migrations)} legacy skill location(s)')
    if recovered_locations:
        console.print(
            f'[green]+[/green] Recovered {len(recovered_locations)} skill location(s)'
        )
    console.print(f'[green]+[/green] Updated {total_updated} item(s)')
