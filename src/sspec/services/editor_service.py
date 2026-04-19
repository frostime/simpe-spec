"""Editor integration helpers (no click/rich/questionary).

These are used by CLI commands to optionally open files after creation.
"""

from __future__ import annotations

import os
import shlex
import subprocess
from collections.abc import Mapping
from pathlib import Path

from dotenv import dotenv_values


def _quote_for_shell(path: Path) -> str:
    """Quote a path for the current platform shell."""
    path_str = str(path)
    if os.name == 'nt':
        return subprocess.list2cmdline([path_str])
    return shlex.quote(path_str)


def get_editor_command(
    sspec_root: Path,
    *,
    env: Mapping[str, str] | None = None,
    cwd: Path | None = None,
) -> str | None:
    """Get editor command from local .env and process env vars.

    Resolution order:
    1) `.env` in cwd -> `SSPEC_EDITOR`
    2) Runtime env `SSPEC_EDITOR`
    3) Runtime env `EDITOR`
    """
    env_map = os.environ if env is None else env

    env_path = (cwd or Path.cwd()) / '.env'
    if env_path.exists():
        file_env = dotenv_values(env_path)
        editor = file_env.get('SSPEC_EDITOR')
        if editor:
            return editor

    editor = env_map.get('SSPEC_EDITOR')
    if editor:
        return editor

    return env_map.get('EDITOR')


def open_in_editor(
    *,
    file_path: Path,
    sspec_root: Path,
    env: Mapping[str, str] | None = None,
) -> bool:
    """Open a file in an editor.

    Returns True if an editor command was found and executed.
    """
    editor_cmd = get_editor_command(sspec_root, env=env)
    if not editor_cmd:
        return False

    quoted_file = _quote_for_shell(file_path)

    if '{file}' in editor_cmd:
        # Replace pre-quoted placeholders first to avoid accidental double quoting.
        cmd = editor_cmd.replace('"{file}"', quoted_file)
        cmd = cmd.replace("'{file}'", quoted_file)
        cmd = cmd.replace('{file}', quoted_file)
    else:
        cmd = f'{editor_cmd} {quoted_file}'

    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
