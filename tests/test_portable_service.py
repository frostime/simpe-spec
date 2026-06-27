"""Service tests for portable sspec resources."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from sspec.core import SCHEMA_VERSION
from sspec.services.portable_service import (
    PortableResourceError,
    list_builtin_skills,
    read_portable_resource,
    render_portable_index,
)


def test_render_portable_index_is_zero_context_bootstrap() -> None:
    output = render_portable_index()

    assert f'<sspec-portable schema="{SCHEMA_VERSION}">' in output
    assert '<what_is_this>' in output
    assert 'sspec is a spec-driven working protocol' in output
    assert '<portable_constraints>' in output
    assert 'sspec portable read rule:sspec' in output
    assert '<available_skills>' in output
    assert '<name>sspec-design</name>' in output
    assert '<read-cmd>sspec portable read skill:sspec-design</read-cmd>' in output
    assert '<location>builtin:sspec-design</location>' not in output
    assert '# .sspec Agent Protocol' not in output
    assert '# SSPEC Design' not in output


def test_list_builtin_skills_contains_metadata() -> None:
    skills = list_builtin_skills()
    by_name = {skill.name: skill for skill in skills}

    assert 'sspec-design' in by_name
    location = Path(by_name['sspec-design'].location)
    assert location.is_absolute()
    assert location.parts[-5:] == ('sspec', 'templates', 'skills', 'sspec-design', 'SKILL.md')
    assert by_name['sspec-design'].read_command == 'sspec portable read skill:sspec-design'
    assert 'Assess scale' in by_name['sspec-design'].description


def test_read_rule_sspec_wraps_rendered_source() -> None:
    output = read_portable_resource('rule:sspec')

    assert '<ref>rule:sspec</ref>' in output
    source = _extract_source(output)
    assert source.is_absolute()
    assert source.parts[-3:] == ('sspec', 'templates', 'SSPEC.rule.md')
    assert '<read-cmd>sspec portable read rule:sspec</read-cmd>' in output
    assert f'SSPEC_SCHEMA::{SCHEMA_VERSION}' in output
    assert '## 2. Change Lifecycle' in output
    assert '{{SCHEMA_VERSION}}' not in output


def test_read_skill_wraps_source_metadata() -> None:
    output = read_portable_resource('skill:sspec-design')

    assert '<ref>skill:sspec-design</ref>' in output
    source = _extract_source(output)
    assert source.is_absolute()
    assert source.parts[-5:] == ('sspec', 'templates', 'skills', 'sspec-design', 'SKILL.md')
    assert '<read-cmd>sspec portable read skill:sspec-design</read-cmd>' in output
    assert '# SSPEC Design' in output


def test_read_skill_attachment_wraps_source_metadata() -> None:
    output = read_portable_resource('skill:sspec-design/examples-feature.md')

    assert '<ref>skill:sspec-design/examples-feature.md</ref>' in output
    source = _extract_source(output)
    assert source.is_absolute()
    assert source.parts[-5:] == (
        'sspec',
        'templates',
        'skills',
        'sspec-design',
        'examples-feature.md',
    )
    assert '<content><![CDATA[' in output


def test_read_howto_and_template() -> None:
    howto = read_portable_resource('howto:write-memory')
    template = read_portable_resource('template:change/spec.md')

    assert _extract_source(howto).parts[-3:] == ('sspec', 'howto', 'write-memory.md')
    assert _extract_source(template).parts[-4:] == ('sspec', 'templates', 'change', 'spec.md')
    assert _extract_source(howto).is_absolute()
    assert _extract_source(template).is_absolute()
    assert 'Problem Statement' in template


@pytest.mark.parametrize(
    ('ref', 'message'),
    [
        ('rule:portable', 'Unknown portable rule: portable'),
        ('unknown:x', 'Unknown portable resource scope: unknown'),
        ('skill:../core.py', 'Unsafe resource path.'),
        ('skill:sspec-design/../SKILL.md', 'Unsafe resource path.'),
        ('template:change', 'Portable resource is a directory'),
        ('skill:missing-skill', 'Portable resource not found: skill:missing-skill'),
    ],
)
def test_read_resource_errors(ref: str, message: str) -> None:
    with pytest.raises(PortableResourceError, match=message):
        read_portable_resource(ref)


def _extract_source(output: str) -> Path:
    match = re.search(r'<source>(.+)</source>', output)
    assert match is not None
    return Path(match.group(1))
