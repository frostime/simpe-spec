"""Basic tests for sspec."""

import tempfile
from pathlib import Path

from sspec.core import (
    SSPEC_DIR,
    copy_template,
    create_change,
    find_sspec_root,
    get_template_dir,
)


def test_find_sspec_root_not_found():
    """Test that find_sspec_root returns None when not in sspec project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = find_sspec_root(Path(tmpdir))
        assert result is None


def test_get_template_dir_exists():
    """Test that template directory exists."""
    template_dir = get_template_dir()
    assert template_dir.exists()
    assert (template_dir / 'AGENTS.md').exists()


def test_copy_template_with_replacements():
    """Test template copying with variable replacement."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / 'src.md'
        src.write_text('Hello {{NAME}}!')

        dest = Path(tmpdir) / 'dest.md'
        copy_template(src, dest, {'NAME': 'World'})

        assert dest.read_text() == 'Hello World!'
