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


def test_parse_patch_header_supports_paths_with_spaces(tmp_path: Path) -> None:
    parsed_path, display_path, line_range = parse_patch_header(
        '# docs/my file.py:L3-L5',
        project_root=tmp_path,
    )

    assert parsed_path == (tmp_path / 'docs' / 'my file.py').resolve()
    assert display_path == 'docs/my file.py'
    assert line_range == (3, 5)


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


def test_parse_patches_errors_when_no_valid_patch_block_exists(tmp_path: Path) -> None:
    target = tmp_path / 'note.txt'
    target.write_text('old\n', encoding='utf-8')

    patch_text = """# explanatory heading

This is not a patch block.
"""

    result = parse_patches(patch_text, project_root=tmp_path)

    expected_error = (
        "No valid patch blocks found. Ensure each block starts with '# <path>' "
        'followed by a SEARCH/REPLACE block.'
    )

    assert result.patches == []
    assert result.errors == [expected_error]


def test_parse_patches_ignores_hash_lines_without_following_search_marker(tmp_path: Path) -> None:
    target = tmp_path / 'note.txt'
    target.write_text('old\n', encoding='utf-8')

    patch_text = """# note.txt
this line prevents the header from being treated as a patch block
<<<<<<< SEARCH
old
=======
new
>>>>>>> REPLACE
"""

    result = parse_patches(patch_text, project_root=tmp_path)

    expected_error = (
        "No valid patch blocks found. Ensure each block starts with '# <path>' "
        'followed by a SEARCH/REPLACE block.'
    )

    assert result.patches == []
    assert result.errors == [expected_error]


def test_apply_patches_allows_empty_search_for_empty_file(tmp_path: Path) -> None:
    target = tmp_path / 'empty.txt'
    target.write_text('', encoding='utf-8')

    patch_text = """# empty.txt
<<<<<<< SEARCH
=======
hello
>>>>>>> REPLACE
"""

    result = apply_patches(patch_text, project_root=tmp_path)

    assert len(result.results) == 1
    assert result.results[0].status == 'applied'
    assert target.read_text(encoding='utf-8') == 'hello\n'


def test_apply_patches_empty_search_noop_for_empty_file(tmp_path: Path) -> None:
    target = tmp_path / 'empty.txt'
    target.write_text('', encoding='utf-8')

    patch_text = """# empty.txt
<<<<<<< SEARCH
=======
>>>>>>> REPLACE
"""

    result = apply_patches(patch_text, project_root=tmp_path)

    assert len(result.results) == 1
    assert result.results[0].status == 'no_change_patch'
    assert target.read_text(encoding='utf-8') == ''


def test_apply_patches_rejects_empty_search_for_non_empty_file(tmp_path: Path) -> None:
    target = tmp_path / 'note.txt'
    target.write_text('old\n', encoding='utf-8')

    patch_text = """# note.txt
<<<<<<< SEARCH
=======
new
>>>>>>> REPLACE
"""

    result = apply_patches(patch_text, project_root=tmp_path)

    assert len(result.results) == 1
    assert result.results[0].status == 'parse_error'
    assert 'non-empty' in (result.results[0].error or '')
    assert target.read_text(encoding='utf-8') == 'old\n'


def test_apply_patches_dry_run_reports_success_without_writing(tmp_path: Path) -> None:
    target = tmp_path / 'note.txt'
    target.write_text('alpha\n', encoding='utf-8')

    patch_text = """# note.txt
<<<<<<< SEARCH
alpha
=======
beta
>>>>>>> REPLACE
"""

    result = apply_patches(patch_text, project_root=tmp_path, dry_run=True)

    assert len(result.results) == 1
    assert result.results[0].status == 'applied'
    assert result.results[0].match_line == 1
    assert target.read_text(encoding='utf-8') == 'alpha\n'


def test_apply_patches_supports_ascii_target_file(tmp_path: Path) -> None:
    target = tmp_path / 'ascii.txt'
    target.write_bytes(b'alpha\n')

    patch_text = """# ascii.txt
<<<<<<< SEARCH
alpha
=======
beta
>>>>>>> REPLACE
"""

    result = apply_patches(patch_text, project_root=tmp_path)

    assert len(result.results) == 1
    assert result.results[0].status == 'applied'
    assert target.read_bytes() == b'beta\n'


def test_apply_patches_supports_utf8_target_file(tmp_path: Path) -> None:
    target = tmp_path / 'utf8.txt'
    target.write_text('café\n', encoding='utf-8', newline='')

    patch_text = """# utf8.txt
<<<<<<< SEARCH
café
=======
CAFÉ
>>>>>>> REPLACE
"""

    result = apply_patches(patch_text, project_root=tmp_path)

    assert len(result.results) == 1
    assert result.results[0].status == 'applied'
    assert target.read_text(encoding='utf-8') == 'CAFÉ\n'


def test_apply_patches_supports_utf8_bom_target_file(tmp_path: Path) -> None:
    target = tmp_path / 'utf8bom.txt'
    target.write_text('alpha\n', encoding='utf-8-sig', newline='')

    patch_text = """# utf8bom.txt
<<<<<<< SEARCH
alpha
=======
beta
>>>>>>> REPLACE
"""

    result = apply_patches(patch_text, project_root=tmp_path)

    assert len(result.results) == 1
    assert result.results[0].status == 'applied'
    raw = target.read_bytes()
    assert raw.startswith(b'\xef\xbb\xbf')
    assert raw.decode('utf-8-sig') == 'beta\n'


def test_apply_patches_supports_gbk_target_file(tmp_path: Path) -> None:
    target = tmp_path / 'gbk.txt'
    target.write_text('你好\n', encoding='gbk', newline='')

    patch_text = """# gbk.txt
<<<<<<< SEARCH
你好
=======
您好
>>>>>>> REPLACE
"""

    result = apply_patches(patch_text, project_root=tmp_path)

    assert len(result.results) == 1
    assert result.results[0].status == 'applied'
    raw = target.read_bytes()
    assert raw.decode('gbk') == '您好\n'
