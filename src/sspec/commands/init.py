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
    get_template_dir,
)

console = Console()


ROOT_AGENT_STUB = f"""
<!-- SSPEC:START -->
# sspec

SSPEC_SCHEMA::{SCHEMA_VERSION}

This project uses sspec for AI collaboration.

## 🚀 Quick Start

**User mentioned these keywords?** Read `@/.sspec/AGENTS.md` immediately:
- sspec
- "new feature" / "create change" / `@new`
- "change plans" / "pivot" / `@pivot`
- "end session" / "handover" / `@handover`
- "status" / "progress" / `@status`
- "go on changes" / `@context`

## 📍 Core Files

- `@/.sspec/AGENTS.md` — Complete workflow instructions
- `@/.sspec/knowledge/index.md` — Project context
- `@/.sspec/changes/<name>/spec.md` — Current change plan
- `@/.sspec/changes/<name>/handover.md` — Previous session state

## ⚡ Cross Session Principles

1. **Session start**: Read handover.md (where we left off)
2. **Task completed**: Update spec.md progress
3. **Session end**: Write handover.md (where to continue)

Full instructions: `@/.sspec/AGENTS.md`

<!-- Keep this block for `sspec update` to refresh -->
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

    # Copy templates
    copy_template(template_dir / 'AGENTS.md', sspec_path / 'AGENTS.md')
    copy_template(template_dir / 'handover.md', sspec_path / 'handover.md')
    copy_template(template_dir / 'knowledge' / 'index.md', sspec_path / 'knowledge' / 'index.md')

    # Create .gitignore
    (sspec_path / '.gitignore').touch()
    (sspec_path / '.gitignore').write_text('*', encoding='utf-8')

    # Create metadata for update tracking
    _create_meta(sspec_path)

    # Root AGENTS.md stub
    root_agents_path = Path.cwd() / 'AGENTS.md'
    if not root_agents_path.exists():
        root_agents_path.write_text(ROOT_AGENT_STUB, encoding='utf-8')
    else:
        content = root_agents_path.read_text(encoding='utf-8')
        if '<!-- SSPEC:START -->' not in content:
            with open(root_agents_path, 'a', encoding='utf-8') as f:
                f.write('\n\n' + ROOT_AGENT_STUB)

    console.print(f'[green]✓[/green] Initialized {SSPEC_DIR}')
    console.print()
    console.print('[cyan]Structure:[/cyan]')
    console.print(f'  {SSPEC_DIR}/')
    console.print('  ├── AGENTS.md           # AI instructions')
    console.print('  ├── knowledge/')
    console.print('  │   └── index.md        # Project context')
    console.print('  ├── changes/')
    console.print('  │   └── archive/')
    console.print('  ├── requests/')
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
