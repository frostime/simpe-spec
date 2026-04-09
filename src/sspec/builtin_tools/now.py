"""Current time helper for agents writing timestamped docs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import click

__all__ = [
    'TOOL_NAME',
    'TOOL_DESCRIPTION',
    'TOOL_PROMPT',
    'register_command',
]

TOOL_NAME = 'now'
TOOL_DESCRIPTION = 'Show current local or UTC time for timestamped documents'

TOOL_PROMPT = """
# now — Current Time Helper

## Purpose

Provide a reliable current timestamp when an agent needs to write time-sensitive
content such as memory updates, milestones, frontmatter, or spec-doc
metadata.

## Usage

```
sspec tool now
sspec tool now --date
sspec tool now --seconds
sspec tool now --utc
sspec tool now --json
```

## Output

- Default: local ISO timestamp with timezone offset, minute precision
- `--seconds`: include seconds
- `--date`: output only `YYYY-MM-DD`
- `--utc`: use UTC instead of local timezone
- `--json`: output structured local + UTC timestamps for agent consumption
""".strip()


def _format_iso(now: datetime, *, include_seconds: bool) -> str:
    """Format timestamp as ISO-8601 with timezone offset."""
    timespec = 'seconds' if include_seconds else 'minutes'
    return now.isoformat(timespec=timespec)


def _format_timezone_label(now: datetime) -> str:
    """Return a stable UTC offset label for agent consumption."""
    return now.strftime('UTC%z')[:-2] + ':' + now.strftime('UTC%z')[-2:]


def build_now_payload(*, use_utc: bool, include_seconds: bool) -> dict[str, str]:
    """Build structured time output for CLI and tests."""
    local_now = datetime.now().astimezone()
    utc_now = local_now.astimezone(timezone.utc)
    active_now = utc_now if use_utc else local_now

    return {
        'timestamp': _format_iso(active_now, include_seconds=include_seconds),
        'date': active_now.date().isoformat(),
        'timezone': _format_timezone_label(active_now),
        'local': _format_iso(local_now, include_seconds=include_seconds),
        'utc': _format_iso(utc_now, include_seconds=include_seconds),
    }


def register_command(group: click.Group) -> None:
    """Register now as a Click subcommand."""
    import click

    @group.command(name=TOOL_NAME, help=TOOL_DESCRIPTION)
    @click.option('--date', 'date_only', is_flag=True, help='Show only YYYY-MM-DD.')
    @click.option('--seconds', is_flag=True, help='Include seconds in ISO output.')
    @click.option('--utc', 'use_utc', is_flag=True, help='Use UTC instead of local timezone.')
    @click.option('--json', 'json_output', is_flag=True, help='Show structured JSON output.')
    @click.option(
        '--prompt', 'show_prompt', is_flag=True, help='Show LLM-oriented tool description.'
    )
    def now_command(
        date_only: bool,
        seconds: bool,
        use_utc: bool,
        json_output: bool,
        show_prompt: bool,
    ) -> None:
        """Show the current time for timestamped content."""
        if show_prompt:
            click.echo(TOOL_PROMPT)
            return

        payload = build_now_payload(use_utc=use_utc, include_seconds=seconds)

        if json_output:
            click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
            return

        if date_only:
            click.echo(payload['date'])
            return

        click.echo(payload['timestamp'])
