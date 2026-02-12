"""Tests for sspec.services.meta_service — .meta.json persistence."""

from __future__ import annotations

import json
from pathlib import Path

from sspec.services.meta_service import load_meta, save_meta


class TestMetaService:
    def test_load_empty_when_missing(self, sspec_root: Path):
        assert load_meta(sspec_root) == {}

    def test_save_and_load_roundtrip(self, sspec_root: Path):
        meta = {
            'schema_version': '6.1',
            'file_hashes': {'skills/sspec': 'abc123'},
            'managed_skills': ['sspec', 'sspec-ask'],
            'skill_locations': ['.sspec/skills'],
        }
        save_meta(sspec_root, meta)
        loaded = load_meta(sspec_root)
        assert loaded == meta

    def test_unicode_values(self, sspec_root: Path):
        meta = {'note': '中文测试', 'emoji': '🚀'}
        save_meta(sspec_root, meta)
        loaded = load_meta(sspec_root)
        assert loaded['note'] == '中文测试'
        assert loaded['emoji'] == '🚀'

    def test_corrupt_json_returns_empty(self, sspec_root: Path):
        (sspec_root / '.meta.json').write_text('not json', encoding='utf-8')
        assert load_meta(sspec_root) == {}

    def test_non_dict_json_returns_empty(self, sspec_root: Path):
        (sspec_root / '.meta.json').write_text('["a list"]', encoding='utf-8')
        assert load_meta(sspec_root) == {}

    def test_overwrite_existing(self, sspec_root: Path):
        save_meta(sspec_root, {'v': 1})
        save_meta(sspec_root, {'v': 2})
        assert load_meta(sspec_root) == {'v': 2}
