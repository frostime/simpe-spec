"""sspec cmd command - project command registry."""

from pathlib import Path
from typing import cast

import click
import questionary
from click.shell_completion import CompletionItem
from rich.console import Console
from rich.table import Table

from sspec.core import SspecNotFoundError, get_sspec_root
from sspec.services.cmd_service import (
    CommandExistsError,
    CommandInfo,
    CommandNotFoundError,
    ScriptStrategy,
    add_command,
    handle_script_file,
    load_registry,
    remove_command,
    run_command,
    suggest_invoke_pattern,
)

console = Console()


class CommandNameParam(click.ParamType):
    """Custom parameter type for command name with shell completion."""

    name = 'command'

    def shell_complete(self, ctx: click.Context, param: click.Parameter, incomplete: str):
        """Provide shell completion for command names."""
        try:
            sspec_root = get_sspec_root()
        except SspecNotFoundError:
            return []

        commands = load_registry(sspec_root)
        completions = []
        for name in commands.keys():
            if name.startswith(incomplete):
                completions.append(CompletionItem(name, type=self.name))
        return completions


COMMAND_NAME_PARAM = CommandNameParam()


# ============================================================================
# Helpers
# ============================================================================


def _suggest_name_from_invoke(invoke: str) -> str:
    """Guess a reasonable command name from an invoke string."""
    # "uv run ruff check src/" → "ruff"
    # "npm test" → "test"
    # "python scripts/migrate.py" → "migrate"
    parts = invoke.strip().split()

    # Skip common prefixes
    skip = {
        'uv',
        'run',
        'npx',
        'python',
        'python3',
        'node',
        'bash',
        'sh',
        'powershell',
        '-File',
        '-c',
    }

    for part in parts:
        token = Path(part).stem if ('/' in part or '\\' in part) else part
        if token.lower() not in skip and not token.startswith('-'):
            return token.lower()

    return parts[-1].lower() if parts else 'cmd'


def _suggest_name_from_path(script_path: Path) -> str:
    """Guess a command name from a script filename."""
    return script_path.stem.lower().replace(' ', '-')


# ============================================================================
# CLI Group
# ============================================================================


@click.group()
def cmd() -> None:
    """Project command registry — register, list, and run project commands."""
    pass


# ============================================================================
# sspec cmd add
# ============================================================================


@cmd.command()
@click.option('--name', 'cmd_name', default=None, help='Command name (skip prompt)')
def add(cmd_name: str | None) -> None:
    """Register a new project command (interactive)."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    # 1. Choose type
    cmd_type = questionary.select(
        'Command type:',
        choices=[
            questionary.Choice(
                'cmd-line — Shell command (e.g. npm test, uv run ruff check src/)',
                value='cmd-line',
            ),
            questionary.Choice(
                'script  — Managed script file (e.g. python scripts/deploy.py)',
                value='script',
            ),
        ],
    ).ask()

    if cmd_type is None:
        return  # User cancelled

    script_file: str | None = None
    invoke: str = ''
    strategy: ScriptStrategy = 'copy'

    if cmd_type == 'cmd-line':
        # 2a. cmd-line: get invoke string
        invoke = questionary.text('Command to run:').ask()
        if not invoke:
            return

        default_name = cmd_name or _suggest_name_from_invoke(invoke)

    else:
        # 2b. script: get file path
        script_path_str = questionary.path(
            'Script file path:',
            # only_files=True,
        ).ask()
        if not script_path_str:
            return

        source_path = Path(script_path_str)
        if not source_path.exists():
            raise click.ClickException(f'File not found: {source_path}')
        if not source_path.is_file():
            raise click.ClickException(f'Not a file: {source_path}')

        # Auto-detect invoke pattern
        suggested = suggest_invoke_pattern(source_path)
        if suggested:
            invoke = questionary.text(
                'Invoke pattern:',
                default=suggested,
            ).ask()
        else:
            invoke = questionary.text(
                'Invoke pattern (use {script} as placeholder):',
            ).ask()

        if not invoke:
            return

        default_name = cmd_name or _suggest_name_from_path(source_path)

        strategy_raw = questionary.select(
            'Script handling strategy:',
            choices=[
                questionary.Choice(
                    'ref  — Only reference script location (no copy/move)',
                    value='ref',
                ),
                questionary.Choice(
                    'move — Move script to .sspec/commands/',
                    value='move',
                ),
                questionary.Choice(
                    'copy — Copy script to .sspec/commands/',
                    value='copy',
                ),
            ],
            default='ref',
        ).ask()
        if strategy_raw is None:
            return

        strategy = cast(ScriptStrategy, strategy_raw)

        script_file = handle_script_file(sspec_root, source_path, strategy)

    # 3. Name
    if cmd_name is None:
        cmd_name = questionary.text('Name:', default=default_name).ask()
    if not cmd_name:
        return

    # 4. Description
    description = questionary.text('Description:').ask()
    if description is None:
        return

    # 5. Save
    command = CommandInfo(
        name=cmd_name,
        description=description,
        type=cmd_type,
        invoke=invoke,
        script_file=script_file,
        script_strategy=strategy,
    )

    try:
        add_command(sspec_root, command)
    except CommandExistsError:
        raise click.ClickException(
            f"Command '{cmd_name}' already exists. "
            f'Remove it first with: sspec cmd remove {cmd_name}'
        ) from None

    console.print(f'[green][OK][/green] Added command "{cmd_name}" ({cmd_type})')
    console.print(f'  invoke: {invoke}')
    if script_file:
        console.print(f'  script: .sspec/commands/{script_file}')


# ============================================================================
# sspec cmd list
# ============================================================================


@cmd.command('list')
def list_cmd() -> None:
    """List all registered project commands."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    commands = load_registry(sspec_root)

    if not commands:
        console.print('[dim]No commands registered.[/dim]')
        console.print()
        console.print('Add one with: sspec cmd add')
        return

    table = Table(show_header=True, header_style='bold')
    table.add_column('Name', style='cyan')
    table.add_column('Type', style='dim')
    table.add_column('Description')
    table.add_column('Invoke', style='green')

    for name, cmd_info in commands.items():
        table.add_row(
            name,
            cmd_info.type,
            cmd_info.description,
            cmd_info.invoke,
        )

    console.print()
    console.print(table)
    console.print()
    console.print(f'[dim]Total: {len(commands)} command(s)[/dim]')
    console.print('[dim]Run with: sspec cmd run <name>[/dim]')


# ============================================================================
# sspec cmd remove
# ============================================================================


@cmd.command()
@click.argument('name', type=COMMAND_NAME_PARAM)
def remove(name: str) -> None:
    """Remove a registered command."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    commands = load_registry(sspec_root)
    if name not in commands:
        raise click.ClickException(
            f"Command '{name}' not found. Run 'sspec cmd list' to see available commands."
        )

    cmd_info = commands[name]
    detail = f'  invoke: {cmd_info.invoke}'
    if cmd_info.script_file:
        detail += f'\n  script: .sspec/commands/{cmd_info.script_file}'

    console.print(f'Removing command "{name}" ({cmd_info.type})')
    console.print(detail)

    if not questionary.confirm('Confirm removal?', default=False).ask():
        console.print('[dim]Cancelled.[/dim]')
        return

    try:
        remove_command(sspec_root, name)
    except CommandNotFoundError:
        raise click.ClickException(f"Command '{name}' not found.") from None

    console.print(f'[red]-[/red] Removed command "{name}"')


# ============================================================================
# sspec cmd run
# ============================================================================


@cmd.command(
    'run',
    context_settings={
        'ignore_unknown_options': True,
        'allow_extra_args': True,
    },
)
@click.argument('name', type=COMMAND_NAME_PARAM, required=False, default=None)
@click.pass_context
def run_cmd(ctx: click.Context, name: str | None) -> None:
    """Run a registered command. Extra args are appended to the invoke string."""
    try:
        sspec_root = get_sspec_root()
    except SspecNotFoundError:
        raise click.ClickException("Not a sspec project. Run 'sspec project init' first.") from None

    commands = load_registry(sspec_root)

    if not commands:
        console.print('[dim]No commands registered.[/dim]')
        console.print('Add one with: sspec cmd add')
        return

    if name is None:
        choices = [
            questionary.Choice(
                f'{cmd_name} — {cmd_info.description}',
                value=cmd_name,
            )
            for cmd_name, cmd_info in commands.items()
        ]
        name = questionary.select(
            'Select command to run:',
            choices=choices,
        ).ask()
        if name is None:
            return

    if name not in commands:
        raise click.ClickException(
            f"Command '{name}' not found. Run 'sspec cmd list' to see available commands."
        )

    cmd_info = commands[name]

    extra_args = ctx.args
    if not extra_args:
        extra_args_input = questionary.text(
            f'Extra args for "{name}":',
            default='',
        ).ask()
        if extra_args_input:
            extra_args = extra_args_input.strip().split()

    try:
        exit_code = run_command(cmd_info, sspec_root, extra_args or [])
    except FileNotFoundError as e:
        raise click.ClickException(str(e)) from None

    if exit_code != 0:
        raise SystemExit(exit_code)
