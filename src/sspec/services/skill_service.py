"""Skill management services.

This module contains non-CLI business logic used by `sspec skill` commands.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from sspec import __version__
from sspec.core import SCHEMA_VERSION, SSPEC_DIR, list_template_skills
from sspec.libs.hashing import compute_dir_hash
from sspec.services.meta_service import load_meta, save_meta
from sspec.services.project_init_service import get_skill_targets_from_locations
from sspec.skill_installer import SkillInstaller


@dataclass(frozen=True, slots=True)
class ReinitSkillsResult:
    skill_targets: list[Path]
    skill_install_strategies: dict[str, str]
    managed_skills: list[str]


@dataclass(frozen=True, slots=True)
class NewSkillResult:
    hub_dir: Path
    installed_to: list[tuple[Path, str]]  # (target_dir, strategy)


def _compute_skill_install_strategies(
    *,
    project_root: Path,
    install_results: dict[Path, str],
) -> dict[str, str]:
    """Aggregate per-location strategy.

    If any skill in a location falls back to copy, the location strategy becomes copy.
    """

    strategies: dict[str, str] = {}
    for target_dir, strategy in install_results.items():
        try:
            location_key = str(target_dir.parent.relative_to(project_root))
        except ValueError:
            continue

        existing = strategies.get(location_key)
        if existing is None:
            strategies[location_key] = strategy
        elif existing == 'symlink' and strategy == 'copy':
            strategies[location_key] = 'copy'

    return strategies


def _normalize_loc_path(loc_str: str) -> Path:
    # meta uses OS-specific separators; Path() handles both.
    return Path(loc_str)


def get_linked_skill_locations(*, sspec_root: Path) -> list[str]:
    """Return linked skill locations from meta, excluding `.sspec/skills`.

    The returned values are stored meta strings (e.g. `.github\\skills`).
    """

    meta = load_meta(sspec_root)
    locations: list[str] = meta.get('skill_locations', []) or []

    linked: list[str] = []
    for loc_str in locations:
        loc_path = _normalize_loc_path(loc_str)
        if loc_path.parts and loc_path.parts[0] == SSPEC_DIR:
            continue
        linked.append(loc_str)

    # stable order
    return sorted(linked)


def reinit_template_skills(
    *,
    project_root: Path,
    sspec_root: Path,
    skill_locations: list[str],
    prefer_symlink: bool = True,
) -> ReinitSkillsResult:
    """Re-install latest template skills into `.sspec/skills` and selected targets.

    This mirrors the `project init` skill installation behavior, but does not touch
    other `.sspec/` files.
    """

    common_replacements = {'SCHEMA_VERSION': SCHEMA_VERSION, 'SCHEMA': SCHEMA_VERSION}
    template_skills = list_template_skills()

    # Resolve skill targets: spokes + always include `.sspec/skills`.
    skill_targets = get_skill_targets_from_locations(
        project_root=project_root,
        locations=skill_locations,
        sspec_dir=SSPEC_DIR,
    )

    hub_skills_dir = sspec_root / 'skills'
    hub_skills_dir.mkdir(parents=True, exist_ok=True)
    spoke_dirs = [t for t in skill_targets if t != hub_skills_dir]

    installs = [
        (skill_dir, hub_skills_dir / skill_dir.name, [t / skill_dir.name for t in spoke_dirs])
        for skill_dir in template_skills
    ]

    install_results = SkillInstaller.install_hub_and_links_batch(
        installs=installs,
        prefer_symlink=prefer_symlink,
    )

    skill_install_strategies = _compute_skill_install_strategies(
        project_root=project_root,
        install_results=cast(dict[Path, str], install_results),
    )

    # Refresh skill hashes and managed_skills
    managed_skill_names: list[str] = []
    skill_hashes: dict[str, str] = {}
    for skill_dir in template_skills:
        skill_name = skill_dir.name
        managed_skill_names.append(skill_name)
        if (skill_dir / 'SKILL.md').exists():
            skill_hashes[f'skills/{skill_name}'] = compute_dir_hash(
                skill_dir,
                common_replacements,
            )

    # Refresh meta skill-related fields
    meta: dict[str, Any] = load_meta(sspec_root)

    meta['schema_version'] = meta.get('schema_version') or SCHEMA_VERSION
    meta['sspec_version'] = __version__
    meta['updated_at'] = datetime.now().isoformat()

    old_hashes: dict[str, str] = meta.get('file_hashes', {}) or {}
    kept_hashes = {k: v for k, v in old_hashes.items() if not k.startswith('skills/')}
    kept_hashes.update(skill_hashes)
    meta['file_hashes'] = kept_hashes

    meta['managed_skills'] = sorted(managed_skill_names)
    meta['skill_install_strategies'] = skill_install_strategies

    # Persist selected + hub locations
    meta_locations: list[str] = []
    for target_dir in skill_targets:
        try:
            rel_loc = target_dir.relative_to(project_root)
        except ValueError:
            continue
        meta_locations.append(str(rel_loc))
    meta['skill_locations'] = meta_locations

    save_meta(sspec_root, meta)

    return ReinitSkillsResult(
        skill_targets=skill_targets,
        skill_install_strategies=skill_install_strategies,
        managed_skills=sorted(managed_skill_names),
    )


def create_skill_in_hub_and_install_to_linked_locations(
    *,
    sspec_root: Path,
    name: str,
    template_content: str,
    prefer_symlink: bool = True,
) -> NewSkillResult:
    """Create a new skill under `.sspec/skills/<name>` and install to linked targets."""

    project_root = sspec_root.parent
    hub_skills_dir = sspec_root / 'skills'
    hub_dir = hub_skills_dir / name

    linked_locations = get_linked_skill_locations(sspec_root=sspec_root)
    target_skill_dirs: list[Path] = [project_root / loc / name for loc in linked_locations]

    conflicts: list[Path] = []
    if hub_dir.exists():
        conflicts.append(hub_dir)
    for t in target_skill_dirs:
        if t.exists():
            conflicts.append(t)
    if conflicts:
        conflict_list = ', '.join(str(p.relative_to(project_root)) for p in conflicts)
        raise FileExistsError(f"Skill '{name}' already exists in: {conflict_list}")

    hub_dir.mkdir(parents=True, exist_ok=True)
    skill_file = hub_dir / 'SKILL.md'
    skill_file.write_text(template_content, encoding='utf-8')

    installed_to: list[tuple[Path, str]] = []
    if target_skill_dirs:
        results = SkillInstaller.install_skills_batch(
            installs=[(hub_dir, t) for t in target_skill_dirs],
            prefer_symlink=prefer_symlink,
        )
        installed_to = [(target, strategy) for target, _source, strategy in results]

    return NewSkillResult(hub_dir=hub_dir, installed_to=installed_to)
