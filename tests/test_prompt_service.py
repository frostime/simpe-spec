from __future__ import annotations

from pathlib import Path

import pytest

from sspec.services.prompt_service import (
    PromptShellPermissionError,
    PromptValidationError,
    ResolvedPromptBlock,
    build_file_source,
    build_glob_source,
    build_shell_source,
    parse_chunk_value,
    parse_inline_source_tokens,
    render_blocks,
    resolve_prompt_blocks,
    run_prompt_assembly,
    save_preset,
    validate_sources,
)


def _make_sspec_project(tmp_path: Path) -> Path:
    sspec_root = tmp_path / '.sspec'
    sspec_root.mkdir()
    (sspec_root / 'project.md').write_text('# Project\n', encoding='utf-8')
    return sspec_root


def test_parse_inline_source_tokens_preserves_cli_order() -> None:
    sources = parse_inline_source_tokens(
        [
            '--add-file',
            'a.py',
            '--add-shell',
            'git status',
            '--add-chunk',
            'b.py:1-3',
        ]
    )

    assert [source['type'] for source in sources] == ['file', 'shell', 'file-chunk']
    assert sources[2]['path'] == 'b.py'
    assert sources[2]['start'] == 1
    assert sources[2]['end'] == 3


@pytest.mark.parametrize(
    ('raw', 'path', 'start', 'end'),
    [
        ('src/mod.py:1-10', 'src/mod.py', 1, 10),
        ('C:/work/demo.py:10-20', 'C:/work/demo.py', 10, 20),
    ],
)
def test_parse_chunk_value_supports_path_and_range(
    raw: str,
    path: str,
    start: int,
    end: int,
) -> None:
    source = parse_chunk_value(raw)

    assert source['type'] == 'file-chunk'
    assert source['path'] == path
    assert source['start'] == start
    assert source['end'] == end


def test_validate_sources_rejects_invalid_range() -> None:
    with pytest.raises(PromptValidationError):
        validate_sources([{'type': 'file-chunk', 'path': 'a.py', 'start': 5, 'end': 3}])


def test_render_blocks_uses_frontmatter_and_fenced_content() -> None:
    text = render_blocks(
        [
            ResolvedPromptBlock(
                kind='file-chunk',
                label='demo',
                meta={
                    'label': 'demo',
                    'path': 'src/demo.py',
                    'range': 'L1-L2',
                    'kind': 'file-chunk',
                    'content_format': 'fenced',
                    'fence': '````',
                },
                body='print(1)\n',
            )
        ]
    )

    assert '========== BEGIN FILE CHUNK ==========' in text
    assert '---\nlabel: demo\n' in text
    assert 'content_format: fenced' in text
    assert '````\nprint(1)\n````' in text
    assert '========== END FILE CHUNK ==========' in text


def test_resolve_prompt_blocks_supports_file_chunk_glob_and_tree(tmp_path: Path) -> None:
    sspec_root = _make_sspec_project(tmp_path)
    project_root = sspec_root.parent
    src = project_root / 'src'
    src.mkdir()
    (src / 'a.py').write_text('one\ntwo\nthree\n', encoding='utf-8')
    (src / 'b.py').write_text('print(2)\n', encoding='utf-8')
    subdir = project_root / 'pkg'
    subdir.mkdir()
    (subdir / 'mod.py').write_text('x = 1\n', encoding='utf-8')

    sources = validate_sources(
        [
            parse_chunk_value('src/a.py:2-3'),
            build_glob_source('src/*.py'),
            {'type': 'file-tree', 'path': 'pkg', 'label': 'pkg tree', 'depth': 2},
        ]
    )

    blocks = resolve_prompt_blocks(sspec_root=sspec_root, sources=sources, allow_shell=False)

    assert blocks[0].meta['range'] == 'L2-L3'
    assert blocks[0].body == 'two\nthree\n'
    assert any(block.meta.get('glob') == 'src/*.py' for block in blocks)
    assert any(block.kind == 'file-tree' and 'Files:' in block.body for block in blocks)


def test_resolve_prompt_blocks_requires_allow_shell_in_noninteractive_mode(tmp_path: Path) -> None:
    sspec_root = _make_sspec_project(tmp_path)

    with pytest.raises(PromptShellPermissionError):
        resolve_prompt_blocks(
            sspec_root=sspec_root,
            sources=validate_sources([build_shell_source('echo hi')]),
            allow_shell=False,
        )


def test_resolve_prompt_blocks_supports_interactive_shell_skip(tmp_path: Path) -> None:
    sspec_root = _make_sspec_project(tmp_path)
    blocks = resolve_prompt_blocks(
        sspec_root=sspec_root,
        sources=validate_sources([build_shell_source('echo hi')]),
        allow_shell=False,
        interactive_shell_confirm=lambda source: False,
    )

    assert len(blocks) == 1
    assert blocks[0].meta['status'] == 'skipped-by-user'
    assert '[SHELL BLOCK SKIPPED]' in blocks[0].body


def test_run_prompt_assembly_writes_tmp_output_and_preset(tmp_path: Path) -> None:
    sspec_root = _make_sspec_project(tmp_path)
    project_root = sspec_root.parent
    target = project_root / 'demo.py'
    target.write_text('print(1)\n', encoding='utf-8')

    result = run_prompt_assembly(
        sspec_root=sspec_root,
        sources=validate_sources([build_file_source('demo.py')]),
        allow_shell=False,
        dry_run=False,
        to_preset='demo_context',
    )

    assert result.output_path is not None
    assert result.output_path.exists()
    assert result.output_path.suffix == '.txt'
    assert '========== BEGIN FILE ==========' in result.output_text
    assert result.preset_path is not None
    assert result.preset_path.exists()
    preset_text = result.preset_path.read_text(encoding='utf-8')
    assert 'name: demo_context' in preset_text
    assert 'path: demo.py' in preset_text


def test_save_preset_writes_yaml_under_default_prompt_dir(tmp_path: Path) -> None:
    sspec_root = _make_sspec_project(tmp_path)
    preset_path = save_preset(
        sspec_root,
        'review',
        validate_sources([build_file_source('demo.py')]),
    )

    assert preset_path == (sspec_root / 'prompts' / 'review.yml').resolve(strict=False)
    assert preset_path.exists()
    content = preset_path.read_text(encoding='utf-8')
    assert 'output_format: hybrid-headers' in content
