"""Prompt assembly service for builtin `sspec tool prompt`."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, TypedDict

import yaml
from rich.console import Console

from sspec.services.tmp_service import create_tmp_entry

PromptSourceType = Literal['file', 'file-chunk', 'shell', 'file-tree', 'glob']
PromptOutputFormat = Literal['hybrid-headers']
DEFAULT_OUTPUT_FORMAT: PromptOutputFormat = 'hybrid-headers'
DEFAULT_FENCE = '````'
DEFAULT_TMP_NAME = 'prompt.prompt.txt'

SOURCE_KIND_TITLES: dict[PromptSourceType, str] = {
    'file': 'FILE',
    'file-chunk': 'FILE CHUNK',
    'shell': 'SHELL OUTPUT',
    'file-tree': 'FILE TREE',
    'glob': 'FILE',
}


class PromptSource(TypedDict, total=False):
    type: PromptSourceType
    label: str
    path: str
    glob: str
    start: int
    end: int
    command: str
    cwd: str
    depth: int
    no_gitignore: bool
    dirs_only: bool


class PromptPreset(TypedDict, total=False):
    name: str
    description: str
    output_format: Literal['hybrid-headers']
    sources: list[PromptSource]


@dataclass(frozen=True, slots=True)
class ResolvedPromptBlock:
    kind: PromptSourceType
    label: str
    meta: dict[str, Any]
    body: str


@dataclass(frozen=True, slots=True)
class PromptRunResult:
    output_text: str
    output_path: Path | None
    preset_path: Path | None
    block_count: int


class PromptError(RuntimeError):
    """Base prompt tool error."""


class PromptValidationError(PromptError):
    """Raised when a prompt source or preset is invalid."""


class PromptShellPermissionError(PromptError):
    """Raised when shell sources are present without permission."""


class PromptPresetError(PromptError):
    """Raised when preset loading or saving fails."""


class PromptSourceParseError(PromptValidationError):
    """Raised when inline source syntax is invalid."""


def build_file_source(path: str, *, label: str | None = None) -> PromptSource:
    return PromptSource(type='file', path=path, label=label or path)


def build_chunk_source(
    path: str,
    start: int,
    end: int,
    *,
    label: str | None = None,
) -> PromptSource:
    return PromptSource(
        type='file-chunk',
        path=path,
        start=start,
        end=end,
        label=label or f'{path}:L{start}-L{end}',
    )


def build_shell_source(
    command: str,
    *,
    cwd: str | None = None,
    label: str | None = None,
) -> PromptSource:
    source: PromptSource = PromptSource(
        type='shell',
        command=command,
        label=label or command,
    )
    if cwd:
        source['cwd'] = cwd
    return source


def build_tree_source(path: str, *, label: str | None = None) -> PromptSource:
    return PromptSource(type='file-tree', path=path, label=label or path)


def build_glob_source(pattern: str, *, label: str | None = None) -> PromptSource:
    return PromptSource(type='glob', glob=pattern, label=label or pattern)


def parse_chunk_value(raw: str) -> PromptSource:
    if ':' not in raw:
        raise PromptSourceParseError(f"Invalid --add-chunk value: '{raw}'. Use PATH:START-END.")

    path_text, range_text = raw.rsplit(':', 1)
    if '-' not in range_text:
        raise PromptSourceParseError(f"Invalid --add-chunk range: '{raw}'. Use PATH:START-END.")

    start_text, end_text = range_text.split('-', 1)
    try:
        start = int(start_text)
        end = int(end_text)
    except ValueError as exc:
        raise PromptSourceParseError(
            f"Invalid --add-chunk line numbers: '{raw}'. Use PATH:START-END."
        ) from exc

    return build_chunk_source(path_text, start, end)


def parse_inline_source_tokens(tokens: list[str]) -> list[PromptSource]:
    sources: list[PromptSource] = []
    index = 0

    while index < len(tokens):
        token = tokens[index]
        value: str | None = None

        if token.startswith('--add-file='):
            value = token.split('=', 1)[1]
            sources.append(build_file_source(value))
        elif token == '--add-file':
            index += 1
            if index >= len(tokens):
                raise PromptSourceParseError('Missing value for --add-file')
            sources.append(build_file_source(tokens[index]))
        elif token.startswith('--add-chunk='):
            value = token.split('=', 1)[1]
            sources.append(parse_chunk_value(value))
        elif token == '--add-chunk':
            index += 1
            if index >= len(tokens):
                raise PromptSourceParseError('Missing value for --add-chunk')
            sources.append(parse_chunk_value(tokens[index]))
        elif token.startswith('--add-shell='):
            value = token.split('=', 1)[1]
            sources.append(build_shell_source(value))
        elif token == '--add-shell':
            index += 1
            if index >= len(tokens):
                raise PromptSourceParseError('Missing value for --add-shell')
            sources.append(build_shell_source(tokens[index]))
        elif token.startswith('--add-tree='):
            value = token.split('=', 1)[1]
            sources.append(build_tree_source(value))
        elif token == '--add-tree':
            index += 1
            if index >= len(tokens):
                raise PromptSourceParseError('Missing value for --add-tree')
            sources.append(build_tree_source(tokens[index]))
        elif token.startswith('--add-glob='):
            value = token.split('=', 1)[1]
            sources.append(build_glob_source(value))
        elif token == '--add-glob':
            index += 1
            if index >= len(tokens):
                raise PromptSourceParseError('Missing value for --add-glob')
            sources.append(build_glob_source(tokens[index]))
        elif token.startswith('--'):
            raise PromptSourceParseError(f'Unknown inline prompt option: {token}')
        else:
            raise PromptSourceParseError(
                f"Unexpected positional token in prompt source list: '{token}'"
            )
        index += 1

    return sources


def validate_source(source: PromptSource) -> PromptSource:
    source_type = source.get('type')
    if source_type not in {'file', 'file-chunk', 'shell', 'file-tree', 'glob'}:
        raise PromptValidationError(f'Unsupported prompt source type: {source_type!r}')

    normalized = dict(source)

    if source_type == 'file':
        path = str(normalized.get('path', '')).strip()
        if not path:
            raise PromptValidationError('file source requires path')
        normalized['path'] = path
        normalized['label'] = str(normalized.get('label') or path)

    elif source_type == 'file-chunk':
        path = str(normalized.get('path', '')).strip()
        start = normalized.get('start')
        end = normalized.get('end')
        if not path:
            raise PromptValidationError('file-chunk source requires path')
        if not isinstance(start, int) or not isinstance(end, int):
            raise PromptValidationError('file-chunk source requires integer start/end')
        if start < 1 or end < start:
            raise PromptValidationError('file-chunk requires 1 <= start <= end')
        normalized['path'] = path
        normalized['label'] = str(normalized.get('label') or f'{path}:L{start}-L{end}')

    elif source_type == 'shell':
        command = str(normalized.get('command', '')).strip()
        if not command:
            raise PromptValidationError('shell source requires command')
        normalized['command'] = command
        if 'cwd' in normalized and normalized['cwd'] is not None:
            normalized['cwd'] = str(normalized['cwd']).strip()
        normalized['label'] = str(normalized.get('label') or command)

    elif source_type == 'file-tree':
        path = str(normalized.get('path', '')).strip()
        if not path:
            raise PromptValidationError('file-tree source requires path')
        normalized['path'] = path
        normalized['label'] = str(normalized.get('label') or path)
        if 'depth' in normalized and normalized['depth'] is not None:
            depth = normalized['depth']
            if not isinstance(depth, int) or depth < 1:
                raise PromptValidationError('file-tree depth must be a positive integer')

    elif source_type == 'glob':
        pattern = str(normalized.get('glob', '')).strip()
        if not pattern:
            raise PromptValidationError('glob source requires glob pattern')
        normalized['glob'] = pattern
        normalized['label'] = str(normalized.get('label') or pattern)

    return PromptSource(**normalized)


def validate_sources(sources: list[PromptSource]) -> list[PromptSource]:
    return [validate_source(source) for source in sources]


def load_preset(sspec_root: Path, preset_ref: str) -> PromptPreset:
    preset_path = resolve_preset_ref(sspec_root, preset_ref)
    if not preset_path.exists():
        raise PromptPresetError(f'Preset not found: {preset_ref}')

    try:
        data = yaml.safe_load(preset_path.read_text(encoding='utf-8')) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise PromptPresetError(f'Failed to load preset {preset_ref}: {exc}') from exc

    if not isinstance(data, dict):
        raise PromptPresetError(f'Preset must contain a YAML mapping: {preset_ref}')

    raw_sources = data.get('sources', [])
    if not isinstance(raw_sources, list):
        raise PromptPresetError(f'Preset sources must be a list: {preset_ref}')

    sources: list[PromptSource] = []
    for item in raw_sources:
        if not isinstance(item, dict):
            raise PromptPresetError(f'Preset source entries must be mappings: {preset_ref}')
        sources.append(validate_source(PromptSource(**item)))

    return PromptPreset(
        name=str(data.get('name') or preset_path.stem),
        description=str(data.get('description') or ''),
        output_format=DEFAULT_OUTPUT_FORMAT,
        sources=sources,
    )


def save_preset(
    sspec_root: Path,
    preset_ref: str,
    sources: list[PromptSource],
    *,
    description: str | None = None,
) -> Path:
    preset_path = resolve_preset_ref(sspec_root, preset_ref)
    preset_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        'name': preset_path.stem,
        'description': description or '',
        'output_format': DEFAULT_OUTPUT_FORMAT,
        'sources': validate_sources(sources),
    }

    content = yaml.safe_dump(payload, default_flow_style=False, allow_unicode=True, sort_keys=False)
    preset_path.write_text(content, encoding='utf-8')
    return preset_path


def resolve_preset_ref(sspec_root: Path, preset_ref: str) -> Path:
    preset_ref = preset_ref.strip()
    if not preset_ref:
        raise PromptPresetError('Preset name/path cannot be empty')

    ref_path = Path(preset_ref)
    if ref_path.is_absolute():
        return ref_path.resolve(strict=False)

    if ref_path.suffix in {'.yml', '.yaml'} or len(ref_path.parts) > 1:
        return (sspec_root.parent / ref_path).resolve(strict=False)

    return (sspec_root / 'prompts' / f'{preset_ref}.yml').resolve(strict=False)


def render_blocks(blocks: list[ResolvedPromptBlock]) -> str:
    rendered = [_render_block(block) for block in blocks]
    return '\n\n'.join(rendered).rstrip() + '\n'


def write_prompt_output(sspec_root: Path, text: str, *, output_path: Path | None = None) -> Path:
    if output_path is None:
        tmp_entry = create_tmp_entry(
            sspec_root=sspec_root,
            name=DEFAULT_TMP_NAME,
            is_dir=False,
            add_timestamp=True,
        )
        target = tmp_entry.path
    else:
        raw_target = output_path.expanduser()
        target = raw_target if raw_target.is_absolute() else (Path.cwd() / raw_target)
        target = target.resolve(strict=False)
        target.parent.mkdir(parents=True, exist_ok=True)

    target.write_text(text, encoding='utf-8', newline='')
    return target


def run_prompt_assembly(
    *,
    sspec_root: Path,
    sources: list[PromptSource],
    allow_shell: bool,
    dry_run: bool,
    output_path: Path | None = None,
    to_preset: str | None = None,
    interactive_shell_confirm: Callable[[PromptSource], bool] | None = None,
) -> PromptRunResult:
    normalized_sources = validate_sources(sources)
    preset_path = save_preset(sspec_root, to_preset, normalized_sources) if to_preset else None
    blocks = resolve_prompt_blocks(
        sspec_root=sspec_root,
        sources=normalized_sources,
        allow_shell=allow_shell,
        interactive_shell_confirm=interactive_shell_confirm,
    )
    rendered = render_blocks(blocks)
    written_path = None
    if not dry_run:
        written_path = write_prompt_output(
            sspec_root,
            rendered,
            output_path=output_path,
        )
    return PromptRunResult(
        output_text=rendered,
        output_path=written_path,
        preset_path=preset_path,
        block_count=len(blocks),
    )


def resolve_prompt_blocks(
    *,
    sspec_root: Path,
    sources: list[PromptSource],
    allow_shell: bool,
    interactive_shell_confirm: Callable[[PromptSource], bool] | None = None,
) -> list[ResolvedPromptBlock]:
    project_root = sspec_root.parent
    blocks: list[ResolvedPromptBlock] = []

    for source in validate_sources(sources):
        source_type = source['type']

        if source_type == 'file':
            blocks.append(_resolve_file_block(project_root, source))
        elif source_type == 'file-chunk':
            blocks.append(_resolve_chunk_block(project_root, source))
        elif source_type == 'file-tree':
            blocks.append(_resolve_tree_block(project_root, source))
        elif source_type == 'glob':
            blocks.extend(_resolve_glob_blocks(project_root, source))
        elif source_type == 'shell':
            blocks.append(
                _resolve_shell_block(
                    project_root,
                    source,
                    allow_shell=allow_shell,
                    interactive_shell_confirm=interactive_shell_confirm,
                )
            )

    return blocks


def _resolve_file_block(project_root: Path, source: PromptSource) -> ResolvedPromptBlock:
    target = _resolve_project_path(project_root, source['path'])
    if not target.exists() or not target.is_file():
        raise PromptValidationError(f'File source not found: {source["path"]}')
    body = target.read_text(encoding='utf-8')
    return ResolvedPromptBlock(
        kind='file',
        label=source['label'],
        meta={
            'label': source['label'],
            'path': _display_path(target, project_root),
            'kind': 'file',
            'content_format': 'fenced',
            'fence': DEFAULT_FENCE,
        },
        body=body,
    )


def _resolve_chunk_block(project_root: Path, source: PromptSource) -> ResolvedPromptBlock:
    target = _resolve_project_path(project_root, source['path'])
    if not target.exists() or not target.is_file():
        raise PromptValidationError(f'File chunk source not found: {source["path"]}')

    lines = target.read_text(encoding='utf-8').splitlines(keepends=True)
    start = source['start']
    end = source['end']
    if start > len(lines):
        raise PromptValidationError(
            f'Chunk start L{start} exceeds file length ({len(lines)}): {source["path"]}'
        )
    excerpt = ''.join(lines[start - 1 : end])
    return ResolvedPromptBlock(
        kind='file-chunk',
        label=source['label'],
        meta={
            'label': source['label'],
            'path': _display_path(target, project_root),
            'range': f'L{start}-L{end}',
            'kind': 'file-chunk',
            'content_format': 'fenced',
            'fence': DEFAULT_FENCE,
        },
        body=excerpt,
    )


def _resolve_tree_block(project_root: Path, source: PromptSource) -> ResolvedPromptBlock:
    from sspec.builtin_tools.view_tree import build_tree, collect_stats, format_size

    target = _resolve_project_path(project_root, source['path'])
    if not target.exists() or not target.is_dir():
        raise PromptValidationError(f'File tree source not found: {source["path"]}')

    tree = build_tree(
        target,
        max_depth=source.get('depth'),
        dirs_only=bool(source.get('dirs_only', False)),
        show_size=False,
        show_detail=False,
        no_gitignore=bool(source.get('no_gitignore', False)),
        gitignore_root=project_root,
    )
    file_count, dir_count, total_size = collect_stats(
        target,
        bool(source.get('no_gitignore', False)),
        gitignore_root=project_root,
    )

    console = Console(record=True, width=120)
    console.print(tree)
    console.print()
    stats_line = (
        f'Files: {file_count} | Directories: {dir_count} | Total size: {format_size(total_size)}'
    )
    console.print(stats_line)
    body = console.export_text(clear=False)

    meta: dict[str, Any] = {
        'label': source['label'],
        'path': _display_path(target, project_root),
        'kind': 'file-tree',
        'content_format': 'fenced',
        'fence': DEFAULT_FENCE,
    }
    if source.get('depth') is not None:
        meta['depth'] = source['depth']

    return ResolvedPromptBlock(kind='file-tree', label=source['label'], meta=meta, body=body)


def _resolve_glob_blocks(project_root: Path, source: PromptSource) -> list[ResolvedPromptBlock]:
    pattern = source['glob']
    matches = sorted(project_root.glob(pattern))
    file_matches = [match for match in matches if match.is_file()]
    if not file_matches:
        raise PromptValidationError(f'Glob source matched no files: {pattern}')

    blocks: list[ResolvedPromptBlock] = []
    for match in file_matches:
        body = match.read_text(encoding='utf-8')
        blocks.append(
            ResolvedPromptBlock(
                kind='glob',
                label=f'{source["label"]} :: {_display_path(match, project_root)}',
                meta={
                    'label': f'{source["label"]} :: {_display_path(match, project_root)}',
                    'path': _display_path(match, project_root),
                    'glob': pattern,
                    'kind': 'glob',
                    'content_format': 'fenced',
                    'fence': DEFAULT_FENCE,
                },
                body=body,
            )
        )
    return blocks


def _resolve_shell_block(
    project_root: Path,
    source: PromptSource,
    *,
    allow_shell: bool,
    interactive_shell_confirm: Callable[[PromptSource], bool] | None,
) -> ResolvedPromptBlock:
    command = source['command']
    shell_cwd = _resolve_shell_cwd(project_root, source.get('cwd'))
    meta: dict[str, Any] = {
        'label': source['label'],
        'command': command,
        'cwd': str(shell_cwd).replace('\\', '/'),
        'kind': 'shell',
        'content_format': 'fenced',
        'fence': DEFAULT_FENCE,
    }

    if interactive_shell_confirm is not None:
        approved = bool(interactive_shell_confirm(source))
        if not approved:
            meta['status'] = 'skipped-by-user'
            return ResolvedPromptBlock(
                kind='shell',
                label=source['label'],
                meta=meta,
                body='[SHELL BLOCK SKIPPED]\n',
            )
    elif not allow_shell:
        raise PromptShellPermissionError(
            'Shell sources require --allow-shell in non-interactive mode.'
        )

    result = subprocess.run(
        command,
        shell=True,
        cwd=shell_cwd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        check=False,
    )

    meta['exit_code'] = result.returncode
    body_parts: list[str] = []
    if result.stdout:
        body_parts.append(result.stdout)
    if result.stderr:
        if body_parts and not body_parts[-1].endswith('\n'):
            body_parts[-1] += '\n'
        body_parts.append('[[stderr]]\n')
        body_parts.append(result.stderr)
    body = ''.join(body_parts) or '[NO OUTPUT]\n'

    return ResolvedPromptBlock(kind='shell', label=source['label'], meta=meta, body=body)


def _resolve_shell_cwd(project_root: Path, cwd: str | None) -> Path:
    if not cwd:
        return project_root
    raw = Path(cwd)
    return raw if raw.is_absolute() else (project_root / raw).resolve(strict=False)


def _resolve_project_path(project_root: Path, path_text: str) -> Path:
    raw = Path(path_text)
    if raw.is_absolute():
        return raw.resolve(strict=False)
    return (project_root / raw).resolve(strict=False)


def _display_path(path: Path, project_root: Path) -> str:
    try:
        return str(path.relative_to(project_root)).replace('\\', '/')
    except ValueError:
        return str(path).replace('\\', '/')


def _render_block(block: ResolvedPromptBlock) -> str:
    title = SOURCE_KIND_TITLES[block.kind]
    meta_yaml = yaml.safe_dump(
        block.meta,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )
    body = block.body
    if body and not body.endswith('\n'):
        body += '\n'
    return (
        f'========== BEGIN {title} ==========\n'
        f'---\n{meta_yaml}---\n'
        f'{DEFAULT_FENCE}\n'
        f'{body}'
        f'{DEFAULT_FENCE}\n'
        f'========== END {title} =========='
    )
