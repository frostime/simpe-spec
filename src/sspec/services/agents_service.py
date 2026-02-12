"""Services related to the root AGENTS.md SSPEC block."""

from __future__ import annotations

import re
from pathlib import Path

from sspec.core import render_template


def update_root_agents_block(
    *,
    project_root: Path,
    template_agents_path: Path,
    replacements: dict[str, str],
    dry_run: bool = False,
) -> bool:
    """Update the SSPEC block in the project's root AGENTS.md.

    Returns True if the file would change (dry_run=True) or was changed.
    """
    if not template_agents_path.exists():
        return False

    rendered = render_template(
        template_agents_path.read_text(encoding='utf-8'),
        replacements,
    )

    root_agents = project_root / 'AGENTS.md'

    if not root_agents.exists():
        if not dry_run:
            root_agents.write_text(rendered, encoding='utf-8')
        return True

    content = root_agents.read_text(encoding='utf-8').strip()

    start_marker = '<!-- SSPEC:START -->'
    end_marker = '<!-- SSPEC:END -->'

    if start_marker not in content:
        if not dry_run:
            with open(root_agents, 'a', encoding='utf-8') as f:
                f.write('\n\n' + rendered)
        return True

    pattern = re.compile(
        rf'{re.escape(start_marker)}.*?{re.escape(end_marker)}',
        re.DOTALL,
    )

    new_content = pattern.sub(rendered, content)

    if new_content != content:
        if not dry_run:
            root_agents.write_text(new_content, encoding='utf-8')
        return True

    return False
