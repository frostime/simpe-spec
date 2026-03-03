---
change: "analyse-project-level"
updated: "2026-03-03"
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Fix A1 — meta.json bugs & defaults ✅
- [x] Fix `updated_at` bug in `skill_service.py:create_skill_in_hub()` (was `= __version__`, should be `datetime.now().isoformat()`) `src/sspec/services/skill_service.py`
- [x] Add `META_SCHEMA_VERSION = '1'` constant to `meta_service.py` `src/sspec/services/meta_service.py`
- [x] Add `get_meta_with_defaults()` helper in `meta_service.py` `src/sspec/services/meta_service.py`
- [x] Use `meta_schema_version` (new field) when writing meta in `project_init_service.py` `src/sspec/services/project_init_service.py`

### Phase 2: Fix A2 — .agent → .agents + custom dir input ✅
- [x] Rename `.agent` → `.agents` in `core.py:WORKSPACE_DIRS` `src/sspec/core.py`
- [x] Update `_interactive_skill_selection()` in `project.py`: fix available_locations list + fallback `.agent` → `.agents` `src/sspec/commands/project.py`
- [x] Change `--skill-loc` CLI option from restricted `Choice` to free `str` type in `project.py` `src/sspec/commands/project.py`
- [x] Add custom directory prompt at end of `_interactive_skill_selection()` (questionary.text) `src/sspec/commands/project.py`

### Phase 3: Fix A3 — skill dominate updates meta ✅
- [x] After successful dominate in `skill.py:dominate` command, load meta and append the new location to `skill_locations`, save meta `src/sspec/commands/skill.py`

### Phase 4: Fix A5 — simplify .gitignore ✅
- [x] Update `DEFAULT_GITIGNORE` in `project_init_service.py` to only ignore `skills/**` and `tmp/**` `src/sspec/services/project_init_service.py`

### Phase 5: Update tests ✅
- [x] Update `test_project_init_service.py` for `meta_schema_version` field `tests/test_project_init_service.py`
- [x] Add `TestMetaSchemaVersion` and `TestGetMetaWithDefaults` test classes `tests/test_meta_service.py`
- [x] All 232 tests pass, lint clean

---

## Progress
- All 5 phases complete
- 232 tests passing, lint clean (ruff F,E,I)
- Status: REVIEW

**Overall**: 0%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 0% | ⏳ |

**Recent**:
- (none yet)
