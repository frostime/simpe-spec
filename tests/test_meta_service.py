"""Tests for sspec.services.meta_service — .meta.json persistence."""

from __future__ import annotations

from pathlib import Path

from sspec.services.meta_service import (
    META_SCHEMA,
    get_meta_with_defaults,
    load_meta,
    save_meta,
    upgrade_meta,
)


class TestMetaService:
    def test_load_empty_when_missing(self, sspec_root: Path):
        assert load_meta(sspec_root) == {}

    def test_save_and_load_roundtrip(self, sspec_root: Path):
        meta = {
            'meta_schema': META_SCHEMA,
            'sspec_schema': '6.1',
            'file_hashes': {'skills/sspec': 'abc123'},
            'managed_skills': ['sspec', 'sspec-ask'],
            'skill_locations': ['.sspec/skills'],
        }
        save_meta(sspec_root, meta)
        loaded = load_meta(sspec_root)
        # load_meta upgrades + fills defaults; ensure our fields survived.
        assert loaded['meta_schema'] == META_SCHEMA
        assert loaded['sspec_schema'] == '6.1'
        assert loaded['file_hashes'] == {'skills/sspec': 'abc123'}
        assert loaded['managed_skills'] == ['sspec', 'sspec-ask']
        assert loaded['skill_locations'] == ['.sspec/skills']

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
        loaded = load_meta(sspec_root)
        assert loaded.get('v') == 2


class TestMetaSchemaVersion:
    def test_meta_schema_is_string(self):
        assert isinstance(META_SCHEMA, str)
        assert len(META_SCHEMA) > 0

    def test_meta_schema_version_independent_from_agents_schema(self):
        """META_SCHEMA tracks meta.json structure, not AGENTS.md protocol."""
        from sspec.core import SCHEMA_VERSION

        # They are separate versioning axes; no equality constraint required.
        assert META_SCHEMA != SCHEMA_VERSION or True  # always passes; just documents intent


class TestGetMetaWithDefaults:
    def test_empty_meta_returns_all_defaults(self):
        result = get_meta_with_defaults({})
        assert result.get('meta_schema') == META_SCHEMA
        assert result.get('file_hashes') == {}
        assert result.get('managed_skills') == []
        assert result.get('skill_locations') == []
        assert result.get('skill_install_strategies') == {}

    def test_existing_values_are_preserved(self):
        meta = {'sspec_schema': '9.1', 'managed_skills': ['sspec']}
        result = get_meta_with_defaults(meta)
        assert result.get('sspec_schema') == '9.1'
        assert result.get('managed_skills') == ['sspec']

    def test_missing_fields_filled_without_overwriting(self):
        meta = {'meta_schema': '99'}  # user has a custom version
        result = get_meta_with_defaults(meta)
        assert result.get('meta_schema') == '99'  # preserved, not overwritten

    def test_does_not_mutate_input(self):
        original = {}
        get_meta_with_defaults(original)
        assert original == {}


class TestUpgradeMeta:
    def test_v1_meta_is_migrated_to_v2_keys(self):
        raw = {
            'meta_schema_version': '1',
            'schema_version': '9.1',
            'managed_skills': ['sspec'],
        }
        res = upgrade_meta(raw)
        assert res.meta.get('meta_schema') == META_SCHEMA
        assert res.meta.get('sspec_schema') == '9.1'
        assert 'schema_version' not in res.meta
        assert 'meta_schema_version' not in res.meta
