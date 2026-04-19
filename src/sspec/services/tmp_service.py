"""Services for managing `.sspec/tmp` entries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import final


@dataclass(frozen=True, slots=True)
class TmpEntryResult:
    """Result for creating an entry under `.sspec/tmp`."""

    path: Path
    is_dir: bool
    name: str


def create_tmp_entry(
    *,
    sspec_root: Path,
    name: str | None,
    is_dir: bool,
    add_timestamp: bool = True,
) -> TmpEntryResult:
    """Create a file or directory under `.sspec/tmp`.

    If name is omitted, uses a timestamp.
    """

    tmp_root = sspec_root / 'tmp'
    tmp_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%y-%m-%dT%H-%M')

    if name:
        final_name = f'{timestamp}_{name.strip()}' if add_timestamp else name.strip()
    else:
        final_name = timestamp
    if not final_name:
        raise ValueError('Name cannot be empty')

    if is_dir:
        target = tmp_root / final_name
        if target.exists():
            raise FileExistsError(f"tmp dir '{final_name}' already exists")
        target.mkdir(parents=True)
        return TmpEntryResult(path=target, is_dir=True, name=final_name)

    file_name = final_name
    if Path(file_name).suffix == '':
        file_name = f'{file_name}.md'

    target = tmp_root / file_name
    if target.exists():
        raise FileExistsError(f"tmp file '{file_name}' already exists")

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('', encoding='utf-8')
    return TmpEntryResult(path=target, is_dir=False, name=file_name)
