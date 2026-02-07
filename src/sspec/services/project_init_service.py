"""Pure-ish init logic for `sspec project init`.

Commands should handle interactive prompts and user-facing output; this service
creates folders/files and performs template + skill installation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from sspec import __version__
from sspec.core import (
    SCHEMA_VERSION,
    SSPEC_DIR,
    UPDATABLE_FILES,
    USER_FILES,
    copy_template,
    get_template_dir,
    list_template_skills,
)
from sspec.libs.hashing import compute_dir_hash, compute_hash
from sspec.services.agents_service import update_root_agents_block
from sspec.services.meta_service import save_meta


class ProjectAlreadyInitializedError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class InitResult:
    sspec_path: Path
    skill_install_strategies: dict[str, str]
    skill_targets: list[Path]
    created_or_updated_agents: bool


def get_skill_targets_from_locations(
    *,
    project_root: Path,
    locations: list[str],
    sspec_dir: str = SSPEC_DIR,
) -> list[Path]:
    """Resolve skill target directories from location names.

    Always includes `.sspec/skills` for backward compatibility.
    """
    targets: list[Path] = []

    for loc in locations:
        if loc == '.sspec':
            continue
        targets.append(project_root / loc / 'skills')

    targets.append(project_root / sspec_dir / 'skills')
    return targets


def initialize_project(
    *,
    project_root: Path,
    force: bool,
    skill_locations: list[str],
    default_gitignore: str,
    prefer_symlink: bool = True,
) -> InitResult:
    """Initialize `.sspec/` in a project root.

    Raises:
        ProjectAlreadyInitializedError: if `.sspec/` exists and force=False.
    """
    sspec_path = project_root / SSPEC_DIR

    if sspec_path.exists() and not force:
        raise ProjectAlreadyInitializedError(
            f'{SSPEC_DIR} already exists. Use --force to reinitialize.'
        )

    template_dir = get_template_dir()
    common_replacements = {'SCHEMA_VERSION': SCHEMA_VERSION, 'SCHEMA': SCHEMA_VERSION}

    # Create directory structure
    sspec_path.mkdir(parents=True, exist_ok=True)
    (sspec_path / 'changes').mkdir(exist_ok=True)
    (sspec_path / 'changes' / 'archive').mkdir(exist_ok=True)
    (sspec_path / 'requests').mkdir(exist_ok=True)
    (sspec_path / 'asks').mkdir(exist_ok=True)
    (sspec_path / 'skills').mkdir(exist_ok=True)
    (sspec_path / 'spec-docs').mkdir(exist_ok=True)

    # Install skills
    template_skills = list_template_skills()
    skill_targets = get_skill_targets_from_locations(
        project_root=project_root,
        locations=skill_locations,
        sspec_dir=SSPEC_DIR,
    )

    from sspec.skill_installer import SkillInstaller

    skill_install_strategies: dict[str, str] = {}

    for skill_dir in template_skills:
        skill_name = skill_dir.name
        for target_dir in skill_targets:
            dest_skill_dir = target_dir / skill_name

            strategy = SkillInstaller.install_skill(
                source_dir=skill_dir,
                target_dir=dest_skill_dir,
                prefer_symlink=prefer_symlink,
            )

            # Record first observed strategy for this location.
            try:
                rel_target = target_dir.relative_to(project_root)
            except ValueError:
                continue

            location_key = str(rel_target)
            if location_key not in skill_install_strategies:
                skill_install_strategies[location_key] = strategy

    # Initialize templates
    for file_path in [*UPDATABLE_FILES, *USER_FILES]:
        template_path = template_dir / file_path
        dest_path = sspec_path / file_path

        if not template_path.exists():
            continue

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        copy_template(template_path, dest_path, common_replacements)

    # Create .gitignore
    gitignore_path = sspec_path / '.gitignore'
    if not gitignore_path.exists():
        gitignore_path.write_text(default_gitignore, encoding='utf-8')

    # Compute hashes for installed skills (for update tracking)
    skill_hashes: dict[str, str] = {}
    managed_skill_names: list[str] = []
    for skill_dir in template_skills:
        skill_name = skill_dir.name
        managed_skill_names.append(skill_name)

        if not (skill_dir / 'SKILL.md').exists():
            continue

        skill_hashes[f'skills/{skill_name}'] = compute_dir_hash(
            skill_dir, common_replacements
        )

    # Create initial .meta.json
    meta_data: dict[str, Any] = {
        'schema_version': SCHEMA_VERSION,
        'sspec_version': __version__,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'file_hashes': skill_hashes,
        'managed_skills': sorted(managed_skill_names),
        'skill_locations': [],
        'skill_install_strategies': skill_install_strategies,
    }

    for target_dir in skill_targets:
        if not target_dir.exists():
            continue
        try:
            rel_loc = target_dir.relative_to(project_root)
        except ValueError:
            continue
        meta_data['skill_locations'].append(str(rel_loc))

    for file_path in UPDATABLE_FILES:
        dest_path = sspec_path / file_path
        if dest_path.exists():
            meta_data['file_hashes'][file_path] = compute_hash(
                dest_path.read_text(encoding='utf-8')
            )

    save_meta(sspec_path, meta_data)

    created_or_updated_agents = update_root_agents_block(
        project_root=project_root,
        template_agents_path=template_dir / 'AGENTS.md',
        replacements=common_replacements,
        dry_run=False,
    )

    return InitResult(
        sspec_path=sspec_path,
        skill_install_strategies=skill_install_strategies,
        skill_targets=skill_targets,
        created_or_updated_agents=created_or_updated_agents,
    )
