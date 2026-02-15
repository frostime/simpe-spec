"""Editor integration helpers (no click/rich/questionary).

These are used by CLI commands to optionally open files after creation.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping
from pathlib import Path

from dotenv import dotenv_values

from sspec.config import get_config, get_global_config


def get_editor_command(
    sspec_root: Path,
    *,
    env: Mapping[str, str] | None = None,
    cwd: Path | None = None,
) -> str | None:
    """Get editor command from config, env vars, or a local .env.

    Resolution order:
    1) Runtime env `SSPEC_EDITOR`
    2) `.env` in cwd -> `SSPEC_EDITOR`
    3) Global config `~/.config/sspec/sspec.config.yaml` -> `SSPEC_EDITOR`
    4) `.sspec/config.yaml` -> `editor` (legacy compatibility)
    5) Runtime env `EDITOR`
    """
    env_map = env or os.environ

    editor = env_map.get('SSPEC_EDITOR')
    if editor:
        return editor

    env_path = (cwd or Path.cwd()) / '.env'
    if env_path.exists():
        file_env = dotenv_values(env_path)
        editor = file_env.get('SSPEC_EDITOR')
        if editor:
            return editor

    global_config = get_global_config()
    if global_config.sspec_editor:
        return global_config.sspec_editor

    config = get_config(sspec_root)
    if config.editor:
        return config.editor

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

    if '{file}' in editor_cmd:
        cmd = editor_cmd.replace('{file}', str(file_path))
    else:
        cmd = f'{editor_cmd} {file_path}'

    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
