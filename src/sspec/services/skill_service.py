"""Skill management services.

This module contains non-CLI business logic used by `sspec skill` commands.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

import yaml

from sspec import __version__
from sspec.core import SKILL_SUBDIR, SKILLS_DIR, SSPEC_DIR, WORKSPACE_DIRS
from sspec.services.meta_service import load_meta, save_meta


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


def create_skill_in_hub(
    *,
    sspec_root: Path,
    name: str,
    template_content: str,
) -> CreateSkillResult:
    """Create a new skill under `.sspec/skills/<name>`.

    User should run `project update` after creating to sync to other locations.
    """

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
    meta['updated_at'] = __version__
    save_meta(sspec_root, meta)

    return CreateSkillResult(hub_dir=hub_dir, skill_name=name)
