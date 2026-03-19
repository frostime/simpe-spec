"""sspec tool command - builtin development tools."""

import click

from sspec.builtin_tools import (
    apply_patch,
    ask,
    fileinfo,
    mdtoc,
    now,
    pack_zip,
    treesitter,
    view_tree,
    write,
)


@click.group()
def tool() -> None:
    """Builtin development tools."""
    pass


# Register tools (manual for now, clear and explicit)
apply_patch.register_command(tool)
pack_zip.register_command(tool)
view_tree.register_command(tool)
fileinfo.register_command(tool)
write.register_command(tool)
mdtoc.register_command(tool)
now.register_command(tool)
ask.register_command(tool)
treesitter.register_command(tool)
