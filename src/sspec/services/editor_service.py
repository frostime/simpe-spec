"""Editor integration helpers (no click/rich/questionary).

These are used by CLI commands to optionally open files after creation.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping
from pathlib import Path

from dotenv import load_dotenv

from sspec.config import get_config


def get_editor_command(
    sspec_root: Path,
    *,
    env: Mapping[str, str] | None = None,
    cwd: Path | None = None,
) -> str | None:
    """Get editor command from config, env vars, or a local .env.

    Resolution order:
    1) `.sspec/config.yaml` -> `editor`
    2) `SSPEC_EDITOR`
    3) `.env` in cwd -> `SSPEC_EDITOR`
    4) `EDITOR`
    """
    config = get_config(sspec_root)
    if config.editor:
        return config.editor

    env_map = env or os.environ

    editor = env_map.get('SSPEC_EDITOR')
    if editor:
        return editor

    env_path = (cwd or Path.cwd()) / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        editor = os.environ.get('SSPEC_EDITOR')
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

    if '{file}' in editor_cmd:
        cmd = editor_cmd.replace('{file}', str(file_path))
    else:
        cmd = f'{editor_cmd} {file_path}'

    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
