---
change: "simplify-skill-install"
updated: ""
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks
### Phase 1: Simplify install strategy logic ✅
- [x] Refactor `src/sspec/skill_installer.py` to remove elevation flow and use platform-fixed link creation.
- [x] Unify public strategy contract to `link|copy` while keeping internal symlink/junction detection.
- [x] Update init/update command/service call paths for simplified installer API `src/sspec/commands/project.py` `src/sspec/services/project_init_service.py` `src/sspec/services/project_update_service.py`
**Verification**: `uv run pytest tests/test_skill_installer.py tests/test_project_init_service.py tests/test_project_init_skill_sync.py`

### Phase 2: Remove deprecated metadata field with schema migration ✅
- [x] Bump `META_SCHEMA` to `2.1` and add `2.0 -> 2.1` migration in `src/sspec/services/meta_service.py`.
- [x] Stop writing `skill_install_strategies` in init/sync/dominate/update flows `src/sspec/services/project_init_service.py` `src/sspec/commands/skill.py` `src/sspec/services/project_update_service.py`
- [x] Keep backward-compatible strategy input normalization in installer for old values.
**Verification**: `uv run pytest tests/test_meta_service.py tests/test_project_update_service.py tests/test_project_command.py tests/test_skill_command_error_handling.py`

### Phase 3: Docs and regression checks ✅
- [x] Update spec-docs for meta schema and installation behavior `.sspec/spec-docs/meta-json.md` `.sspec/spec-docs/skill-installation.md`
- [x] Run lint and targeted tests for touched modules.
**Verification**: `uv run ruff check src/` and targeted pytest suite passed

<!-- @RULE: Organize by phases. Each task <2h, independently testable.
Phase emoji: ⏳ pending | 🚧 in progress | ✅ done

### Phase 1: <name> ⏳
- [ ] Task description `path/file.py`
- [ ] Task description `path/file.py`
**Verification**: <how to verify this phase>

### Feedback Tasks
Use this section for tasks added during review/feedback loop.
-->

---

## Progress
**Overall**: 100%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 100% | ✅ |
| Phase 2 | 100% | ✅ |
| Phase 3 | 100% | ✅ |

**Recent**:
- Completed installer refactor to platform-fixed link flow with public `link|copy` strategy.
- Added `.meta.json` schema migration to `2.1` and removed `skill_install_strategies` persistence.
- Updated docs and validated with `ruff check` + 57 targeted passing tests.
