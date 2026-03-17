"""Focused tests for the builtin patch tool helpers."""

from __future__ import annotations

from pathlib import Path

from sspec.builtin_tools.apply_patch import apply_patches, parse_patch_header, parse_patches


def test_parse_patch_header_supports_absolute_paths_and_open_ranges(tmp_path: Path) -> None:
    target = (tmp_path / 'demo.py').resolve()

    parsed_path, display_path, line_range = parse_patch_header(
        f'# {target}:L10-',
        project_root=tmp_path,
    )
    assert parsed_path == target
    assert display_path == str(target)
    assert line_range == (10, None)

    relative_path, relative_display, relative_range = parse_patch_header(
        '# src/demo.py:-L20',
        project_root=tmp_path,
    )
    assert relative_path == (tmp_path / 'src' / 'demo.py').resolve()
    assert relative_display == 'src/demo.py'
    assert relative_range == (None, 20)


def test_parse_patches_supports_markdown_bundle_input(tmp_path: Path) -> None:
    target = tmp_path / 'note.txt'
    target.write_text('old\n', encoding='utf-8')

    bundle = """# Failed Patch Bundle

## Failed Patch 1

- File: `note.txt`

```patch
# note.txt
<<<<<<< SEARCH
old
=======
new
>>>>>>> REPLACE
```
"""

    result = parse_patches(bundle, project_root=tmp_path)

    assert result.errors == []
    assert len(result.patches) == 1
    assert result.patches[0].display_path == 'note.txt'


def test_apply_patches_marks_repeated_apply_as_already_applied(tmp_path: Path) -> None:
    target = tmp_path / 'note.txt'
    target.write_text('alpha\n', encoding='utf-8')

    patch_text = """# note.txt
<<<<<<< SEARCH
alpha
=======
beta
>>>>>>> REPLACE
"""

    first = apply_patches(patch_text, project_root=tmp_path)
    assert len(first.results) == 1
    assert first.results[0].status == 'applied'
    assert target.read_text(encoding='utf-8') == 'beta\n'

    second = apply_patches(patch_text, project_root=tmp_path)
    assert len(second.results) == 1
    assert second.results[0].success is True
    assert second.results[0].status == 'already_applied'
    assert second.results[0].match_line == 1


def test_apply_patches_supports_open_ended_line_ranges(tmp_path: Path) -> None:
    target = tmp_path / 'demo.txt'
    target.write_text('one\ntwo\nthree\nfour\n', encoding='utf-8', newline='')

    patch_text = """# demo.txt:L3-
<<<<<<< SEARCH
three
four
=======
THREE
FOUR
>>>>>>> REPLACE
"""

    result = apply_patches(patch_text, project_root=tmp_path)

    assert len(result.results) == 1
    assert result.results[0].status == 'applied'
    assert target.read_text(encoding='utf-8') == 'one\ntwo\nTHREE\nFOUR\n'
