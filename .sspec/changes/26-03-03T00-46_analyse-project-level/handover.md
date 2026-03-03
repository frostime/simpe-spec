# Handover: analyse-project-level

**Updated**: 2026-03-03

---

## Background
Investigated 5 project-level issues around `.meta.json` design, `project init` skill location options, SKILL dominate meta tracking, meta schema versioning, and `.sspec/.gitignore` adequacy. All 5 fixes designed and implemented in a single session.

## This Session

### Accomplished
- **A1a Bug fixed**: `skill_service.py:create_skill_in_hub()` was writing `__version__` into `meta['updated_at']` — now correctly uses `datetime.now().isoformat()`
- **A1b/A4 meta schema v2**: Introduced explicit meta schema `meta_schema = 2.0` and renamed keys `schema_version -> sspec_schema`, `meta_schema_version -> meta_schema`
- **A1b defaults + model**: Added `MetaModel` + `upgrade_meta()` + `load_meta_latest()` in `meta_service.py` (schema-driven migrations; preserves unknown keys)
- **A2 `.agent` → `.agents`**: `core.py:WORKSPACE_DIRS`, `_interactive_skill_selection()`, CLI option fallback all updated
- **A2 custom dir**: `_interactive_skill_selection()` now has an "Enter custom path…" option at the end of the checkbox that triggers a `questionary.text()` prompt; `--skill-loc` CLI option changed from restricted `Choice` to free `str`
- **A3 dominate meta**: `skill.py:dominate` command now calls `_record_dominate_location()` after any successful (non-skipped) dominate to write the location into `.meta.json:skill_locations`
- **A4 migration mandatory in update**: Meta migration is an explicit first stage of `sspec project update` (`prepare_meta_for_project_update()`); migrations are persisted even if no other files change
- **A4 future schema handling**: Unsupported future `meta_schema` fails with a CLI-friendly error (no traceback)
- **A5 gitignore simplified**: `DEFAULT_GITIGNORE` now only ignores `skills/**` and `tmp/**`; changes/requests/asks are tracked in git by default
- Spec-doc: Added `.sspec/spec-docs/meta-json.md` describing `.meta.json` schema, migration strategy, and update-time guarantees
- Tests: all passing, ruff lint clean

### Next Steps
- Sanity test: run `sspec project update` once in this repo to migrate legacy `.sspec/.meta.json` (currently still has `schema_version`)
- Sanity test: `sspec project init` in `tmp/test_new_init/` to verify `.agents` option + gitignore
- If satisfied → `sspec change archive`

## Working Memory

### Key Files
- `src/sspec/services/meta_service.py` — `META_SCHEMA = 2.0`, `MetaModel`, `upgrade_meta()`, `load_meta_latest()`
- `src/sspec/services/project_update_service.py` — `prepare_meta_for_project_update()` (mandatory migration stage)
- `src/sspec/commands/project.py` — persists meta migration even with no file updates; CLI-friendly schema errors
- `.sspec/spec-docs/meta-json.md` — spec-doc for meta schema + migrations
- `src/sspec/services/project_init_service.py` — new gitignore, `meta_schema` + `sspec_schema` in meta write
- `src/sspec/services/skill_service.py` — fixed `updated_at` bug, removed now-unused `__version__` import
- `src/sspec/commands/project.py` — `.agent` → `.agents`, custom dir prompt, `--skill-loc` as free str
- `src/sspec/commands/skill.py` — `_record_dominate_location()` helper + call after dominate
- `src/sspec/core.py` — `WORKSPACE_DIRS` renamed `.agent` → `.agents`
- `tests/test_meta_service.py` — meta schema v2 migration tests
- `tests/test_project_command.py` — command-level tests for `project update` meta migration

### Decisions
- **A3 location**: User chose command-layer (skill.py) over service-layer for meta update. Reason: keeps `dominate_skills_location()` pure (no project_root dep).
- **A5 gitignore**: User chose minimal `skills/**, tmp/**` only. All change/request/ask data tracked by git by default.
- **A2 custom dir**: Interactive checkbox + trailing questionary.text prompt. CLI `--skill-loc` now free string (no Choice restriction).

### Notes
- The repo's current `.sspec/.meta.json` is legacy format (`schema_version`) and will be migrated to v2 keys on the next non-dry-run `project update`.
- `meta_schema` is the meta file schema; `sspec_schema` is the sspec protocol schema used by templates (independent axes).
