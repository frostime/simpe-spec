"""Pure logic for computing update candidates for `sspec project update`."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from sspec.core import UPDATABLE_FILES, list_template_skills
from sspec.libs.hashing import compute_dir_hash, compute_file_hash, compute_hash

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

    is_symlink: bool = False
    strategy: str | None = None


@dataclass(frozen=True, slots=True)
class OrphanedSkill:
    """A skill that exists on disk but is no longer in the template set."""

    skill_name: str
    paths: list[Path]  # All locations where this orphan exists


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
        if path.is_symlink():
            path.unlink()
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
                status = 'unknown'
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
            )
        )

    # ---------------------------------------------------------------------
    # Skill candidates — uses directory hash for full content tracking
    # ---------------------------------------------------------------------
    project_root = sspec_root.parent
    skill_locations: list[str] = meta.get('skill_locations', []) or []
    skill_install_strategies: dict[str, str] = meta.get('skill_install_strategies', {}) or {}

    for skill_dir in list_template_skills():
        skill_name = skill_dir.name
        template_skill_file = skill_dir / 'SKILL.md'
        if not template_skill_file.exists():
            continue

        # Hash key: prefer new format, fall back to legacy
        hash_key = f'skills/{skill_name}'
        legacy_hash_key = f'skills/{skill_name}/SKILL.md'

        for loc_str in skill_locations:
            skill_dest_dir = project_root / loc_str / skill_name
            skill_dest_file = skill_dest_dir / 'SKILL.md'

            strategy = skill_install_strategies.get(loc_str, 'copy')

            # Symlink: only check link validity
            if strategy == 'symlink':
                if skill_dest_dir.is_symlink():
                    try:
                        status = (
                            'current'
                            if skill_dest_dir.resolve() == skill_dir.resolve()
                            else 'updatable'
                        )
                    except OSError:
                        status = 'missing'
                else:
                    status = 'missing'

                updates.append(
                    UpdateCandidate(
                        display_path=str(Path(loc_str) / skill_name),
                        status=status,  # type: ignore[arg-type]
                        template_path=skill_dir,
                        dest_path=skill_dest_dir,
                        template_content='',
                        new_hash=None,
                        current_hash=None,
                        hash_key=hash_key,
                        is_symlink=True,
                        strategy=strategy,
                    )
                )
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
                    # No recorded hash — compare directly
                    status = 'current' if current_hash == new_hash else 'updatable'
                elif current_hash == new_hash:
                    status = 'current'
                else:
                    status = 'updatable'

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
                    is_symlink=False,
                    strategy=strategy,
                )
            )

    return updates
