"""sspec CLI - main entry point."""

import click
from rich.console import Console

from sspec.commands import ask, change, doc, project, request, skill

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option()
def main(ctx: click.Context) -> None:
    """sspec - Lightweight AI collaboration spec for solo/small projects."""
    if ctx.invoked_subcommand is None:
        from sspec.core import find_sspec_root

        if find_sspec_root():
            ctx.invoke(project.status)
        else:
            click.echo(ctx.get_help())


# Register command groups
main.add_command(project.project)
main.add_command(change.change)
main.add_command(skill.skill)
main.add_command(request.request)
main.add_command(doc.doc)
main.add_command(ask.ask)


if __name__ == '__main__':
    main()
