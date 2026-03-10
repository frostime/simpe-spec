---
change: "howto-integration-optimize"
updated: "2026-03-10T14:17"
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: New Builtin HOWTOs ⏳
- [ ] Create `src/sspec/howto/resume-change.md` with read-order procedure and `sspec` commands for locating/verifying a change
- [ ] Create `src/sspec/howto/write-handover.md` with Session Log format rules, Working Memory update rules, and promotion triggers
**Verification**: `uv run sspec howto list` shows both new HOWTOs; `uv run sspec howto resume-change write-handover` returns both bodies; `uv run pytest tests/test_howto_command.py` passes

### Phase 2: AGENTS.md Template Updates ⏳
- [ ] Add `### HOWTO System` discovery block to §5 Reference in `src/sspec/templates/AGENTS.md` (after SKILL System)
- [ ] Add `sspec howto list` row to CLI Quick Reference table in §5 Reference
- [ ] Add HOWTO pointer to §1 Background rule for timestamps (`get-current-time`)
- [ ] Add HOWTO pointer to §1 Background rule for alignment (`use-sspec-ask`)
- [ ] Slim §3 Alignment `@align` tool choice block; add `📚 Full flow: sspec howto use-sspec-ask` footer line
**Verification**: Template renders cleanly; `sspec project update --dry-run` shows expected diff; managed block in root `AGENTS.md` updated correctly after `sspec project update`

### Phase 3: SKILL File Integration ⏳
- [ ] `sspec-research` SKILL: add `→ sspec howto find-change` near resume tip; add `→ sspec howto read-long-mdfile` near file reading section
- [ ] `sspec-implement` SKILL: add `→ sspec howto update-change-status` after status update guidance
- [ ] `sspec-handover` SKILL: add `→ sspec howto get-current-time` near timestamp rule; add `→ sspec howto write-handover` near Session Log procedure
**Verification**: Each SKILL file loads cleanly; `uv pip install -e .` and `uv run sspec skill list` show updated files

### Phase 4: Sync & Validation ⏳
- [ ] Run `uv pip install -e .` to ensure package re-installs with new HOWTO files
- [ ] Run `uv run sspec project update` to sync AGENTS.md managed block and SKILL copies
- [ ] Run `uv run ruff check src/` and `uv run ruff format src/`
- [ ] Run `uv run pytest tests/test_howto_command.py tests/test_project_init_service.py tests/test_project_update_service.py`
- [ ] Smoke check: `uv run sspec howto list`, `uv run sspec howto resume-change`, `uv run sspec howto write-handover`
**Verification**: All tests pass; no lint errors; new HOWTOs show in list output

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

**Overall**: 0%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1: New Builtin HOWTOs | 0% | ⏳ |
| Phase 2: AGENTS.md Updates | 0% | ⏳ |
| Phase 3: SKILL File Integration | 0% | ⏳ |
| Phase 4: Sync & Validation | 0% | ⏳ |

**Recent**:
- (none yet)
