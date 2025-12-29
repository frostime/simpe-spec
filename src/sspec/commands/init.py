"""sspec init command."""

from pathlib import Path

import click
from rich.console import Console

from sspec.core import (
    SCHEMA_VERSION,
    SSPEC_DIR,
    UPDATABLE_FILES,
    USER_FILES,
    copy_template,
    find_sspec_root,
    get_template_dir,
)

console = Console()


ROOT_AGENT_PROMPT = f"""
<!-- SSPEC:START -->
# Simple-Spec Instructions

SSPEC_SCHEMA::{SCHEMA_VERSION}

These instructions are for AI assistants working in this project.

## When to Read `.sspec/AGENTS.md`

Open `.sspec/AGENTS.md` when the request:
- Involves planning, proposals, or multi-step changes
- Introduces new features, architecture changes, or breaking changes
- Seems ambiguous and you need authoritative context before coding
- Mentions "change", "proposal", "spec", "plan", or "handover"

## Quick Commands

| Command | Purpose |
|---------|---------|
| `/propose <n>` | Create new change proposal |
| `/status` | Report current state |
| `/pivot` | Record direction change |
| `/handover` | Generate session handover |
| `/context` | Reload project context |
| `/archive` | Archive completed change |

## First Session?

1. Read `.sspec/knowledge/index.md` for project context
2. Check `.sspec/changes/` for active work
3. Read relevant `handover.md` for previous state

Keep this block so `sspec update` can refresh instructions.
<!-- SSPEC:END -->
""".strip()


@click.command()
@click.option('--force', is_flag=True, help='Overwrite existing .sspec directory')
def init(force: bool) -> None:
    """Initialize .sspec directory in current project."""
    sspec_path = Path.cwd() / SSPEC_DIR

    if sspec_path.exists() and not force:
        raise click.ClickException(
            f'{SSPEC_DIR} already exists. Use --force to reinitialize, '
            f"or 'sspec update' to update templates."
        )

    template_dir = get_template_dir()

    # Create directory structure
    sspec_path.mkdir(parents=True, exist_ok=True)
    (sspec_path / 'knowledge').mkdir(exist_ok=True)
    (sspec_path / 'changes').mkdir(exist_ok=True)
    (sspec_path / 'changes' / 'archive').mkdir(exist_ok=True)
    (sspec_path / 'requests').mkdir(exist_ok=True)
    (sspec_path / 'prompts').mkdir(exist_ok=True)

    # Copy templates
    copy_template(template_dir / 'AGENTS.md', sspec_path / 'AGENTS.md')
    copy_template(template_dir / 'handover.md', sspec_path / 'handover.md')
    copy_template(
        template_dir / 'knowledge' / 'index.md', sspec_path / 'knowledge' / 'index.md'
    )

    # Copy prompt templates
    prompts_template = template_dir / 'prompts'
    if prompts_template.exists():
        copy_template(prompts_template, sspec_path / 'prompts')

    # Create .gitignore
    (sspec_path / '.gitignore').touch()
    (sspec_path / '.gitignore').write_text('*', encoding='utf-8')

    # Create metadata for update tracking
    _create_meta(sspec_path)

    # Root AGENTS.md
    root_agents_path = Path.cwd() / 'AGENTS.md'
    if not root_agents_path.exists():
        root_agents_path.write_text(ROOT_AGENT_PROMPT, encoding='utf-8')
    else:
        content = root_agents_path.read_text(encoding='utf-8')
        if '<!-- SSPEC:START -->' not in content:
            with open(root_agents_path, 'a', encoding='utf-8') as f:
                f.write('\n\n' + ROOT_AGENT_PROMPT)

    console.print(f'[green]✓[/green] Initialized {SSPEC_DIR}')
    console.print()
    console.print('[cyan]Structure:[/cyan]')
    console.print(f'  {SSPEC_DIR}/')
    console.print('  ├── AGENTS.md           # AI instructions (entry point)')
    console.print('  ├── knowledge/')
    console.print('  │   └── index.md        # Project context')
    console.print('  ├── changes/')
    console.print('  │   └── archive/')
    console.print('  ├── prompts/            # Command definitions')
    console.print('  └── handover.md         # Global handover')
    console.print()
    console.print('[yellow]Next steps:[/yellow]')
    console.print('  1. Edit .sspec/knowledge/index.md with project info')
    console.print('  2. Run: sspec new <change-name>')
    console.print('  3. Tell AI: "Read .sspec/AGENTS.md"')


def _create_meta(sspec_root: Path) -> None:
    """Create initial metadata file for update tracking."""
    import hashlib
    import json
    from datetime import datetime

    from sspec import __version__

    def compute_hash(path: Path) -> str:
        if not path.exists():
            return ''
        content = path.read_text(encoding='utf-8')
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

    # Files to track (combine updatable and user files)
    tracked_files = UPDATABLE_FILES + USER_FILES

    files = {}
    for rel_path in tracked_files:
        file_path = sspec_root / rel_path
        if file_path.exists():
            files[rel_path] = compute_hash(file_path)

    meta = {
        'schema_version': SCHEMA_VERSION,
        'package_version': __version__,
        'initialized_at': datetime.now().isoformat(timespec='seconds'),
        'files': files,
    }

    meta_path = sspec_root / '.meta.json'
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8')
