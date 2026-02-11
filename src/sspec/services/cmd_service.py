"""Command registry service (no click/rich/questionary dependencies).

Manages .sspec/commands/registry.yaml and script files.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

from sspec.commands import project

COMMANDS_DIR = 'commands'
REGISTRY_FILE = 'registry.yaml'

CommandType = Literal['cmd-line', 'script']
ScriptStrategy = Literal['copy', 'move', 'ref']


@dataclass(frozen=True, slots=True)
class CommandInfo:
    """A registered project command."""

    name: str
    description: str
    type: CommandType
    invoke: str
    script_file: str | None = None  # Relative to .sspec/commands/
    script_strategy: ScriptStrategy = 'copy'  # copy/move/ref


class CommandExistsError(RuntimeError):
    pass


class CommandNotFoundError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# Registry I/O
# ---------------------------------------------------------------------------


def _get_commands_dir(sspec_root: Path) -> Path:
    return sspec_root / COMMANDS_DIR


def _get_registry_path(sspec_root: Path) -> Path:
    return _get_commands_dir(sspec_root) / REGISTRY_FILE


def load_registry(sspec_root: Path) -> dict[str, CommandInfo]:
    """Load all commands from registry.yaml."""
    registry_path = _get_registry_path(sspec_root)
    if not registry_path.exists():
        return {}

    try:
        data = yaml.safe_load(registry_path.read_text(encoding='utf-8')) or {}
    except (yaml.YAMLError, OSError):
        return {}

    commands_data: dict[str, Any] = data.get('commands', {})
    if not isinstance(commands_data, dict):
        return {}

    result: dict[str, CommandInfo] = {}
    for name, entry in commands_data.items():
        if not isinstance(entry, dict):
            continue
        result[name] = CommandInfo(
            name=name,
            description=entry.get('description', ''),
            type=entry.get('type', 'cmd-line'),
            invoke=entry.get('invoke', ''),
            script_file=entry.get('script_file'),
            script_strategy=entry.get('script_strategy', 'copy'),
        )
    return result


def save_registry(sspec_root: Path, commands: dict[str, CommandInfo]) -> None:
    """Persist commands to registry.yaml."""
    commands_dir = _get_commands_dir(sspec_root)
    commands_dir.mkdir(parents=True, exist_ok=True)

    data: dict[str, Any] = {}
    for name, cmd in commands.items():
        entry: dict[str, Any] = {
            'description': cmd.description,
            'type': cmd.type,
            'invoke': cmd.invoke,
        }
        if cmd.script_file:
            entry['script_file'] = cmd.script_file
        if cmd.script_strategy != 'copy':
            entry['script_strategy'] = cmd.script_strategy
        data[name] = entry

    registry_path = _get_registry_path(sspec_root)
    content = yaml.dump(
        {'commands': data}, default_flow_style=False, allow_unicode=True, sort_keys=False
    )
    registry_path.write_text(content, encoding='utf-8')


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


def add_command(sspec_root: Path, cmd: CommandInfo) -> None:
    """Add a command to the registry. Raises CommandExistsError on duplicate."""
    commands = load_registry(sspec_root)
    if cmd.name in commands:
        raise CommandExistsError(f"Command '{cmd.name}' already exists")
    commands[cmd.name] = cmd
    save_registry(sspec_root, commands)


def remove_command(sspec_root: Path, name: str) -> CommandInfo:
    """Remove a command. Returns removed info. Raises CommandNotFoundError."""
    commands = load_registry(sspec_root)
    if name not in commands:
        raise CommandNotFoundError(f"Command '{name}' not found")

    removed = commands.pop(name)

    if removed.script_file and removed.script_strategy in ('copy', 'move'):
        script_path = _get_commands_dir(sspec_root) / removed.script_file
        if script_path.exists():
            script_path.unlink()

    save_registry(sspec_root, commands)
    return removed


def handle_script_file(
    sspec_root: Path, source: Path, strategy: ScriptStrategy
) -> str | None:
    """Handle script file according to strategy.

    - copy: Copy the script file to .sspec/commands/. Returns the filename.
    - move: Move the script file to .sspec/commands/. Returns the filename.
    - ref: Only reference the script location. Returns the absolute path.
    """
    commands_dir = _get_commands_dir(sspec_root)
    commands_dir.mkdir(parents=True, exist_ok=True)

    if strategy == 'ref':
        source = source.resolve().absolute()
        project_root = sspec_root.parent.resolve().absolute()
        # source is outside project → return absolute path
        is_under_project = source.is_relative_to(project_root)
        if is_under_project:
            return str(source.relative_to(sspec_root.parent))
        else:
            return str(source)

    dest = commands_dir / source.name

    if strategy == 'copy':
        if dest.exists():
            stem = source.stem
            suffix = source.suffix
            counter = 1
            while dest.exists():
                dest = commands_dir / f'{stem}_{counter}{suffix}'
                counter += 1
        shutil.copy2(source, dest)
    elif strategy == 'move':
        if dest.exists():
            stem = source.stem
            suffix = source.suffix
            counter = 1
            while dest.exists():
                dest = commands_dir / f'{stem}_{counter}{suffix}'
                counter += 1
        shutil.move(str(source), str(dest))

    return dest.name


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------


# check if have pwsh
def has_powershell() -> bool:
    try:
        subprocess.run(
            ['pwsh', '-Command', 'exit'],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    except Exception:
        return False


has_pwsh = has_powershell()


# Extension → default invoke pattern
INVOKE_PATTERNS: dict[str, str] = {
    '.py': 'python {script}',
    '.ps1': 'powershell -File {script}' if not has_pwsh else 'pwsh -File {script}',
    '.sh': 'bash {script}',
    '.bash': 'bash {script}',
    '.bat': '{script}',
    '.cmd': '{script}',
}


def suggest_invoke_pattern(script_path: Path) -> str | None:
    """Suggest an invoke pattern based on file extension."""
    return INVOKE_PATTERNS.get(script_path.suffix.lower())


def resolve_invoke(cmd: CommandInfo, sspec_root: Path, extra_args: list[str]) -> str:
    """Build the final shell command string."""
    invoke = cmd.invoke

    if cmd.script_file and '{script}' in invoke:
        if cmd.script_strategy == 'ref':
            script_abs = str(cmd.script_file)
        else:
            script_abs = str((_get_commands_dir(sspec_root) / cmd.script_file).resolve())
        invoke = invoke.replace('{script}', script_abs)

    if extra_args:
        invoke = invoke + ' ' + ' '.join(extra_args)

    return invoke


def resolve_script_path(cmd: CommandInfo, sspec_root: Path) -> Path | None:
    """Get the absolute path to the script file."""
    if not cmd.script_file:
        return None
    if cmd.script_strategy == 'ref':
        return Path(cmd.script_file)
    return _get_commands_dir(sspec_root) / cmd.script_file


def run_command(cmd: CommandInfo, sspec_root: Path, extra_args: list[str]) -> int:
    """Execute a command from project root. Returns exit code."""
    project_root = sspec_root.parent
    invoke_str = resolve_invoke(cmd, sspec_root, extra_args)

    script_path = resolve_script_path(cmd, sspec_root)
    if script_path and not script_path.exists():
        raise FileNotFoundError(
            f'Script file not found: {cmd.script_file}\n' f'Expected at: {script_path}'
        )

    result = subprocess.run(invoke_str, shell=True, cwd=project_root)
    return result.returncode
