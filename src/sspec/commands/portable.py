"""sspec portable command - no-project Agent workflow resources."""

from __future__ import annotations

import click

from sspec.services.portable_service import (
    PortableResourceError,
    read_portable_resource,
    render_portable_index,
)


@click.group(invoke_without_command=True)
@click.pass_context
def portable(ctx: click.Context) -> None:
    """Print portable sspec Agent instructions without initializing a project."""

    if ctx.invoked_subcommand is None:
        click.echo(render_portable_index(), nl=False)


@portable.command(name='read')
@click.argument('resource_ref')
def read_cmd(resource_ref: str) -> None:
    """Read a built-in portable resource by <scope:slug>."""

    try:
        click.echo(read_portable_resource(resource_ref), nl=False)
    except PortableResourceError as e:
        raise click.ClickException(str(e)) from None
