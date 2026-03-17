"""sspec howto command - lightweight HOWTO document access."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from sspec.core import SSPEC_DIR, find_sspec_dir
from sspec.services.howto_service import (
    HowtoInfo,
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
    """Best-effort resolve `.sspec/` directory.

    HOWTO is intentionally usable without a fully initialized sspec project:
    - If `.sspec/` exists, merge builtin + `.sspec/howto/`.
    - Otherwise, fall back to builtin-only.
    """

    return find_sspec_dir() or Path.cwd() / SSPEC_DIR


def _resolve_output_format(
    ctx: click.Context,
    local_output_format: str | None = None,
) -> OutputFormat:
    """Resolve effective HOWTO output format from local option or parent contexts."""

    if local_output_format in {'plain', 'rich'}:
        return local_output_format  # type: ignore[return-value]

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


def _render_plain_list(items: tuple[HowtoInfo, ...], *, show_type: bool = False) -> None:
    """Render HOWTO list in YAML-like plain text."""

    for item in items:
        description = item.description.replace('\n', ' ').strip()
        click.echo(f'- name: {item.name}')
        click.echo(f'  source: {item.source}')
        if show_type and item.type:
            click.echo(f'  type: {item.type}')
        if description:
            click.echo(f'  desc: {description}')
    click.echo('')
    click.echo('Run `sspec howto [<name>...]` to read HOWTO. Multi-names are supported.')


def _compose_display_body(name: str, body: str) -> str:
    """Add a display header when the stored HOWTO body has none."""

    stripped = body.strip()
    if stripped.startswith('#'):
        return stripped
    if not stripped:
        return f'# {name}'
    return f'# {name}\n\n{stripped}'


def _render_plain_howto(*, name: str, body: str) -> None:
    """Render a HOWTO body in agent-friendly plain text."""

    click.echo(f'===== HOWTO/{name} =====')
    click.echo(_compose_display_body(name, body))


@click.group(cls=ImplicitReadGroup, invoke_without_command=True)
@click.option('--list', 'list_only', is_flag=True, help='List all HOWTO documents')
@click.option(
    '--format',
    'output_format',
    type=click.Choice(['plain', 'rich']),
    default=None,
    help='Output format for `list` and `read`.',
)
@click.pass_context
def howto(ctx: click.Context, list_only: bool, output_format: str | None) -> None:
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
@click.option(
    '--format',
    'output_format',
    type=click.Choice(['plain', 'rich']),
    default=None,
    help='Override output format for this command.',
)
@click.option(
    '--type',
    'howto_type',
    default=None,
    help='Filter HOWTOs by type (e.g. design-dimension).',
)
@click.pass_context
def list_cmd(ctx: click.Context, output_format: str | None, howto_type: str | None) -> None:
    """List all available HOWTO documents."""

    sspec_root = find_sspec_dir()
    catalog = collect_howtos(sspec_root)
    effective_format = _resolve_output_format(ctx, output_format)
    _print_warnings(catalog.warnings, output_format=effective_format)

    items = catalog.items
    if howto_type:
        items = tuple(item for item in items if item.type == howto_type)

    if not items:
        msg = (
            f"No HOWTOs matching type '{howto_type}'."
            if howto_type
            else 'No HOWTO documents found.'
        )
        if effective_format == 'rich':
            console.print(f'[dim]{msg}[/dim]')
        else:
            click.echo(msg)
        return

    has_types = any(item.type for item in items)

    if effective_format == 'plain':
        _render_plain_list(items, show_type=has_types)
        return

    table = Table(title='Available HOWTO documents')
    table.add_column('Name', style='cyan')
    table.add_column('Description', style='dim')
    if has_types:
        table.add_column('Type', style='green')
    table.add_column('Source', style='magenta')

    for item in items:
        row = [item.name, item.description]
        if has_types:
            row.append(item.type or '')
        row.append(item.source)
        table.add_row(*row)

    console.print(table)
    console.print(f'[dim]{len(items)} HOWTO document(s)[/dim]')


@howto.command(name='read')
@click.argument('names', nargs=-1, required=True)
@click.option(
    '--format',
    'output_format',
    type=click.Choice(['plain', 'rich']),
    default=None,
    help='Override output format for this command.',
)
@click.pass_context
def read_cmd(ctx: click.Context, names: tuple[str, ...], output_format: str | None) -> None:
    """Read one or more HOWTO documents by name."""

    sspec_root = find_sspec_dir()
    effective_format = _resolve_output_format(ctx, output_format)
    rendered_items: list[tuple[str, str, str, str]] = []
    warning_list: list[str] = []

    for name in names:
        howto_info, warnings = resolve_howto(sspec_root, name)
        warning_list.extend(warnings)

        if howto_info is None:
            raise click.ClickException(
                f"HOWTO '{name}' not found. Use 'sspec howto --list' to browse."
            )

        rendered_items.append(
            (
                howto_info.name,
                howto_info.source,
                howto_info.description,
                read_howto_body(howto_info.path),
            )
        )

    _print_warnings(tuple(dict.fromkeys(warning_list)), output_format=effective_format)

    for index, (name, source, description, body) in enumerate(rendered_items):
        if effective_format == 'plain':
            _render_plain_howto(name=name, body=body)
        else:
            if description:
                # Print description outside the panel so it stays plain/ASCII in captured output.
                console.print(f'[dim]{description}[/dim]')
                console.print()

            console.print(
                Panel(
                    Markdown(_compose_display_body(name, body)),
                    title=f'HOWTO: {name}',
                    subtitle=source,
                    border_style='cyan',
                )
            )

        if index < len(rendered_items) - 1:
            if effective_format == 'plain':
                click.echo('')
                click.echo('')
            else:
                console.print()
                console.print()


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
