"""sspec howto command - lightweight HOWTO document access."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from sspec.core import SspecNotFoundError, get_sspec_root
from sspec.services.howto_service import (
    collect_howtos,
    create_project_howto,
    read_howto_body,
    resolve_howto,
)

console = Console()
OutputFormat = Literal['plain', 'rich']


class ImplicitReadGroup(click.Group):
    """Map `sspec howto <name>` to `sspec howto read <name>`."""

    def resolve_command(self, ctx: click.Context, args: list[str]):
        """Resolve unknown first positional argument as the `read` subcommand."""

        if not args or args[0].startswith('-'):
            return super().resolve_command(ctx, args)

        cmd = self.get_command(ctx, args[0])
        if cmd is not None:
            return args[0], cmd, args[1:]

        read_cmd = self.get_command(ctx, 'read')
        if read_cmd is None:
            return super().resolve_command(ctx, args)
        return 'read', read_cmd, args


def _get_sspec_root_or_fail() -> Path:
    """Resolve `.sspec/` root or raise a CLI error."""

    try:
        return get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None


def _get_output_format(ctx: click.Context) -> OutputFormat:
    """Get current HOWTO output format from the root command context."""

    current: click.Context | None = ctx
    while current is not None:
        if isinstance(current.obj, dict):
            value = current.obj.get('output_format')
            if value in {'plain', 'rich'}:
                return value
        current = current.parent
    return 'plain'


def _print_warnings(warnings: tuple[str, ...], *, output_format: OutputFormat) -> None:
    """Print non-fatal HOWTO registry warnings."""

    for warning in warnings:
        if output_format == 'rich':
            console.print(f'[yellow]Warning:[/yellow] {warning}')
        else:
            click.echo(f'WARNING: {warning}')


def _render_plain_list(catalog) -> None:
    """Render HOWTO list in compact plain text."""

    click.echo('name\tsource\tdescription\tfile')
    for item in catalog.items:
        description = item.description.replace('\t', ' ').replace('\n', ' ')
        click.echo(f'{item.name}\t{item.source}\t{description}\t{item.file}')


def _render_plain_howto(*, name: str, source: str, file: str, description: str, body: str) -> None:
    """Render a HOWTO body in agent-friendly plain text."""

    click.echo(f'name: {name}')
    click.echo(f'source: {source}')
    click.echo(f'file: {file}')
    if description:
        click.echo(f'desc: {description}')
    click.echo('---')
    if body:
        click.echo(body)


@click.group(cls=ImplicitReadGroup, invoke_without_command=True)
@click.option('--list', 'list_only', is_flag=True, help='List all HOWTO documents')
@click.option(
    '--format',
    'output_format',
    type=click.Choice(['plain', 'rich']),
    default='plain',
    show_default=True,
    help='Output format for `list` and `read`.',
)
@click.pass_context
def howto(ctx: click.Context, list_only: bool, output_format: OutputFormat) -> None:
    """Read, list, and scaffold HOWTO documents.

    `sspec howto <name>` is shorthand for `sspec howto read <name>`.
    By default, `list` and `read` use agent-friendly plain text output.
    """

    ctx.ensure_object(dict)
    ctx.obj['output_format'] = output_format

    if ctx.invoked_subcommand is None:
        if list_only:
            ctx.invoke(list_cmd)
            return
        raise click.UsageError('Provide a HOWTO name or use --list.')


@howto.command(name='list')
@click.pass_context
def list_cmd(ctx: click.Context) -> None:
    """List all available HOWTO documents."""

    sspec_root = _get_sspec_root_or_fail()
    catalog = collect_howtos(sspec_root)
    output_format = _get_output_format(ctx)
    _print_warnings(catalog.warnings, output_format=output_format)

    if not catalog.items:
        if output_format == 'rich':
            console.print('[dim]No HOWTO documents found.[/dim]')
        else:
            click.echo('No HOWTO documents found.')
        return

    if output_format == 'plain':
        _render_plain_list(catalog)
        return

    table = Table(title='Available HOWTO documents')
    table.add_column('Name', style='cyan')
    table.add_column('Description', style='dim')
    table.add_column('Source', style='magenta')

    for item in catalog.items:
        table.add_row(item.name, item.description, item.source)

    console.print(table)
    console.print(f'[dim]{len(catalog.items)} HOWTO document(s)[/dim]')


@howto.command(name='read')
@click.argument('name')
@click.pass_context
def read_cmd(ctx: click.Context, name: str) -> None:
    """Read a HOWTO document by name."""

    sspec_root = _get_sspec_root_or_fail()
    howto_info, warnings = resolve_howto(sspec_root, name)
    output_format = _get_output_format(ctx)
    _print_warnings(warnings, output_format=output_format)

    if howto_info is None:
        raise click.ClickException(f"HOWTO '{name}' not found. Use 'sspec howto --list' to browse.")

    body = read_howto_body(howto_info.path)
    if output_format == 'plain':
        _render_plain_howto(
            name=howto_info.name,
            source=howto_info.source,
            file=howto_info.file,
            description=howto_info.description,
            body=body,
        )
        return

    subtitle = f'{howto_info.source} • {howto_info.file}'
    title = f'HOWTO: {howto_info.name}'
    if howto_info.description:
        console.print(f'[dim]{howto_info.description}[/dim]')
        console.print()

    console.print(
        Panel(
            Markdown(body),
            title=title,
            subtitle=subtitle,
            border_style='cyan',
        )
    )


@howto.command(name='new')
@click.argument('name')
def new_cmd(name: str) -> None:
    """Create a new project HOWTO under `.sspec/howto/`."""

    sspec_root = _get_sspec_root_or_fail()

    try:
        howto_path = create_project_howto(sspec_root, name)
    except (FileExistsError, ValueError, OSError) as e:
        raise click.ClickException(str(e)) from None

    rel_path = howto_path.relative_to(sspec_root.parent).as_posix()
    console.print(f"[green][OK][/green] Created HOWTO '{name}'")
    console.print(f'  {rel_path}')
    console.print()
    console.print('[yellow]Next:[/yellow]')
    console.print('  1. Edit the frontmatter name/desc fields if needed')
    console.print('  2. Keep the guide focused and short')
    console.print('  3. Read it with `sspec howto <name>`')
