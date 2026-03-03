"""Tests for sspec.libs.md_yaml — YAML frontmatter parse/update utilities."""

from __future__ import annotations

from sspec.libs.md_yaml import parse_frontmatter, update_frontmatter

# ---------------------------------------------------------------------------
# parse_frontmatter
# ---------------------------------------------------------------------------


class TestParseFrontmatter:
    def test_standard_frontmatter(self):
        content = '---\nstatus: OPEN\nname: demo\n---\nBody text'
        meta, body = parse_frontmatter(content)
        assert meta == {'status': 'OPEN', 'name': 'demo'}
        assert body == 'Body text'

    def test_no_frontmatter_returns_original(self):
        content = 'Just plain markdown'
        meta, body = parse_frontmatter(content)
        assert meta == {}
        assert body == content

    def test_empty_frontmatter(self):
        meta, body = parse_frontmatter('---\n---\nBody')
        assert meta == {}
        assert body == 'Body'

    def test_incomplete_frontmatter_one_separator(self):
        """Only opening --- without closing --- is not valid frontmatter."""
        content = '---\nkey: value'
        meta, body = parse_frontmatter(content)
        assert meta == {}
        assert body == content

    def test_invalid_yaml_returns_empty_meta(self):
        content = '---\n: invalid: yaml: :\n---\nBody'
        meta, body = parse_frontmatter(content)
        assert meta == {}
        assert body == 'Body'

    def test_non_dict_yaml_treated_as_empty(self):
        """If YAML parses to a non-dict (e.g. list), treat as empty meta."""
        content = '---\n- item1\n- item2\n---\nBody'
        meta, body = parse_frontmatter(content)
        assert meta == {}

    def test_complex_yaml_structures(self):
        content = (
            '---\n'
            'reference:\n'
            '  - source: path/to/file\n'
            '    type: request\n'
            'status: DOING\n'
            '---\n'
            'Content'
        )
        meta, body = parse_frontmatter(content)
        assert isinstance(meta['reference'], list)
        assert meta['reference'][0]['source'] == 'path/to/file'
        assert meta['status'] == 'DOING'
        assert body == 'Content'

    def test_leading_newlines_stripped_from_body(self):
        meta, body = parse_frontmatter('---\nk: v\n---\n\n\nBody')
        assert body == 'Body'

    def test_unicode_in_frontmatter(self):
        content = '---\nname: 测试\n---\n内容'
        meta, body = parse_frontmatter(content)
        assert meta['name'] == '测试'
        assert body == '内容'

    def test_multiline_body_preserved(self):
        content = '---\nk: v\n---\nLine 1\nLine 2\nLine 3'
        _, body = parse_frontmatter(content)
        assert body == 'Line 1\nLine 2\nLine 3'

    def test_body_containing_triple_dashes(self):
        """Triple dashes in body should not confuse the parser (only first two matter)."""
        content = '---\nk: v\n---\nSome text\n---\nNot frontmatter'
        meta, body = parse_frontmatter(content)
        assert meta == {'k': 'v'}
        # Body is everything after the second ---
        assert 'Some text' in body


# ---------------------------------------------------------------------------
# update_frontmatter
# ---------------------------------------------------------------------------


class TestUpdateFrontmatter:
    def test_update_existing_field(self):
        content = '---\nstatus: OPEN\n---\nBody'
        updated = update_frontmatter(content, {'status': 'DONE'})
        meta, body = parse_frontmatter(updated)
        assert meta['status'] == 'DONE'
        assert body == 'Body'

    def test_add_new_field(self):
        content = '---\nstatus: OPEN\n---\nBody'
        updated = update_frontmatter(content, {'archived': '2026-02-05'})
        meta, _ = parse_frontmatter(updated)
        assert meta['status'] == 'OPEN'
        assert meta['archived'] == '2026-02-05'

    def test_create_frontmatter_when_none_exists(self):
        updated = update_frontmatter('Plain body', {'status': 'NEW'})
        meta, body = parse_frontmatter(updated)
        assert meta['status'] == 'NEW'
        assert body == 'Plain body'

    def test_update_multiple_fields(self):
        content = '---\nstatus: OPEN\ntype: feature\n---\nBody'
        updated = update_frontmatter(content, {'status': 'DONE', 'type': 'bugfix', 'note': 'x'})
        meta, _ = parse_frontmatter(updated)
        assert meta['status'] == 'DONE'
        assert meta['type'] == 'bugfix'
        assert meta['note'] == 'x'

    def test_complex_value(self):
        content = '---\nstatus: OPEN\n---\nBody'
        updated = update_frontmatter(
            content,
            {'reference': [{'source': 'requests/test.md', 'type': 'request'}]},
        )
        meta, _ = parse_frontmatter(updated)
        assert isinstance(meta['reference'], list)
        assert meta['reference'][0]['source'] == 'requests/test.md'

    def test_body_preserved_after_update(self):
        content = '---\nk: v\n---\nImportant\nMulti-line\nContent'
        updated = update_frontmatter(content, {'new': 'val'})
        _, body = parse_frontmatter(updated)
        assert body == 'Important\nMulti-line\nContent'

    def test_unicode_values(self):
        content = '---\nname: test\n---\n中文内容'
        updated = update_frontmatter(content, {'description': '描述'})
        meta, body = parse_frontmatter(updated)
        assert meta['description'] == '描述'
        assert '中文内容' in body

    def test_roundtrip_idempotent_for_same_data(self):
        """Updating with same values should produce parseable result."""
        content = '---\nstatus: OPEN\n---\nBody'
        updated = update_frontmatter(content, {'status': 'OPEN'})
        meta, body = parse_frontmatter(updated)
        assert meta['status'] == 'OPEN'
        assert body == 'Body'
