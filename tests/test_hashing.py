"""Tests for sspec.libs.hashing — content and file hashing utilities."""

from __future__ import annotations

from pathlib import Path

from sspec.libs.hashing import compute_dir_hash, compute_file_hash, compute_hash


class TestComputeHash:
    def test_deterministic(self):
        assert compute_hash('hello') == compute_hash('hello')

    def test_different_inputs_differ(self):
        assert compute_hash('a') != compute_hash('b')

    def test_returns_16_char_hex(self):
        h = compute_hash('test')
        assert len(h) == 16
        assert all(c in '0123456789abcdef' for c in h)


class TestComputeFileHash:
    def test_existing_file(self, tmp_path: Path):
        f = tmp_path / 'test.txt'
        f.write_text('content', encoding='utf-8')
        h = compute_file_hash(f)
        assert h is not None
        assert h == compute_hash('content')

    def test_missing_file_returns_none(self, tmp_path: Path):
        assert compute_file_hash(tmp_path / 'nope.txt') is None


class TestComputeDirHash:
    def test_deterministic_for_same_content(self, tmp_path: Path):
        d = tmp_path / 'dir'
        d.mkdir()
        (d / 'a.txt').write_text('hello', encoding='utf-8')
        (d / 'b.txt').write_text('world', encoding='utf-8')
        assert compute_dir_hash(d) == compute_dir_hash(d)

    def test_different_content_differs(self, tmp_path: Path):
        d1 = tmp_path / 'd1'
        d1.mkdir()
        (d1 / 'a.txt').write_text('hello', encoding='utf-8')

        d2 = tmp_path / 'd2'
        d2.mkdir()
        (d2 / 'a.txt').write_text('world', encoding='utf-8')

        assert compute_dir_hash(d1) != compute_dir_hash(d2)

    def test_filename_changes_detected(self, tmp_path: Path):
        """Renaming a file should change the hash (paths are included)."""
        d1 = tmp_path / 'd1'
        d1.mkdir()
        (d1 / 'a.txt').write_text('same', encoding='utf-8')

        d2 = tmp_path / 'd2'
        d2.mkdir()
        (d2 / 'b.txt').write_text('same', encoding='utf-8')

        assert compute_dir_hash(d1) != compute_dir_hash(d2)

    def test_md_replacements_applied(self, tmp_path: Path):
        d = tmp_path / 'dir'
        d.mkdir()
        (d / 'doc.md').write_text('Version: {{VER}}', encoding='utf-8')

        h_with = compute_dir_hash(d, {'VER': '1.0'})
        h_without = compute_dir_hash(d, {})
        assert h_with != h_without

    def test_replacements_only_affect_md_files(self, tmp_path: Path):
        d = tmp_path / 'dir'
        d.mkdir()
        (d / 'doc.txt').write_text('{{VER}}', encoding='utf-8')

        h_with = compute_dir_hash(d, {'VER': '1.0'})
        h_without = compute_dir_hash(d, {})
        # .txt files should not have replacements applied
        assert h_with == h_without
