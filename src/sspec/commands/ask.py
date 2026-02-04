"""sspec ask command - two-step Q&A with file-based workflow."""

from __future__ import annotations

from pathlib import Path

import click

from sspec.core import SspecNotFoundError, get_sspec_root
from sspec.services.ask_service import (
    convert_ask_to_md,
    create_ask_template,
    execute_ask_prompt,
    save_ask_answer,
)


@click.group(name='ask')
def ask_group() -> None:
    """Manage ask prompts for mid-execution user consultation."""
    pass


@ask_group.command(name='create')
@click.option(
    '--name',
    default='ask',
    help='Ask name (lowercase letters and underscores only)',
)
def ask_create(name: str) -> None:
    """Create a new ask template (.py file) for editing."""

    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException(
            "Not a sspec project. Run 'sspec project init' first."
        ) from None

    try:
        py_path = create_ask_template(sspec_root=sspec_root, name=name)
    except ValueError as e:
        raise click.ClickException(str(e)) from None

    try:
        rel = py_path.relative_to(sspec_root.parent)
        rel_str = str(rel).replace('\\', '/')
    except ValueError:
        rel_str = str(py_path)

    click.echo(f'✓ Created ask template: {rel_str}')
    click.echo('')
    click.echo('Next steps:')
    click.echo(f'  1. Edit REASON and QUESTION in {rel_str}')
    click.echo(f'  2. Run: sspec ask prompt {rel_str}')


@ask_group.command(name='prompt')
@click.argument('ask_file', type=click.Path(exists=True, path_type=Path))
def ask_prompt(ask_file: Path) -> None:
    """Execute ask prompt, collect answer, and convert to .md."""

    if ask_file.suffix != '.py':
        raise click.ClickException(
            f'Ask file must be .py file, got: {ask_file.suffix}'
        )

    try:
        # Execute prompt and get answer
        answer = execute_ask_prompt(ask_file_path=ask_file)

        # Save answer to .py file
        save_ask_answer(ask_file_path=ask_file, answer=answer)

        # Convert to .md and cleanup .py
        md_path = convert_ask_to_md(py_path=ask_file)

        try:
            sspec_root = get_sspec_root()
            rel = md_path.relative_to(sspec_root.parent)
            rel_str = str(rel).replace('\\', '/')
        except (SspecNotFoundError, ValueError):
            rel_str = str(md_path)

        click.echo('')
        click.echo(f'✓ Ask recorded to: {rel_str}')
        click.echo('')
        click.echo('Answer:')
        click.echo(answer)

    except (FileNotFoundError, AttributeError, ImportError) as e:
        raise click.ClickException(str(e)) from None

