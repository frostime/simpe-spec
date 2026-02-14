"""Unified CLI echo utilities for consistent output."""

from __future__ import annotations

from enum import Enum
from typing import Any

import click


class Style(str, Enum):
    """Preset styles - zero-config usage."""

    INFO = 'info'
    SUCCESS = 'success'
    WARNING = 'warning'
    ERROR = 'error'
    DEBUG = 'debug'
    TITLE = 'title'
    MUTED = 'muted'
    BOLD = 'bold'


class Color:
    """Available colors - use with fg/bg parameters."""

    BLACK = 'black'
    RED = 'red'
    GREEN = 'green'
    YELLOW = 'yellow'
    BLUE = 'blue'
    MAGENTA = 'magenta'
    CYAN = 'cyan'
    WHITE = 'white'


_STYLE_PRESETS: dict[Style, dict[str, Any]] = {
    Style.INFO: {'fg': 'cyan', 'bold': True},
    Style.SUCCESS: {'fg': 'green', 'bold': True},
    Style.WARNING: {'fg': 'yellow'},
    Style.ERROR: {'fg': 'red', 'bold': True},
    Style.DEBUG: {'fg': 'black', 'dim': True},
    Style.TITLE: {'fg': 'cyan', 'bold': True},
    Style.MUTED: {'fg': 'black', 'dim': True},
    Style.BOLD: {'bold': True},
}


def echo(
    *messages: Any,
    style: Style | str | None = None,
    fg: str | None = None,
    bg: str | None = None,
    bold: bool = False,
    italic: bool = False,
    dim: bool = False,
    underline: bool = False,
    err: bool = False,
    verbose: bool = False,
    verbose_only: bool = False,
) -> None:
    """Unified CLI echo with flexible styling.

    Args:
        *messages: Text messages to print (joined with newlines)
        style: Preset style (Style.INFO, Style.SUCCESS, etc.) - zero-config
        fg: Foreground color (red, green, yellow, blue, magenta, cyan, white, black)
        bg: Background color (same colors as fg)
        bold: Bold text
        italic: Italic text
        dim: Dimmed text
        underline: Underlined text
        err: Print to stderr
        verbose: If True, enables verbose mode
        verbose_only: Only print if verbose=True

    Examples:
        echo("Hello")                                    # plain text
        echo("Done!", style=Style.SUCCESS)               # preset style
        echo("Done!", style="success")                   # or string
        echo("Warning", fg="yellow")                     # custom color
        echo("Important", fg="red", bold=True)           # color + bold
        echo("Debug info", style=Style.DEBUG, verbose=True)
    """
    if verbose_only and not verbose:
        return

    msg = '\n'.join(str(m) for m in messages)
    if not msg:
        return

    # Build style kwargs
    kwargs: dict[str, Any] = {}

    # Apply preset first, then override with explicit params
    if style:
        preset = _get_preset(style)
        if preset:
            kwargs.update(preset)

    # Override with explicit parameters
    if fg:
        kwargs['fg'] = fg
    if bg:
        kwargs['bg'] = bg
    if bold:
        kwargs['bold'] = True
    if italic:
        kwargs['italic'] = True
    if dim:
        kwargs['dim'] = True
    if underline:
        kwargs['underline'] = True

    if kwargs:
        msg = click.style(msg, **kwargs)

    click.echo(msg, err=err)


def _get_preset(style: Style | str) -> dict[str, Any] | None:
    """Get preset style dict."""
    try:
        if isinstance(style, str):
            style = Style(style)
        return _STYLE_PRESETS.get(style)
    except ValueError:
        return None


def info(*msgs: Any, **kwargs: Any) -> None:
    """Print info message (cyan, bold)."""
    echo(*msgs, style=Style.INFO, **kwargs)


def success(*msgs: Any, **kwargs: Any) -> None:
    """Print success message (green, bold)."""
    echo(*msgs, style=Style.SUCCESS, **kwargs)


def warn(*msgs: Any, **kwargs: Any) -> None:
    """Print warning message (yellow)."""
    echo(*msgs, style=Style.WARNING, **kwargs)


def error(*msgs: Any, **kwargs: Any) -> None:
    """Print error message (red, bold)."""
    echo(*msgs, style=Style.ERROR, **kwargs)


def debug(*msgs: Any, verbose: bool = True, **kwargs: Any) -> None:
    """Print debug message (dimmed). Only prints if verbose=True."""
    echo(*msgs, style=Style.DEBUG, verbose=verbose, verbose_only=True, **kwargs)


def title(*msgs: Any, **kwargs: Any) -> None:
    """Print title message (cyan, bold)."""
    echo(*msgs, style=Style.TITLE, **kwargs)


def muted(*msgs: Any, **kwargs: Any) -> None:
    """Print muted message (dimmed)."""
    echo(*msgs, style=Style.MUTED, **kwargs)


echo_instance = echo
