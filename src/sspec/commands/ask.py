"""sspec ask command - in-turn question/answer capture with persistence."""

from __future__ import annotations

import click

from sspec.core import SspecNotFoundError, get_sspec_root
from sspec.services.ask_service import (
    collect_multiline_input,
    resolve_question,
    write_ask_record,
)


@click.command(name='ask')
@click.option('--name', required=True, help='Ask topic/name (used in filename)')
@click.option(
    '--question',
    required=True,
    help="Question text (multi-line supported). Use '-' to read full stdin.",
)
@click.option('--why', required=False, help='Why this question is being asked (optional)')
def ask(name: str, question: str, why: str | None) -> None:
    """Ask user for input and save the Q/A record under .sspec/asks/."""

    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException(
            "Not a sspec project. Run 'sspec project init' first."
        ) from None

    resolved_question = resolve_question(question_opt=question)
    if not resolved_question.strip():
        raise click.ClickException('Question is empty')

    prompt = (
        'Please answer the question below.\n\n'
        f'{resolved_question.strip()}\n\n'
        '(Tip: type END on a new line to finish)'
    )

    answer = collect_multiline_input(prompt=prompt)

    record_path = write_ask_record(
        sspec_root=sspec_root,
        name=name,
        why=why,
        question=resolved_question,
        answer=answer,
    )

    try:
        rel = record_path.relative_to(sspec_root.parent)
        rel_str = str(rel).replace('\\', '/')
    except ValueError:
        rel_str = str(record_path)

    click.echo(answer)
    click.echo('')
    click.echo(f'The ASK FILE is recorded to "{rel_str}"')
