"""Command-level tests for `sspec project` workflows."""

from __future__ import annotations

import json
import re
from pathlib import Path

from click.testing import CliRunner

from sspec.cli import main
from sspec.commands import project as project_cmd
from sspec.core import SCHEMA_VERSION, SSPEC_DIR
from sspec.services.project_init_service import initialize_project
from sspec.services.project_update_service import MissingSkillLocationRecovery


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
                'skill_install_strategies': {'.sspec/skills': 'copy'},
            }
        ),
        encoding='utf-8',
    )

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['project', 'update'])

    assert result.exit_code == 0
    new_meta = json.loads(meta_path.read_text(encoding='utf-8'))
    assert new_meta.get('meta_schema') == '2.1'
    assert new_meta.get('sspec_schema') == SCHEMA_VERSION
    assert 'meta_schema_version' not in new_meta
    assert 'schema_version' not in new_meta
    assert 'skill_install_strategies' not in new_meta


def test_project_update_persists_sspec_schema_drift(tmp_path: Path, monkeypatch):
    sspec_root = _init_project(tmp_path)
    meta_path = sspec_root / '.meta.json'
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    meta['sspec_schema'] = '6.2'
    meta_path.write_text(json.dumps(meta), encoding='utf-8')

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['project', 'update'])

    assert result.exit_code == 0
    new_meta = json.loads(meta_path.read_text(encoding='utf-8'))
    assert new_meta.get('sspec_schema') == SCHEMA_VERSION
    assert f'Updated sspec_schema to {SCHEMA_VERSION}' in result.output


def test_project_update_migrates_6_2_layout_to_7_0(tmp_path: Path, monkeypatch):
    sspec_root = _init_project(tmp_path)
    meta_path = sspec_root / '.meta.json'
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    meta['sspec_schema'] = '6.2'
    meta.get('file_hashes', {}).pop('SSPEC.rule.md', None)
    meta_path.write_text(json.dumps(meta), encoding='utf-8')
    (sspec_root / 'SSPEC.rule.md').unlink()
    (tmp_path / 'AGENTS.md').write_text(
        '<!-- SSPEC:START -->\n# .sspec Agent Protocol\n\nold full rule\n<!-- SSPEC:END -->\n',
        encoding='utf-8',
    )

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['project', 'update'])

    assert result.exit_code == 0
    new_meta = json.loads(meta_path.read_text(encoding='utf-8'))
    agents = (tmp_path / 'AGENTS.md').read_text(encoding='utf-8')
    rule = (sspec_root / 'SSPEC.rule.md').read_text(encoding='utf-8')
    assert new_meta.get('sspec_schema') == SCHEMA_VERSION
    assert 'SSPEC.rule.md' in new_meta.get('file_hashes', {})
    assert '# sspec Router' in agents
    assert 'old full rule' not in agents
    assert '## 2. Change Lifecycle' not in agents
    assert '## 2. Change Lifecycle' in rule
    assert re.search(r'SSPEC_SCHEMA::' + re.escape(SCHEMA_VERSION), agents)


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


def test_project_update_reports_missing_skill_location_recovery(tmp_path: Path, monkeypatch):
    sspec_root = _init_project(tmp_path)
    meta_path = sspec_root / '.meta.json'
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    meta['skill_locations'] = ['.sspec/skills', '.github/skills']
    meta_path.write_text(json.dumps(meta), encoding='utf-8')

    calls: list[tuple[Path, Path, bool]] = []

    def _fake_recover_missing_skill_locations(
        *,
        project_root: Path,
        sspec_root: Path,
        meta: dict,
        dry_run: bool = False,
    ):
        del meta
        calls.append((project_root, sspec_root, dry_run))
        return [
            MissingSkillLocationRecovery(
                location='.github/skills',
                dominate_dir=project_root / '.github',
                status='linked',
                link_kind='link/copy',
            )
        ]

    monkeypatch.setattr(
        project_cmd,
        'recover_missing_skill_locations',
        _fake_recover_missing_skill_locations,
    )

    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ['project', 'update', '--dry-run'])

    assert result.exit_code == 0
    assert 'Missing Skill Location Recovery' in result.output
    assert 'Would recover 1 missing skill location(s)' in result.output
    assert len(calls) == 1
    assert calls[0][0] == tmp_path
    assert calls[0][1] == sspec_root
    assert calls[0][2] is True
