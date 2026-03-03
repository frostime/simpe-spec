"""Pure logic for computing update candidates for `sspec project update`."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from sspec.core import UPDATABLE_FILES, list_template_skills
from sspec.libs.hashing import compute_dir_hash, compute_file_hash, compute_hash
from sspec.skill_installer import SkillStrategy, check_path_link, remove_path_link

UpdateStatus = Literal['missing', 'current', 'updatable', 'modified', 'unknown']


@dataclass(frozen=True, slots=True)
class UpdateCandidate:
    display_path: str
    status: UpdateStatus
    template_path: Path
    dest_path: Path
    template_content: str
    new_hash: str | None
    current_hash: str | None
    hash_key: str

    is_skill: bool = False
    is_symlink: bool = False
    strategy: str | None = None


@dataclass(frozen=True, slots=True)
class OrphanedSkill:
    """A skill that exists on disk but is no longer in the template set."""

    skill_name: str
    paths: list[Path]  # All locations where this orphan exists


@dataclass(frozen=True, slots=True)
class LegacySkillMigration:
    """Result for migrating old per-skill spoke layout to directory-level spoke."""

    location: str
    location_path: Path
    backup_path: Path
    strategy: str
    merged_custom_skills: list[str]


class MetaMigrationError(RuntimeError):
    """Raised when project update cannot migrate .meta.json safely."""


@dataclass(frozen=True, slots=True)
class MetaUpdateState:
    """Meta state prepared for the project update pipeline."""

    meta: dict[str, Any]
    old_hashes: dict[str, str]
    migration_needed: bool


def prepare_meta_for_project_update(*, sspec_root: Path) -> MetaUpdateState:
    """Load and validate meta for project update.

    Meta migration is an explicit first stage of `project update`.
    """

    from sspec.services.meta_service import load_meta_latest

    try:
        meta_res = load_meta_latest(sspec_root)
    except ValueError as err:
        raise MetaMigrationError(str(err)) from err

    meta: dict[str, Any] = dict(meta_res.meta)
    old_hashes: dict[str, str] = dict(meta.get('file_hashes', {}) or {})
    return MetaUpdateState(
        meta=meta,
        old_hashes=old_hashes,
        migration_needed=meta_res.changed,
    )


def apply_skill_update(*, source: Path, target: Path, strategy: SkillStrategy) -> None:
    """Apply skill update through service boundary."""
    from sspec.skill_installer import SkillInstaller

    installer = SkillInstaller._get_installer()
    installer.update_skill(source=source, target=target, strategy=strategy)


def migrate_legacy_skill_layouts(
    *,
    project_root: Path,
    sspec_root: Path,
    meta: dict[str, Any],
    dry_run: bool = False,
) -> list[LegacySkillMigration]:
    """Migrate old per-skill spoke layout to directory-level hub->spoke layout.

    Legacy layout example:
    - `.claude/skills/<skill-a>` (symlink)
    - `.claude/skills/<skill-b>` (symlink)

    Target layout:
    - `.claude/skills` -> `.sspec/skills` (symlink/junction/copy fallback)
    """
    skill_locations: list[str] = meta.get('skill_locations', []) or []
    hub_skills_dir = sspec_root / 'skills'
    if not hub_skills_dir.exists():
        return []

    template_skill_names = {d.name for d in list_template_skills()}
    migrations: list[LegacySkillMigration] = []

    for location in skill_locations:
        if location == '.sspec/skills':
            continue

        location_path = project_root / location
        if (
            not location_path.exists()
            or not location_path.is_dir()
            or check_path_link(location_path)
        ):
            continue

        children = [
            child for child in location_path.iterdir() if child.is_dir() or check_path_link(child)
        ]
        if not children:
            continue

        linked_children = [child for child in children if check_path_link(child)]
        if not linked_children:
            continue

        hub_linked_children = [
            child
            for child in linked_children
            if check_path_link(child, expected_target=hub_skills_dir / child.name)
        ]
        if not hub_linked_children:
            continue

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        safe_location = location.replace('/', '_').replace('\\', '_')
        backup_path = sspec_root / 'tmp' / 'skills-backup' / timestamp / safe_location

        merged_custom_skills: list[str] = []

        if not dry_run:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            backup_path.mkdir(parents=True, exist_ok=True)

            for child in children:
                expected_hub_target = hub_skills_dir / child.name
                if check_path_link(child, expected_target=expected_hub_target):
                    continue

                backup_child = backup_path / child.name
                if child.is_dir():
                    shutil.copytree(child, backup_child, symlinks=False)
                elif child.exists():
                    shutil.copy2(child, backup_child)

            for child in children:
                if child.name in template_skill_names:
                    continue
                if check_path_link(child) or not child.is_dir():
                    continue

                hub_dest = hub_skills_dir / child.name
                if not hub_dest.exists():
                    shutil.copytree(child, hub_dest)
                    merged_custom_skills.append(child.name)

            from sspec.skill_installer import SkillInstaller

            installer = SkillInstaller._get_installer()
            install_results = installer.install_batch(
                [(hub_skills_dir, location_path)],
                prefer_symlink=True,
                allow_elevation=False,
                prefer_junction_on_windows=True,
            )
            strategy = install_results[0].strategy if install_results else 'copy'

            existing_strategies = dict(meta.get('skill_install_strategies', {}) or {})
            existing_strategies[location] = strategy
            meta['skill_install_strategies'] = existing_strategies
        else:
            strategy = 'symlink/junction/copy'

        migrations.append(
            LegacySkillMigration(
                location=location,
                location_path=location_path,
                backup_path=backup_path,
                strategy=strategy,
                merged_custom_skills=merged_custom_skills,
            )
        )

    return migrations


def collect_orphaned_skills(
    *,
    project_root: Path,
    meta: dict[str, Any],
) -> list[OrphanedSkill]:
    """Find skills that were previously managed but are no longer in templates.

    This detects renamed/removed skills that would otherwise leave stale dirs.
    """
    managed: set[str] = set(meta.get('managed_skills', []) or [])
    current_template_names = {d.name for d in list_template_skills()}
    skill_locations: list[str] = meta.get('skill_locations', []) or []

    orphan_names = managed - current_template_names
    orphans: list[OrphanedSkill] = []

    for name in sorted(orphan_names):
        paths: list[Path] = []
        for loc_str in skill_locations:
            location_root = project_root / loc_str
            if check_path_link(location_root):
                continue
            skill_dir = project_root / loc_str / name
            if skill_dir.exists():
                paths.append(skill_dir)
        if paths:
            orphans.append(OrphanedSkill(skill_name=name, paths=paths))

    return orphans


def remove_orphaned_skill(orphan: OrphanedSkill) -> int:
    """Remove an orphaned skill from all locations. Returns count of dirs removed."""
    removed = 0
    for path in orphan.paths:
        if check_path_link(path):
            remove_path_link(path)
            removed += 1
        elif path.exists():
            shutil.rmtree(path)
            removed += 1
    return removed


def collect_update_candidates(
    *,
    sspec_root: Path,
    template_dir: Path,
    meta: dict[str, Any],
    common_replacements: dict[str, str],
) -> list[UpdateCandidate]:
    """Collect all update candidates (template files + skills).

    This function is CLI-agnostic: no click/rich/questionary.
    """
    old_hashes: dict[str, str] = meta.get('file_hashes', {}) or {}
    updates: list[UpdateCandidate] = []

    # ---------------------------------------------------------------------
    # Template file candidates
    # ---------------------------------------------------------------------
    for file_path in UPDATABLE_FILES:
        template_path = template_dir / file_path
        dest_path = sspec_root / file_path

        if not template_path.exists():
            continue

        template_content = template_path.read_text(encoding='utf-8')
        if template_path.suffix == '.md':
            for old, new in common_replacements.items():
                template_content = template_content.replace(f'{{{{{old}}}}}', new)

        new_hash = compute_hash(template_content)

        if not dest_path.exists():
            status: UpdateStatus = 'missing'
            current_hash = None
        else:
            current_hash = compute_file_hash(dest_path)
            old_hash = old_hashes.get(file_path)

            if old_hash is None:
                # If we can verify the file matches the current template, treat as current.
                # This avoids projects being stuck in 'unknown' when hashes are missing.
                status = 'current' if current_hash == new_hash else 'unknown'
            elif current_hash == new_hash:
                status = 'current'
            elif current_hash == old_hash:
                status = 'updatable'
            else:
                status = 'modified'

        updates.append(
            UpdateCandidate(
                display_path=file_path,
                status=status,
                template_path=template_path,
                dest_path=dest_path,
                template_content=template_content,
                new_hash=new_hash,
                current_hash=current_hash,
                hash_key=file_path,
                is_skill=False,
            )
        )

    # ---------------------------------------------------------------------
    # Skill candidates — uses directory hash for full content tracking
    # ---------------------------------------------------------------------
    project_root = sspec_root.parent
    skill_locations: list[str] = meta.get('skill_locations', []) or []
    # NOTE: Skill update behavior is based on actual filesystem state.
    # - If the installed skill directory is a symlink, we skip it entirely.
    # - If it's a real directory (copy), we update it via directory hash.
    # meta.skill_install_strategies is kept for informational purposes only.

    for skill_dir in list_template_skills():
        skill_name = skill_dir.name
        template_skill_file = skill_dir / 'SKILL.md'
        if not template_skill_file.exists():
            # TODO 无法增加新的 SKILL
            continue

        # Hash key: prefer new format, fall back to legacy
        hash_key = f'skills/{skill_name}'
        legacy_hash_key = f'skills/{skill_name}/SKILL.md'

        for loc_str in skill_locations:
            location_root = project_root / loc_str
            if check_path_link(location_root):
                continue

            skill_dest_dir = project_root / loc_str / skill_name
            skill_dest_file = skill_dest_dir / 'SKILL.md'

            # Skip link-like skills (symlink/junction) during update.
            # They should point to hub (.sspec/skills) and are not updated here.
            if check_path_link(skill_dest_dir):
                continue

            # Copy: compare directory hash (catches reference file changes)
            new_hash = compute_dir_hash(skill_dir, common_replacements)

            if not skill_dest_file.exists():
                status = 'missing'
                current_hash = None
            else:
                # Check both new and legacy hash keys for backward compat
                old_hash = old_hashes.get(hash_key) or old_hashes.get(legacy_hash_key)

                current_hash = (
                    compute_dir_hash(skill_dest_dir, {}) if skill_dest_dir.exists() else None
                )

                if old_hash is None:
                    status = 'current' if current_hash == new_hash else 'unknown'
                elif current_hash == new_hash:
                    status = 'current'
                elif current_hash == old_hash:
                    status = 'updatable'
                else:
                    status = 'modified'

            try:
                display_path = str(skill_dest_file.relative_to(project_root))
            except ValueError:
                display_path = str(skill_dest_file)

            updates.append(
                UpdateCandidate(
                    display_path=display_path,
                    status=status,  # type: ignore[arg-type]
                    template_path=skill_dir,
                    dest_path=skill_dest_dir,
                    template_content='',  # Not used for dir-level skills
                    new_hash=new_hash,
                    current_hash=current_hash,
                    hash_key=hash_key,
                    is_skill=True,
                    is_symlink=False,
                    strategy='copy',
                )
            )

    return updates
