"""sspec CLI - main entry point."""

import click
from rich.console import Console

from sspec.commands import archive, init, list_cmd, new, prompt, request, status, update

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option()
def main(ctx: click.Context) -> None:
    """sspec - Lightweight AI collaboration spec for solo/small projects."""
    if ctx.invoked_subcommand is None:
        # Default behavior: show status if initialized, else show help
        from sspec.core import find_sspec_root

        if find_sspec_root():
            ctx.invoke(status.status)
        else:
            click.echo(ctx.get_help())


main.add_command(init.init)
main.add_command(new.new)
main.add_command(update.update)
main.add_command(request.request)
main.add_command(list_cmd.list_changes_cmd, name="list")
main.add_command(status.status)
main.add_command(archive.archive)
main.add_command(prompt.prompt)


if __name__ == "__main__":
    main()
