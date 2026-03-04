"""Skill management services.

This module contains non-CLI business logic used by `sspec skill` commands.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, TypedDict

import yaml

from sspec.core import SKILL_SUBDIR, SKILLS_DIR, SSPEC_DIR, WORKSPACE_DIRS
from sspec.libs.hashing import compute_dir_hash
from sspec.services.meta_service import load_meta, save_meta
from sspec.skill_installer import check_path_link, detect_path_link, remove_path_link


class SkillInfo(TypedDict):
    """Structured skill information."""

    file: str
    path: Path
    skill: str
    description: str


def parse_skill_metadata(skill_path: Path, replacements: Mapping[str, str] | None = None) -> dict:
    """Parse YAML front matter from a SKILL.md file."""

    if not skill_path.exists():
        return {}

    content = skill_path.read_text(encoding='utf-8')
    if replacements:
        content = render_template(content, replacements)
    if not content.startswith('---'):
        return {}

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}

    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


def render_template(content: str, replacements: Mapping[str, str]) -> str:
    """Render {{var}} placeholders with provided replacements."""

    def _replace(match: re.Match) -> str:
        key = match.group(1).strip()
        return str(replacements.get(key, ''))

    return re.sub(r'{{\s*(.+?)\s*}}', _replace, content)


def get_workspace_skill_targets(project_root: Path, primary_loc: str | None = None) -> list[Path]:
    """Return workspace directories that should host skills.

    Args:
        project_root: Project root directory
        primary_loc: Primary location for skills (.claude, .github, or .sspec)
                    If specified, only install to primary_loc and .sspec (for compatibility)
                    If None, auto-detect existing workspace dirs

    Returns:
        List of target directories for skill installation
    """
    targets: list[Path] = []

    if primary_loc:
        if primary_loc != '.sspec':
            primary_path = project_root / primary_loc / SKILL_SUBDIR
            targets.append(primary_path)
        targets.append(project_root / SSPEC_DIR / SKILL_SUBDIR)
    else:
        for ws_dir in WORKSPACE_DIRS:
            ws_path = project_root / ws_dir
            if ws_path.is_dir():
                targets.append(ws_path / SKILL_SUBDIR)
        targets.append(project_root / SSPEC_DIR / SKILL_SUBDIR)

    return targets


def list_skills(sspec_root: Path) -> list[SkillInfo]:
    """List all skills found in skills directory."""

    skills: list[SkillInfo] = []
    skills_dir = sspec_root / SKILLS_DIR

    if not skills_dir.exists():
        return skills

    for entry in skills_dir.iterdir():
        if entry.is_file() and entry.suffix == '.md':
            meta = parse_skill_metadata(entry)
            name = meta.get('name') or meta.get('skill', entry.stem)
            if name:
                skills.append(
                    {
                        'file': entry.name,
                        'path': entry,
                        'skill': str(name),
                        'description': str(meta.get('description', '')),
                    }
                )
        elif entry.is_dir():
            skill_file = entry / 'SKILL.md'
            meta = parse_skill_metadata(skill_file)
            name = meta.get('name') or meta.get('skill', entry.name)
            if name:
                skills.append(
                    {
                        'file': f'{entry.name}/SKILL.md',
                        'path': skill_file,
                        'skill': str(name),
                        'description': str(meta.get('description', '')),
                    }
                )

    return sorted(skills, key=lambda x: x['skill'])


@dataclass(frozen=True, slots=True)
class CreateSkillResult:
    hub_dir: Path
    skill_name: str


DominateStatus = Literal['linked', 'relinked', 'skipped', 'needs_relink', 'merged']


@dataclass(frozen=True, slots=True)
class DominateSkillsResult:
    """Result for `sspec skill dominate` operation."""

    status: DominateStatus
    dominate_dir: Path
    target_dir: Path
    source_dir: Path
    link_kind: str
    current_target: Path | None = None
    backup_path: Path | None = None
    merged_skills: list[str] | None = None
    conflict_skills: list[str] | None = None


def _create_skills_link(*, source_dir: Path, target_dir: Path) -> str:
    """Create a platform-specific link from target_dir to source_dir."""

    # ---------------------------------------------------------------------
    # Section 1: Ensure parent exists and clear pre-existing target node.
    # ---------------------------------------------------------------------

    target_dir.parent.mkdir(parents=True, exist_ok=True)

    if target_dir.exists() or detect_path_link(target_dir) != 'none':
        if check_path_link(target_dir):
            remove_path_link(target_dir)
        elif target_dir.is_dir():
            shutil.rmtree(target_dir)
        else:
            target_dir.unlink()

    # ---------------------------------------------------------------------
    # Section 2: Create platform-specific link.
    # - Windows: junction link
    # - Others: symlink
    # ---------------------------------------------------------------------
    if sys.platform == 'win32':
        cmd = [
            'powershell',
            '-NoProfile',
            '-Command',
            (
                '$ErrorActionPreference="Stop"; '
                f'New-Item -ItemType Junction -Path "{target_dir}" '
                f'-Target "{source_dir}" | Out-Null'
            ),
        ]
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if check_path_link(target_dir, expected_target=source_dir):
            return 'junction'
        raise OSError(f'Failed to create junction link: {target_dir}')

    target_dir.symlink_to(source_dir, target_is_directory=True)
    if check_path_link(target_dir, expected_target=source_dir):
        return 'symlink'
    raise OSError(f'Failed to create symlink: {target_dir}')


def _backup_and_merge_skills(
    *,
    sspec_root: Path,
    external_skills_dir: Path,
) -> tuple[Path, list[str], list[str]]:
    """Backup external skills dir and merge changed skills into hub."""

    # ---------------------------------------------------------------------
    # Section 1: Full backup first (safety net for all follow-up decisions).
    # ---------------------------------------------------------------------
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    safe_name = external_skills_dir.parent.as_posix().replace('/', '_').replace(':', '')
    backup_path = sspec_root / 'tmp' / 'skill-dominate' / f'{timestamp}_{safe_name}' / 'skills'

    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(external_skills_dir, backup_path)

    # ---------------------------------------------------------------------
    # Section 2: Merge non-conflicting skills into hub.
    # Rule:
    # - Missing in hub: copy in
    # - Same content: skip
    # - Different content: mark as conflict, keep hub version unchanged
    # ---------------------------------------------------------------------
    hub_skills_dir = sspec_root / 'skills'
    hub_skills_dir.mkdir(parents=True, exist_ok=True)

    merged_skills: list[str] = []
    conflict_skills: list[str] = []
    for child in external_skills_dir.iterdir():
        if not child.is_dir() or not (child / 'SKILL.md').exists():
            continue

        hub_child = hub_skills_dir / child.name
        if not hub_child.exists():
            shutil.copytree(child, hub_child)
            merged_skills.append(child.name)
            continue

        src_hash = compute_dir_hash(child, {})
        dst_hash = compute_dir_hash(hub_child, {})
        if src_hash == dst_hash:
            continue

        conflict_skills.append(child.name)

    return backup_path, merged_skills, conflict_skills


def dominate_skills_location(
    *,
    sspec_root: Path,
    dominate_dir: Path,
    force_relink: bool = False,
) -> DominateSkillsResult:
    """Dominate an external dir's `skills` by linking it to `.sspec/skills`."""

    # ---------------------------------------------------------------------
    # Section 1: Resolve canonical source/target directories.
    # ---------------------------------------------------------------------
    source_dir = sspec_root / 'skills'
    if not source_dir.exists():
        source_dir.mkdir(parents=True, exist_ok=True)

    dominate_dir.mkdir(parents=True, exist_ok=True)
    target_dir = dominate_dir / 'skills'

    # ---------------------------------------------------------------------
    # Section 2: Missing target -> create link directly.
    # ---------------------------------------------------------------------
    if not target_dir.exists() and detect_path_link(target_dir) == 'none':
        link_kind = _create_skills_link(source_dir=source_dir, target_dir=target_dir)
        return DominateSkillsResult(
            status='linked',
            dominate_dir=dominate_dir,
            target_dir=target_dir,
            source_dir=source_dir,
            link_kind=link_kind,
        )

    # ---------------------------------------------------------------------
    # Section 3: Existing link target.
    # - Correct link: skip
    # - Wrong link: ask caller for relink decision
    # ---------------------------------------------------------------------
    kind = detect_path_link(target_dir)
    if kind != 'none':
        current_target = target_dir.resolve(strict=False)
        if check_path_link(target_dir, expected_target=source_dir):
            return DominateSkillsResult(
                status='skipped',
                dominate_dir=dominate_dir,
                target_dir=target_dir,
                source_dir=source_dir,
                link_kind=kind,
                current_target=current_target,
            )

        if not force_relink:
            return DominateSkillsResult(
                status='needs_relink',
                dominate_dir=dominate_dir,
                target_dir=target_dir,
                source_dir=source_dir,
                link_kind=kind,
                current_target=current_target,
            )

        remove_path_link(target_dir)
        new_kind = _create_skills_link(source_dir=source_dir, target_dir=target_dir)
        return DominateSkillsResult(
            status='relinked',
            dominate_dir=dominate_dir,
            target_dir=target_dir,
            source_dir=source_dir,
            link_kind=new_kind,
            current_target=current_target,
        )

    # ---------------------------------------------------------------------
    # Section 4: Existing real directory.
    # Backup + safe merge + rebuild link.
    # ---------------------------------------------------------------------
    if target_dir.is_dir():
        backup_path, merged_skills, conflict_skills = _backup_and_merge_skills(
            sspec_root=sspec_root,
            external_skills_dir=target_dir,
        )
        shutil.rmtree(target_dir)
        link_kind = _create_skills_link(source_dir=source_dir, target_dir=target_dir)
        return DominateSkillsResult(
            status='merged',
            dominate_dir=dominate_dir,
            target_dir=target_dir,
            source_dir=source_dir,
            link_kind=link_kind,
            backup_path=backup_path,
            merged_skills=merged_skills,
            conflict_skills=conflict_skills,
        )

    raise ValueError(f'Cannot dominate non-directory target: {target_dir}')


def create_skill_in_hub(
    *,
    sspec_root: Path,
    name: str,
    template_content: str,
) -> CreateSkillResult:
    """Create a new skill under `.sspec/skills/<name>`.

    User should run `project update` after creating to sync to other locations.
    """

    if not name or not isinstance(name, str):
        raise ValueError('Skill name must be a non-empty string')
    if name.strip() != name:
        raise ValueError('Skill name must not contain leading/trailing whitespace')
    if '/' in name or '\\' in name or '..' in name or ':' in name:
        raise ValueError(f'Invalid skill name: {name!r}')

    hub_skills_dir = sspec_root / 'skills'
    hub_dir = hub_skills_dir / name

    if hub_dir.exists():
        raise FileExistsError(
            f"Skill '{name}' already exists in {hub_dir.relative_to(sspec_root.parent)}"
        )

    hub_dir.mkdir(parents=True, exist_ok=True)
    skill_file = hub_dir / 'SKILL.md'
    skill_file.write_text(template_content, encoding='utf-8')

    meta: dict[str, Any] = load_meta(sspec_root)
    meta['updated_at'] = datetime.now().isoformat()
    save_meta(sspec_root, meta)

    return CreateSkillResult(hub_dir=hub_dir, skill_name=name)
