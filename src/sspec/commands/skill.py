"""sspec skill command - skill management operations."""

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from sspec.core import SCHEMA_VERSION, SspecNotFoundError, get_sspec_root, list_skills

console = Console()


@click.group()
def skill() -> None:
    """Skill management operations (list, new)."""
    pass


@skill.command(name='list')
def list_skills_cmd() -> None:
    """List all skills."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    _list_skills(sspec_root)


def _list_skills(sspec_root: Path) -> None:
    """List skills."""
    skills = list_skills(sspec_root)

    if not skills:
        console.print('[dim]No skills found.[/dim]')
        console.print()
        console.print('Create one with: sspec skill new <skill-name>')
        return

    console.print()
    console.print('[bold]Skills[/bold]')
    table = Table(show_header=True, header_style='bold')
    table.add_column('Skill')
    table.add_column('Description')
    table.add_column('File')

    for skill in skills:
        table.add_row(skill['skill'], skill['description'], skill['file'])

    console.print(table)
    console.print()
    console.print(f'[dim]Total: {len(skills)}[/dim]')


@skill.command()
@click.argument('name')
@click.option('--claude', 'to_claude', is_flag=True, help='Create skill under .claude/skills')
@click.option('--github', 'to_github', is_flag=True, help='Create skill under .github/skills')
def new(name: str, to_claude: bool, to_github: bool) -> None:
    """Create a new skill directory with SKILL.md in workspace skill locations."""

    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    project_root = sspec_root.parent

    # Determine targets
    explicit = to_claude or to_github
    targets: list[Path] = []

    candidates = [project_root / '.github' / 'skills', project_root / '.claude' / 'skills']

    if to_github:
        targets.append(candidates[0])
    if to_claude:
        targets.append(candidates[1])

    if not explicit:
        # Auto-detect: prefer existing skill dirs, then existing workspace parents, otherwise fallback to .claude/skills
        # This matches the default behavior of 'sspec project init --skill-loc .claude'
        existing_skill_dirs = [p for p in candidates if p.exists()]
        if existing_skill_dirs:
            targets.extend(existing_skill_dirs)
        else:
            existing_parents = [p for p in candidates if p.parent.exists()]
            if existing_parents:
                # Prefer .claude over .github when both exist
                claude_parent = project_root / '.claude' / 'skills'
                if claude_parent.parent in [p.parent for p in existing_parents]:
                    targets.append(claude_parent)
                else:
                    targets.extend(existing_parents)
            else:
                # Default to .claude/skills (consistent with project init)
                targets.append(candidates[1])  # candidates[1] is .claude/skills

    # Ensure unique targets
    targets = list(dict.fromkeys(targets))

    # Pre-flight conflict detection across all targets
    conflicts = [t for t in targets if (t / name).exists()]
    if conflicts:
        conflict_list = ', '.join(str(p.relative_to(project_root)) for p in conflicts)
        raise click.ClickException(f"Skill '{name}' already exists in: {conflict_list}")

    template_content = f"""---
skill: {name}
description: ""
---

# {name}

## Purpose

<!-- Describe what this skill helps the AI to accomplish -->

## Guidelines

<!-- Provide specific instructions -->

## Examples

<!-- Show example usage patterns -->
"""

    created: list[Path] = []
    for target in targets:
        skill_dir = target / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / 'SKILL.md'
        skill_file.write_text(template_content, encoding='utf-8')
        created.append(skill_dir)

    console.print(f"[green]✓[/green] Created skill '{name}'")
    for skill_dir in created:
        console.print(f'  {skill_dir.relative_to(project_root)}/')
        console.print('  └── SKILL.md')
    console.print()
    console.print('[yellow]Next:[/yellow]')
    console.print('  1. Edit SKILL.md to define your skill')
    console.print('  2. Add additional files (examples, templates) as needed')
