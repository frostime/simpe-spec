"""Prompt assembly builtin tool."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

import questionary

from sspec.core import SspecNotFoundError, get_sspec_root
from sspec.services.editor_service import open_in_editor
from sspec.services.prompt_service import (
    PromptError,
    PromptSource,
    PromptSourceType,
    build_chunk_source,
    build_file_source,
    build_glob_source,
    build_shell_source,
    build_tree_source,
    load_preset,
    parse_inline_source_tokens,
    run_prompt_assembly,
    validate_sources,
)

if TYPE_CHECKING:
    import click

__all__ = ['TOOL_NAME', 'TOOL_DESCRIPTION', 'TOOL_PROMPT', 'register_command']

TOOL_NAME = 'prompt'
TOOL_DESCRIPTION = 'Assemble agent-friendly prompt context from local workspace sources'

TOOL_PROMPT = """
# prompt — Inline-first Prompt Assembly Tool

## Purpose

Assemble local workspace context into one agent-friendly prompt bundle.
Supports inline `--add-*` flags, preset import/export, and interactive assembly.

## Usage

```bash
sspec tool prompt \
  --add-file src/sspec/commands/tool.py \
  --add-chunk src/sspec/core.py:190-240 \
  --add-shell "git status --short --branch" \
  --add-tree src/sspec/builtin_tools \
  --to-preset tool_context

sspec tool prompt --from-preset tool_context
sspec tool prompt --from-preset tool_context \
  --add-shell "uv run pytest tests/test_tool_command.py" \
  --allow-shell
sspec tool prompt --dry-run --add-file README.md
sspec tool prompt
```

## Source Flags

- `--add-file PATH`
- `--add-chunk PATH:START-END`
- `--add-shell COMMAND`
- `--add-tree PATH`
- `--add-glob PATTERN`

## Presets

- `--from-preset NAME|PATH` loads reusable sources
- `--to-preset NAME|PATH` exports the merged source list used in this run
- Bare preset names resolve to `.sspec/prompts/<name>.yml`

## Output Contract

Each block uses:
- `BEGIN/END` sentinel header
- YAML frontmatter metadata
- four-backtick fenced content body

Default output writes to `.sspec/tmp/*.prompt.txt` and opens in editor when available.
Use `--dry-run` to print only.

## Shell Safety

- Non-interactive shell sources require `--allow-shell`
- Interactive mode confirms each shell source before execution
""".strip()


def _build_interactive_sources() -> list[PromptSource]:
    sources: list[PromptSource] = []

    while True:
        source_type_raw = questionary.select(
            'Add source type:',
            choices=[
                questionary.Choice('file', value='file'),
                questionary.Choice('file-chunk', value='file-chunk'),
                questionary.Choice('shell', value='shell'),
                questionary.Choice('file-tree', value='file-tree'),
                questionary.Choice('glob', value='glob'),
                questionary.Choice('done', value='done'),
            ],
        ).ask()

        if source_type_raw is None or source_type_raw == 'done':
            break

        source_type = cast(PromptSourceType, source_type_raw)
        if source_type == 'file':
            path = questionary.path('File path:').ask()
            if not path:
                continue
            label = questionary.text('Label (optional):', default=path).ask()
            sources.append(build_file_source(path, label=label or None))
        elif source_type == 'file-chunk':
            path = questionary.path('Chunk file path:').ask()
            if not path:
                continue
            start_text = questionary.text('Start line:').ask()
            end_text = questionary.text('End line:').ask()
            if not start_text or not end_text:
                continue
            start = int(start_text)
            end = int(end_text)
            default_label = f'{path}:L{start}-L{end}'
            label = questionary.text('Label (optional):', default=default_label).ask()
            sources.append(build_chunk_source(path, start, end, label=label or None))
        elif source_type == 'shell':
            command = questionary.text('Shell command:').ask()
            if not command:
                continue
            cwd = questionary.path('Working directory (optional):').ask()
            label = questionary.text('Label (optional):', default=command).ask()
            sources.append(build_shell_source(command, cwd=cwd or None, label=label or None))
        elif source_type == 'file-tree':
            path = questionary.path('Directory path:').ask()
            if not path:
                continue
            label = questionary.text('Label (optional):', default=path).ask()
            depth_text = questionary.text('Depth (optional):').ask()
            source = build_tree_source(path, label=label or None)
            if depth_text:
                source['depth'] = int(depth_text)
            sources.append(source)
        elif source_type == 'glob':
            pattern = questionary.text('Glob pattern:').ask()
            if not pattern:
                continue
            label = questionary.text('Label (optional):', default=pattern).ask()
            sources.append(build_glob_source(pattern, label=label or None))

    return validate_sources(sources)


def _confirm_shell_source(source: PromptSource) -> bool:
    title = source.get('label') or source.get('command') or 'shell source'
    return bool(questionary.confirm(f'Run shell source: {title}?', default=True).ask())


def register_command(group: click.Group) -> None:
    import click

    @group.command(
        name=TOOL_NAME,
        help=TOOL_DESCRIPTION,
        context_settings={'ignore_unknown_options': True, 'allow_extra_args': True},
    )
    @click.option(
        '--from-preset', 'from_preset', help='Load prompt sources from preset name or path.'
    )
    @click.option(
        '--to-preset', 'to_preset', help='Save the merged source list as a preset name or path.'
    )
    @click.option(
        '-o', '--output', type=click.Path(path_type=Path), help='Write prompt output to a file.'
    )
    @click.option('--dry-run', is_flag=True, help='Print prompt text instead of writing a file.')
    @click.option(
        '--allow-shell', is_flag=True, help='Allow shell execution in non-interactive mode.'
    )
    @click.option('--prompt', 'show_prompt', is_flag=True, help='Show tool usage guide.')
    @click.pass_context
    def prompt_command(
        ctx: click.Context,
        from_preset: str | None,
        to_preset: str | None,
        output: Path | None,
        dry_run: bool,
        allow_shell: bool,
        show_prompt: bool,
    ) -> None:
        """Assemble local workspace context into an agent-friendly prompt bundle."""
        if show_prompt:
            click.echo(TOOL_PROMPT)
            return

        try:
            sspec_root = get_sspec_root()
        except SspecNotFoundError:
            message = "Not a sspec project. Run 'sspec project init' first."
            raise click.ClickException(message) from None

        try:
            sources: list[PromptSource] = []
            if from_preset:
                preset = load_preset(sspec_root, from_preset)
                sources.extend(preset.get('sources', []))

            if ctx.args:
                sources.extend(parse_inline_source_tokens(list(ctx.args)))

            is_interactive = not sources
            if is_interactive:
                sources = _build_interactive_sources()
                if not sources:
                    raise click.ClickException('No prompt sources were provided.')
                if to_preset is None:
                    save_choice = questionary.confirm(
                        'Save this source set as a preset?', default=False
                    ).ask()
                    if save_choice:
                        preset_name = questionary.text('Preset name:').ask()
                        if preset_name:
                            to_preset = preset_name

            result = run_prompt_assembly(
                sspec_root=sspec_root,
                sources=sources,
                allow_shell=allow_shell,
                dry_run=dry_run,
                output_path=output,
                to_preset=to_preset,
                interactive_shell_confirm=_confirm_shell_source if is_interactive else None,
            )
        except PromptError as exc:
            raise click.ClickException(str(exc)) from exc
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc

        if result.preset_path is not None:
            click.echo(f'[OK] Saved preset: {result.preset_path}')

        if dry_run:
            click.echo(result.output_text)
            return

        assert result.output_path is not None
        click.echo(f'[OK] Wrote prompt: {result.output_path}')
        click.echo(f'[OK] Blocks: {result.block_count}')
        if open_in_editor(file_path=result.output_path, sspec_root=sspec_root):
            click.echo('[dim]Opened in editor[/dim]')
