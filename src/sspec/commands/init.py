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
    render_template,
)

console = Console()


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
    common_replacements = {
        'SCHEMA_VERSION': SCHEMA_VERSION,
        'SCHEMA': SCHEMA_VERSION,
    }

    # Create directory structure
    sspec_path.mkdir(parents=True, exist_ok=True)
    # Remove legacy spec folder; only create required structure
    (sspec_path / 'changes').mkdir(exist_ok=True)
    (sspec_path / 'changes' / 'archive').mkdir(exist_ok=True)
    (sspec_path / 'requests').mkdir(exist_ok=True)
    (sspec_path / 'skills').mkdir(exist_ok=True)

    # Copy templates
    copy_template(
        template_dir / 'project.md',
        sspec_path / 'project.md',
        {'TODO': 'TODO', **common_replacements},
    )
    # Global handover removed per new structure

    # Create .gitignore
    (sspec_path / '.gitignore').touch()
    (sspec_path / '.gitignore').write_text('*', encoding='utf-8')

    # Create metadata for update tracking
    _create_meta(sspec_path)

    # Root AGENTS.md
    """
    基本理念

    Root Agents 内容不要超过 150 行
    就算有多余的想要添加的，也可以放到 skills/ 目录下，然后在 Root Agents 里面放摘要和引用

    Root Agents 应当多以明确的指令为主；直接告诉 Agent 应该做什么，应该如何同用户协作
    """
    root_agents_path = Path.cwd() / 'AGENTS.md'
    root_agents_content = (template_dir / 'Agents.md').read_text(encoding='utf-8')
    rendered_root_agents = render_template(root_agents_content, common_replacements)

    if not root_agents_path.exists():
        root_agents_path.write_text(rendered_root_agents, encoding='utf-8')
    else:
        content = root_agents_path.read_text(encoding='utf-8')
        start_marker = '<!-- SSPEC:START -->'
        end_marker = '<!-- SSPEC:END -->'
        if start_marker in content and end_marker in content:
            import re

            pattern = re.compile(rf'{re.escape(start_marker)}.*?{re.escape(end_marker)}', re.DOTALL)
            new_content = pattern.sub(rendered_root_agents, content)
            if new_content != content:
                root_agents_path.write_text(new_content, encoding='utf-8')
        else:
            with open(root_agents_path, 'a', encoding='utf-8') as f:
                f.write('\n\n' + rendered_root_agents)

    console.print(f'[green]✓[/green] Initialized {SSPEC_DIR}')
    console.print()
    console.print('[cyan]Structure:[/cyan]')
    console.print(f'  {SSPEC_DIR}/')
    console.print('  ├── project.md          # Project overview and conventions')
    console.print('  ├── changes/')
    console.print('  │   └── archive/')
    console.print('  ├── requests/')
    console.print('  └── skills/             # Reusable knowledge & prompts')
    console.print()
    console.print('[yellow]Next steps:[/yellow]')
    console.print('  1. Fill in .sspec/project.md with project context and constraints')
    console.print('  2. Run: sspec change <change-name>')
    console.print('  3. Tell AI: "Read AGENTS.md"')


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
