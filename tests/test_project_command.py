"""Command-level tests for `sspec project` workflows."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from sspec.cli import main
from sspec.core import SSPEC_DIR
from sspec.services.project_init_service import initialize_project


def _init_project(tmp_path: Path) -> Path:
    initialize_project(
        project_root=tmp_path,
        force=False,
        skill_locations=[],
        prefer_symlink=False,
    )
    return tmp_path / SSPEC_DIR


def test_project_update_migrates_meta_even_without_file_updates(tmp_path: Path, monkeypatch):
    sspec_root = _init_project(tmp_path)
    meta_path = sspec_root / '.meta.json'
    meta_path.write_text(
        json.dumps(
            {
                'meta_schema_version': '1',
                'schema_version': '9.1',
                'skill_locations': ['.sspec/skills'],
            }
        ),
        encoding='utf-8',
    )

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['project', 'update'])

    assert result.exit_code == 0
    new_meta = json.loads(meta_path.read_text(encoding='utf-8'))
    assert new_meta.get('meta_schema') == '2.0'
    assert new_meta.get('sspec_schema') == '9.1'
    assert 'meta_schema_version' not in new_meta
    assert 'schema_version' not in new_meta


def test_project_update_reports_future_meta_schema_error(tmp_path: Path, monkeypatch):
    sspec_root = _init_project(tmp_path)
    meta_path = sspec_root / '.meta.json'
    meta_path.write_text(json.dumps({'meta_schema': '999.0'}), encoding='utf-8')

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['project', 'update', '--dry-run'])

    assert result.exit_code != 0
    assert 'Failed to migrate .meta.json' in result.output
    assert 'Unsupported future meta_schema' in result.output


def test_project_update_reports_invalid_meta_schema_marker(tmp_path: Path, monkeypatch):
    sspec_root = _init_project(tmp_path)
    meta_path = sspec_root / '.meta.json'
    meta_path.write_text(json.dumps({'meta_schema': '2.0-beta'}), encoding='utf-8')

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['project', 'update', '--dry-run'])

    assert result.exit_code != 0
    assert 'Failed to migrate .meta.json' in result.output
    assert 'Invalid meta_schema' in result.output


def test_project_update_backfills_hashes_when_missing(tmp_path: Path, monkeypatch):
    sspec_root = _init_project(tmp_path)
    meta_path = sspec_root / '.meta.json'
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    meta['file_hashes'] = {}
    meta_path.write_text(json.dumps(meta), encoding='utf-8')

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['project', 'update'])

    assert result.exit_code == 0
    new_meta = json.loads(meta_path.read_text(encoding='utf-8'))
    hashes = new_meta.get('file_hashes', {})
    assert isinstance(hashes, dict)
    assert any(str(k).startswith('skills/') for k in hashes.keys())
    assert 'Backfilled' in result.output


def test_project_update_not_up_to_date_when_blocked_by_unknown(tmp_path: Path, monkeypatch):
    sspec_root = _init_project(tmp_path)
    meta_path = sspec_root / '.meta.json'
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    meta['file_hashes'] = {}
    meta_path.write_text(json.dumps(meta), encoding='utf-8')

    # Make one hub skill differ from templates so it becomes 'unknown' without hashes.
    hub = sspec_root / 'skills'
    skill_dirs = [p for p in hub.iterdir() if p.is_dir()]
    assert skill_dirs, 'Expected template skills in .sspec/skills'
    skill_file = skill_dirs[0] / 'SKILL.md'
    skill_file.write_text(
        skill_file.read_text(encoding='utf-8') + '\n# local edit\n', encoding='utf-8'
    )

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['project', 'update'])

    assert result.exit_code == 0
    assert 'All files are up to date' not in result.output
    assert 'No updates applied' in result.output
