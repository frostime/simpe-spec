---
change: "analyse-project-level"
updated: "2026-03-03"
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Fix A1/A4 — meta.json schema v2 + migration (mandatory) ✅
- [x] Rename meta keys: `schema_version` -> `sspec_schema`, `meta_schema_version` -> `meta_schema` `src/sspec/services/meta_service.py`
- [x] Define explicit meta model (`MetaModel`) and migration API (`upgrade_meta`, `load_meta_latest`) `src/sspec/services/meta_service.py`
- [x] Set `meta_schema = 2.0` and implement schema-based migration strategy `src/sspec/services/meta_service.py`
- [x] Make meta migration an explicit first stage of `project update` (`prepare_meta_for_project_update`) `src/sspec/services/project_update_service.py`
- [x] `project update` persists meta migration even if no file updates occur `src/sspec/commands/project.py`
- [x] CLI-friendly error when meta declares unsupported future schema `src/sspec/commands/project.py`

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
- [x] Update init/meta tests for `meta_schema` + `sspec_schema` `tests/test_project_init_service.py`
- [x] Add migration tests for legacy keys + future schema errors `tests/test_meta_service.py`
- [x] Add command-level tests to ensure `project update` always migrates meta `tests/test_project_command.py`
- [x] All tests pass, lint clean (ruff)

### Phase 6: Spec-doc ✅
- [x] Add spec-doc for `.meta.json` schema + migration + update-time guarantees `.sspec/spec-docs/meta-json.md`
- [x] Update spec-doc indexes `.sspec/spec-docs/README.md`, `.sspec/project.md`

---

## Progress
- All phases complete
- Tests passing, lint clean (ruff)
- Status: REVIEW
