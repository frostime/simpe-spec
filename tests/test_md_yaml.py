"""Tests for md_yaml module."""

import pytest

from sspec.libs.md_yaml import parse_frontmatter, update_frontmatter


class TestParseFrontmatter:
    """Tests for parse_frontmatter function."""

    def test_valid_frontmatter(self):
        """Parse valid YAML frontmatter."""
        content = "---\nkey: value\nstatus: OPEN\n---\nBody content"
        meta, body = parse_frontmatter(content)

        assert meta == {'key': 'value', 'status': 'OPEN'}
        assert body == 'Body content'

    def test_no_frontmatter(self):
        """Handle content without frontmatter."""
        content = "Just plain content"
        meta, body = parse_frontmatter(content)

        assert meta == {}
        assert body == "Just plain content"

    def test_empty_frontmatter(self):
        """Handle empty YAML frontmatter."""
        content = "---\n---\nBody"
        meta, body = parse_frontmatter(content)

        assert meta == {}
        assert body == 'Body'

    def test_incomplete_frontmatter(self):
        """Handle incomplete frontmatter (only one separator)."""
        content = "---\nkey: value"
        meta, body = parse_frontmatter(content)

        assert meta == {}
        assert body == content

    def test_invalid_yaml(self):
        """Handle invalid YAML syntax."""
        content = "---\ninvalid: yaml: syntax:\n---\nBody"
        meta, body = parse_frontmatter(content)

        assert meta == {}
        assert body == 'Body'

    def test_complex_yaml(self):
        """Parse complex YAML structures."""
        content = """---
reference:
  - source: "path/to/file"
    type: "request"
    note: "Some note"
status: DOING
---
Content here"""
        meta, body = parse_frontmatter(content)

        assert 'reference' in meta
        assert isinstance(meta['reference'], list)
        assert meta['reference'][0]['source'] == 'path/to/file'
        assert meta['status'] == 'DOING'
        assert body == 'Content here'

    def test_multiline_body(self):
        """Preserve multiline body content."""
        content = "---\nkey: value\n---\nLine 1\nLine 2\nLine 3"
        meta, body = parse_frontmatter(content)

        assert meta == {'key': 'value'}
        assert body == "Line 1\nLine 2\nLine 3"

    def test_body_with_leading_newlines(self):
        """Strip leading newlines from body."""
        content = "---\nkey: value\n---\n\n\nBody"
        meta, body = parse_frontmatter(content)

        assert body == "Body"


class TestUpdateFrontmatter:
    """Tests for update_frontmatter function."""

    def test_update_existing_field(self):
        """Update existing frontmatter field."""
        content = "---\nstatus: OPEN\n---\nBody"
        updated = update_frontmatter(content, {'status': 'DONE'})

        meta, body = parse_frontmatter(updated)
        assert meta['status'] == 'DONE'
        assert body == 'Body'

    def test_add_new_field(self):
        """Add new field to existing frontmatter."""
        content = "---\nstatus: OPEN\n---\nBody"
        updated = update_frontmatter(content, {'archived': '2026-02-05'})

        meta, body = parse_frontmatter(updated)
        assert meta['status'] == 'OPEN'
        assert meta['archived'] == '2026-02-05'

    def test_create_frontmatter_when_none(self):
        """Create frontmatter when none exists."""
        content = "Original body"
        updated = update_frontmatter(content, {'status': 'DONE'})

        meta, body = parse_frontmatter(updated)
        assert meta['status'] == 'DONE'
        assert body == 'Original body'

    def test_update_multiple_fields(self):
        """Update multiple fields at once."""
        content = "---\nstatus: OPEN\ntype: feature\n---\nBody"
        updated = update_frontmatter(content, {
            'status': 'DONE',
            'archived': '2026-02-05',
            'type': 'bugfix'
        })

        meta, body = parse_frontmatter(updated)
        assert meta['status'] == 'DONE'
        assert meta['archived'] == '2026-02-05'
        assert meta['type'] == 'bugfix'

    def test_update_complex_structure(self):
        """Update complex YAML structures."""
        content = "---\nstatus: OPEN\n---\nBody"
        updated = update_frontmatter(content, {
            'reference': [
                {'source': 'requests/test.md', 'type': 'request'}
            ]
        })

        meta, body = parse_frontmatter(updated)
        assert 'reference' in meta
        assert isinstance(meta['reference'], list)
        assert meta['reference'][0]['source'] == 'requests/test.md'

    def test_preserve_body_content(self):
        """Ensure body content is preserved."""
        content = "---\nkey: value\n---\nImportant\nBody\nContent"
        updated = update_frontmatter(content, {'new_key': 'new_value'})

        meta, body = parse_frontmatter(updated)
        assert body == "Important\nBody\nContent"

    def test_unicode_handling(self):
        """Handle Unicode characters correctly."""
        content = "---\nname: test\n---\nBody with 中文"
        updated = update_frontmatter(content, {'description': '描述'})

        meta, body = parse_frontmatter(updated)
        assert meta['description'] == '描述'
        assert '中文' in body
