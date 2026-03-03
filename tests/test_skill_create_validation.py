"""Tests for creating skills and name validation."""

from __future__ import annotations

import pytest

from sspec.services.skill_service import create_skill_in_hub


def test_create_skill_rejects_path_like_names(sspec_root):
    with pytest.raises(ValueError):
        create_skill_in_hub(sspec_root=sspec_root, name='../x', template_content='---\n')

    with pytest.raises(ValueError):
        create_skill_in_hub(sspec_root=sspec_root, name='a/b', template_content='---\n')

    with pytest.raises(ValueError):
        create_skill_in_hub(sspec_root=sspec_root, name='a\\b', template_content='---\n')


def test_create_skill_accepts_simple_name(sspec_root):
    res = create_skill_in_hub(
        sspec_root=sspec_root,
        name='my-skill',
        template_content='---\nname: my-skill\n---\n',
    )
    assert res.skill_name == 'my-skill'
    assert (res.hub_dir / 'SKILL.md').exists()
