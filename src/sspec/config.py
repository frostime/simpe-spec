"""sspec configuration management."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml

CONFIG_FILE = 'config.yaml'
GLOBAL_CONFIG_FILE = 'sspec.config.yaml'
GLOBAL_CONFIG_DIR = Path.home() / '.config' / 'sspec'
DEFAULT_SSPEC_EDITOR = 'code {file}'


@dataclass
class SspecConfig:
    """sspec configuration."""

    editor: str | None = None
    default_change_type: str = ''
    statuses: list[str] = field(
        default_factory=lambda: ['PLANNING', 'DOING', 'BLOCKED', 'REVIEW', 'DONE']
    )

    @classmethod
    def load(cls, sspec_root: Path) -> 'SspecConfig':
        """Load configuration from file or return defaults."""

        config_path = sspec_root / CONFIG_FILE
        if not config_path.exists():
            return cls()

        try:
            data = yaml.safe_load(config_path.read_text(encoding='utf-8')) or {}
            return cls(
                editor=data.get('editor'),
                default_change_type=data.get('default_change_type', ''),
                statuses=data.get('statuses', cls().statuses),
            )
        except (yaml.YAMLError, OSError):
            return cls()

    def save(self, sspec_root: Path) -> None:
        """Persist configuration to file."""

        config_path = sspec_root / CONFIG_FILE
        data = {
            'editor': self.editor,
            'default_change_type': self.default_change_type,
            'statuses': self.statuses,
        }
        data = {k: v for k, v in data.items() if v is not None}
        config_path.write_text(
            yaml.dump(data, default_flow_style=False, allow_unicode=True), encoding='utf-8'
        )


def get_config(sspec_root: Path) -> SspecConfig:
    """Convenience loader."""

    return SspecConfig.load(sspec_root)


@dataclass
class GlobalSspecConfig:
    """Global sspec configuration under ~/.config/sspec/sspec.config.yaml."""

    sspec_editor: str = DEFAULT_SSPEC_EDITOR

    @classmethod
    def load(cls, config_path: Path | None = None) -> 'GlobalSspecConfig':
        """Load global config from file or return defaults."""

        path = config_path or (GLOBAL_CONFIG_DIR / GLOBAL_CONFIG_FILE)
        if not path.exists():
            return cls()

        try:
            data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
            editor_value = data.get(
                'SSPEC_EDITOR',
                data.get('sspec_editor', DEFAULT_SSPEC_EDITOR),
            )
            return cls(
                sspec_editor=editor_value or DEFAULT_SSPEC_EDITOR
            )
        except (yaml.YAMLError, OSError):
            return cls()

    def save(self, config_path: Path | None = None) -> Path:
        """Persist global configuration to disk."""

        path = config_path or (GLOBAL_CONFIG_DIR / GLOBAL_CONFIG_FILE)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'SSPEC_EDITOR': self.sspec_editor,
        }
        path.write_text(
            yaml.dump(data, default_flow_style=False, allow_unicode=True),
            encoding='utf-8',
        )
        return path


def get_global_config(config_path: Path | None = None) -> GlobalSspecConfig:
    """Convenience loader for global config."""

    return GlobalSspecConfig.load(config_path)
