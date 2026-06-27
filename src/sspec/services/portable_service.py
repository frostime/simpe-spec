"""Portable sspec resource access for no-project Agent workflows."""

from __future__ import annotations

import os
from dataclasses import dataclass
from html import escape
from importlib import resources
from importlib.abc import Traversable
from pathlib import Path, PurePosixPath
from typing import Literal

import yaml

from sspec.core import SCHEMA_VERSION, render_template

_ALLOWED_SCOPES = {'rule', 'skill', 'template', 'howto'}

PORTABLE_INTRO = f"""
<sspec-portable schema="{SCHEMA_VERSION}">

<what_is_this>
sspec is a spec-driven working protocol for AI coding agents.
It provides:
- rules: general behavior for clarifying, designing, planning, implementing,
  reviewing, and aligning with the user;
- skills: task-specific instructions loaded only when relevant;
- templates: optional files used by full sspec projects to persist specs,
  tasks, memory, requests, and docs.

You are using sspec in portable mode.
Portable mode means: use sspec rules and skills as behavioral guidance,
but do not initialize or manage sspec project state in the current workspace.
</what_is_this>

<portable_constraints>
Unless the user explicitly asks to install or manage sspec in this project:
- do not run `sspec project init`;
- do not run `sspec change new`, `sspec request new`, `sspec doc new`, or `sspec skill dominate`;
- do not create `.sspec/`, `AGENTS.md`, `spec.md`, `tasks.md`, or `memory.md`
  as sspec-managed files;
- do not treat missing `.sspec/project.md` as an error;
- do not load all SKILLs eagerly.
</portable_constraints>

<required_next_steps>
1. First read the sspec rule:
   sspec portable read rule:sspec

2. Classify the user request using the rule.

3. If the task matches a listed SKILL, read that SKILL before acting:
   sspec portable read skill:<name>

4. If a loaded SKILL references a relative file, read it with:
   sspec portable read skill:<name>/<relative-path>

5. If a loaded rule or SKILL references a HOWTO or template, read it with:
   sspec portable read howto:<name>
   sspec portable read template:<path>
</required_next_steps>

<project_to_portable_behavior_mapping>
- If sspec says to read `.sspec/project.md`:
  If it exists and is relevant, you may read it. If missing, continue using the
  user's request and codebase context.
- If sspec says to run `sspec change new ...`:
  Do not run it. Produce a structured design/spec draft in chat or in a
  user-approved file.
- If sspec says to write `spec.md`:
  Output sections such as Problem Statement, Approach, Behavior Contract,
  Implementation Changes, and Scope Summary.
- If sspec says to write `design.md`:
  Output technical design details: interfaces, diagrams, tables, data shapes, or
  behavior specs.
- If sspec says to write `tasks.md`:
  Output an execution plan/checklist with verification criteria.
- If sspec says to write `memory.md`:
  Keep concise session notes only when needed; do not persist `.sspec` memory unless
  user asks.
- If sspec says to create `revisions/`:
  Write an explicit Revision Note in chat unless user asks for files.
- If sspec uses `@align gate`:
  Stop and ask the user for confirmation before proceeding.
- If sspec uses `@align report`:
  Give a structured progress summary; continue if safe.
- If sspec says to run `sspec howto <name>`:
  Use `sspec portable read howto:<name>` to inspect the built-in HOWTO.
- If a SKILL references `./examples.md`:
  Use `sspec portable read skill:<skill>/<relative-path>`.
</project_to_portable_behavior_mapping>

<rule_index>
  <rule>
    <name>sspec</name>
    <description>Rendered sspec agent protocol from the built-in AGENTS.md template.</description>
    <read-cmd>sspec portable read rule:sspec</read-cmd>
  </rule>
</rule_index>
""".strip()

PORTABLE_FOOTER = '</sspec-portable>'


@dataclass(frozen=True, slots=True)
class PortableSkillEntry:
    """A built-in skill entry exposed through portable bootstrap output."""

    name: str
    description: str
    location: str
    read_command: str


@dataclass(frozen=True, slots=True)
class PortableResource:
    """Resolved portable resource content and metadata."""

    ref: str
    source: str
    content: str

    @property
    def read_command(self) -> str:
        """Return the command that reads this resource."""

        return f'sspec portable read {self.ref}'


class PortableResourceError(ValueError):
    """Raised when a portable resource ref cannot be resolved safely."""


def render_portable_index() -> str:
    """Render the portable bootstrap and built-in skill index."""

    return f'{PORTABLE_INTRO}\n\n{_render_available_skills()}\n\n{PORTABLE_FOOTER}\n'


def read_portable_resource(ref: str) -> str:
    """Read a portable resource by ``<scope:slug>`` and render it with metadata."""

    resource = resolve_portable_resource(ref)
    return render_portable_resource(resource)


def resolve_portable_resource(ref: str) -> PortableResource:
    """Resolve a portable resource by ``<scope:slug>``."""

    scope, slug = _parse_ref(ref)
    if scope == 'rule':
        return _resolve_rule(ref, slug)
    if scope == 'skill':
        return _resolve_skill(ref, slug)
    if scope == 'template':
        return _resolve_template(ref, slug)
    if scope == 'howto':
        return _resolve_howto(ref, slug)
    raise PortableResourceError(f'Unknown portable resource scope: {scope}')


def render_portable_resource(resource: PortableResource) -> str:
    """Render a resource using an XML-like wrapper with source metadata."""

    return (
        '<sspec-portable-resource>\n'
        f'<ref>{escape(resource.ref)}</ref>\n'
        f'<source>{escape(resource.source)}</source>\n'
        f'<read-cmd>{escape(resource.read_command)}</read-cmd>\n'
        '<content><![CDATA[\n'
        f'{_escape_cdata(resource.content)}\n'
        ']]></content>\n'
        '</sspec-portable-resource>\n'
    )


def list_builtin_skills() -> list[PortableSkillEntry]:
    """List built-in skill templates as portable skill index entries."""

    skills_root = _templates_root().joinpath('skills')
    if not skills_root.is_dir():
        return []

    entries: list[PortableSkillEntry] = []
    for skill_dir in skills_root.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir.joinpath('SKILL.md')
        if not skill_file.is_file():
            continue
        meta = _parse_frontmatter(skill_file.read_text(encoding='utf-8'))
        name = str(meta.get('name') or skill_dir.name)
        description = str(meta.get('description') or '')
        entries.append(
            PortableSkillEntry(
                name=name,
                description=description,
                location=_resource_source_path(skill_file),
                read_command=f'sspec portable read skill:{name}',
            )
        )

    return sorted(entries, key=lambda entry: entry.name)


def _render_available_skills() -> str:
    lines = ['<available_skills>']
    for skill in list_builtin_skills():
        lines.extend(
            [
                '  <skill>',
                f'    <name>{escape(skill.name)}</name>',
                f'    <description>{escape(skill.description)}</description>',
                f'    <location>{escape(skill.location)}</location>',
                f'    <read-cmd>{escape(skill.read_command)}</read-cmd>',
                '  </skill>',
            ]
        )
    lines.append('</available_skills>')
    return '\n'.join(lines)


def _parse_ref(ref: str) -> tuple[Literal['rule', 'skill', 'template', 'howto'], str]:
    if ':' not in ref:
        raise PortableResourceError('Invalid resource ref. Expected <scope:slug>.')

    scope, slug = ref.split(':', 1)
    if scope not in _ALLOWED_SCOPES:
        raise PortableResourceError(f'Unknown portable resource scope: {scope}')
    if not slug:
        raise PortableResourceError('Invalid resource ref. Expected <scope:slug>.')
    _validate_safe_slug(slug)
    return scope, slug  # type: ignore[return-value]


def _validate_safe_slug(slug: str) -> None:
    if '\\' in slug:
        raise PortableResourceError('Unsafe resource path.')

    path = PurePosixPath(slug)
    if path.is_absolute() or any(part in {'', '.', '..'} for part in path.parts):
        raise PortableResourceError('Unsafe resource path.')


def _resolve_rule(ref: str, slug: str) -> PortableResource:
    if slug != 'sspec':
        raise PortableResourceError(f'Unknown portable rule: {slug}')

    resource = _templates_root().joinpath('SSPEC.rule.md')
    content = resource.read_text(encoding='utf-8')
    rendered = render_template(content, {'SCHEMA_VERSION': SCHEMA_VERSION})
    return PortableResource(ref=ref, source=_resource_source_path(resource), content=rendered)


def _resolve_skill(ref: str, slug: str) -> PortableResource:
    parts = PurePosixPath(slug).parts
    resource = _templates_root().joinpath('skills', *parts)
    source_parts = ['sspec', 'templates', 'skills', *parts]

    if len(parts) == 1:
        resource = resource.joinpath('SKILL.md')
        source_parts.append('SKILL.md')

    return _read_existing_resource(ref=ref, source='/'.join(source_parts), resource=resource)


def _resolve_template(ref: str, slug: str) -> PortableResource:
    parts = PurePosixPath(slug).parts
    resource = _templates_root().joinpath(*parts)
    source = '/'.join(['sspec', 'templates', *parts])
    return _read_existing_resource(ref=ref, source=source, resource=resource)


def _resolve_howto(ref: str, slug: str) -> PortableResource:
    if '/' in slug:
        raise PortableResourceError('Unsafe resource path.')

    filename = slug if slug.endswith('.md') else f'{slug}.md'
    resource = _howto_root().joinpath(filename)
    source = f'sspec/howto/{filename}'
    return _read_existing_resource(ref=ref, source=source, resource=resource)


def _read_existing_resource(*, ref: str, source: str, resource: Traversable) -> PortableResource:
    del source  # Source metadata should be the installed absolute path, not logical path.
    if not resource.exists():
        raise PortableResourceError(f'Portable resource not found: {ref}')
    if resource.is_dir():
        raise PortableResourceError('Portable resource is a directory, not a readable file.')
    content = resource.read_text(encoding='utf-8')
    return PortableResource(ref=ref, source=_resource_source_path(resource), content=content)


def _resource_source_path(resource: Traversable) -> str:
    """Return an absolute local path for a package resource."""

    try:
        return str(Path(os.fspath(resource)).resolve())
    except TypeError:
        return str(resource)


def _templates_root() -> Traversable:
    return resources.files('sspec').joinpath('templates')


def _howto_root() -> Traversable:
    return resources.files('sspec').joinpath('howto')


def _parse_frontmatter(content: str) -> dict:
    if not content.startswith('---'):
        return {}

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}

    try:
        data = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def _escape_cdata(content: str) -> str:
    return content.replace(']]>', ']]]]><![CDATA[>')
