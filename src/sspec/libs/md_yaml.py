"""Markdown frontmatter YAML utilities.

Provides centralized functions for parsing and updating YAML frontmatter
in markdown files. Eliminates duplication across request_service.py, core.py, etc.
"""

from typing import Any

import yaml


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown content with optional YAML frontmatter

    Returns:
        Tuple of (metadata dict, body content without frontmatter)
        If no frontmatter, returns ({}, original content)

    Examples:
        >>> content = "---\\nkey: value\\n---\\nBody"
        >>> meta, body = parse_frontmatter(content)
        >>> meta
        {'key': 'value'}
        >>> body
        'Body'
    """
    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        # On YAML error, treat the whole third part as body
        body = parts[2].lstrip('\n') if len(parts) > 2 else content
        return {}, body

    if not isinstance(meta, dict):
        meta = {}

    body = parts[2].lstrip('\n') if len(parts) > 2 else ''
    return meta, body


def update_frontmatter(content: str, updates: dict[str, Any]) -> str:
    """Update YAML frontmatter with new values.

    Args:
        content: Markdown content with optional YAML frontmatter
        updates: Dictionary of fields to update/add

    Returns:
        Updated markdown content with modified frontmatter

    Examples:
        >>> content = "---\\nstatus: OPEN\\n---\\nBody"
        >>> updated = update_frontmatter(content, {'status': 'DONE'})
        >>> 'status: DONE' in updated
        True
    """
    meta, body = parse_frontmatter(content)
    meta.update(updates)

    new_yaml = yaml.dump(meta, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return f'---\n{new_yaml}---\n{body}'
