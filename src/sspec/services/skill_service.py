"""Skill management services.

This module contains non-CLI business logic used by `sspec skill` commands.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sspec import __version__
from sspec.services.meta_service import load_meta, save_meta


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
