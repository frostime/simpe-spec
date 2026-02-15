"""Tests for sspec.config — YAML-based configuration."""

from __future__ import annotations

from pathlib import Path

from sspec.config import GlobalSspecConfig, SspecConfig, get_config, get_global_config


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


class TestGlobalSspecConfig:
    def test_defaults_when_no_global_file(self, tmp_path: Path):
        config = GlobalSspecConfig.load(tmp_path / 'missing.yaml')
        assert config.sspec_editor == 'code {file}'

    def test_save_and_reload(self, tmp_path: Path):
        path = tmp_path / 'sspec.config.yaml'
        config = GlobalSspecConfig(sspec_editor='zed {file}')
        config.save(path)

        loaded = GlobalSspecConfig.load(path)
        assert loaded.sspec_editor == 'zed {file}'

    def test_get_global_config_convenience(self, tmp_path: Path):
        path = tmp_path / 'sspec.config.yaml'
        path.write_text('SSPEC_EDITOR: nvim {file}\n', encoding='utf-8')

        config = get_global_config(path)
        assert isinstance(config, GlobalSspecConfig)
        assert config.sspec_editor == 'nvim {file}'
