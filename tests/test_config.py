"""Tests for sspec.config — YAML-based configuration."""

from __future__ import annotations

from pathlib import Path

from sspec.config import SspecConfig, get_config


class TestSspecConfig:
    def test_defaults_when_no_file(self, tmp_path: Path):
        config = SspecConfig.load(tmp_path)
        assert config.editor is None
        assert config.default_change_type == ''
        assert 'PLANNING' in config.statuses
        assert 'DONE' in config.statuses

    def test_load_from_file(self, tmp_path: Path):
        (tmp_path / 'config.yaml').write_text(
            'editor: code {file}\ndefault_change_type: feature\n', encoding='utf-8'
        )
        config = SspecConfig.load(tmp_path)
        assert config.editor == 'code {file}'
        assert config.default_change_type == 'feature'

    def test_save_and_reload(self, tmp_path: Path):
        config = SspecConfig(editor='vim', default_change_type='bugfix')
        config.save(tmp_path)
        loaded = SspecConfig.load(tmp_path)
        assert loaded.editor == 'vim'
        assert loaded.default_change_type == 'bugfix'

    def test_corrupt_yaml_returns_defaults(self, tmp_path: Path):
        (tmp_path / 'config.yaml').write_text('{{not yaml}}', encoding='utf-8')
        config = SspecConfig.load(tmp_path)
        assert config.editor is None

    def test_get_config_convenience(self, tmp_path: Path):
        config = get_config(tmp_path)
        assert isinstance(config, SspecConfig)
