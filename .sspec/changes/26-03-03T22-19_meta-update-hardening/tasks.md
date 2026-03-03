---
change: "meta-update-hardening"
updated: "2026-03-03"
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Meta Schema Strictness ⏳
- [ ] Treat declared-but-unparseable `meta_schema`/`meta_schema_version` as error (do not coerce to `0.0`) `src/sspec/services/meta_service.py`
- [ ] Ensure `load_meta()` / non-update call sites fail with CLI-friendly error (no traceback) when meta schema is future/invalid `src/sspec/services/meta_service.py`
**Verification**: `uv run pytest -q` (schema strictness tests); manually set `.sspec/.meta.json` to `{"meta_schema":"2.0-beta"}` and confirm `sspec project update --dry-run` errors cleanly.

### Phase 2: Project Update Correctness (Unknown/Hashes) ⏳
- [ ] Do not print "All files are up to date" when any candidate is `unknown` or `modified` and blocks safe update `src/sspec/commands/project.py`
- [ ] When `file_hashes` missing/empty, backfill hashes for verifiably `current` candidates so the project becomes updateable without `--force` `src/sspec/commands/project.py`
- [ ] Ensure migration-only write path also persists `file_hashes`/`managed_skills` when needed `src/sspec/commands/project.py`
**Verification**: construct a project with empty `.meta.json` and verify `project update --dry-run` reports blockers; run non-dry-run and verify `.meta.json` gains hashes for current files.

### Phase 3: Path Normalization & Input Validation ⏳
- [ ] Normalize `skill_locations` storage to POSIX (`as_posix()`) during init `src/sspec/services/project_init_service.py`
- [ ] Normalize/clean existing `skill_locations` during meta upgrade (optional if minimal) `src/sspec/services/meta_service.py`
- [ ] `skill dominate` resolves relative paths from project root (not CWD) `src/sspec/commands/skill.py`
- [ ] `skill dominate` records location even if already linked (`skipped`) `src/sspec/commands/skill.py`
- [ ] Validate skill name to prevent path traversal `src/sspec/services/skill_service.py`
- [ ] Validate `--skill-loc` and custom path input: must be relative and inside project root `src/sspec/commands/project.py`
**Verification**: add tests for path validation and normalization; manually run `sspec skill dominate .claude` from a nested directory.

### Phase 4: Bug Fixes (Small but Critical) ⏳
- [ ] Remove duplicate/unreachable return in `create_skill_in_hub()` `src/sspec/services/skill_service.py`
**Verification**: `uv run ruff check src tests`

### Phase 5: Tests ⏳
- [ ] Add tests for invalid schema marker (declared but unparsable) `tests/test_meta_service.py`
- [ ] Add tests ensuring `project update` doesn't claim up-to-date with unknown candidates and backfills hashes `tests/test_project_command.py`
- [ ] Add tests for `--skill-loc` and skill name validation `tests/`
**Verification**: `uv run pytest -q`

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

- Status: PLANNING
- Notes: Created this change as a follow-up hardening pass after the meta schema v2 work.

**Overall**: 0%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 0% | ⏳ |
| Phase 2 | 0% | ⏳ |
| Phase 3 | 0% | ⏳ |
| Phase 4 | 0% | ⏳ |
| Phase 5 | 0% | ⏳ |

**Recent**:
- (none yet)
