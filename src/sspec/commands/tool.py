"""sspec tool command - builtin development tools."""

import click

from sspec.builtin_tools import apply_patch


@click.group()
def tool() -> None:
    """Builtin development tools."""
    pass


# Register tools (manual for now, clear and explicit)
apply_patch.register_command(tool)
