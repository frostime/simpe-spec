"""Pure logic for computing update candidates for `sspec project update`."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from sspec.core import UPDATABLE_FILES, list_template_skills
from sspec.libs.hashing import compute_file_hash, compute_hash

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
    # Skill candidates
    # ---------------------------------------------------------------------
    project_root = sspec_root.parent
    skill_locations: list[str] = meta.get('skill_locations', []) or []
    skill_install_strategies: dict[str, str] = meta.get('skill_install_strategies', {}) or {}

    for skill_dir in list_template_skills():
        skill_name = skill_dir.name
        template_skill_file = skill_dir / 'SKILL.md'
        if not template_skill_file.exists():
            continue

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
                        hash_key=f'skills/{skill_name}/SKILL.md',
                        is_symlink=True,
                        strategy=strategy,
                    )
                )
                continue

            # Copy: compare content hash
            template_content = template_skill_file.read_text(encoding='utf-8')
            for old, new in common_replacements.items():
                template_content = template_content.replace(f'{{{{{old}}}}}', new)

            new_hash = compute_hash(template_content)

            if not skill_dest_file.exists():
                status = 'missing'
                current_hash = None
            else:
                current_hash = compute_file_hash(skill_dest_file)
                status = 'current' if current_hash == new_hash else 'updatable'

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
                    template_content=template_content,
                    new_hash=new_hash,
                    current_hash=current_hash,
                    hash_key=f'skills/{skill_name}/SKILL.md',
                    is_symlink=False,
                    strategy=strategy,
                )
            )

    return updates
