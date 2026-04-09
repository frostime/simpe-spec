---
change: "pareto-cleanup"
updated: "2026-04-09T19:48"
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Memory-only summary model ✅
- [x] Update `src/sspec/core.py` — simplify `ChangeStatusSummary` around the supported `memory.md` contract and add a missing-memory flag
- [x] Refactor `src/sspec/services/change_service.py` — parse `State`, `Milestones`, and `Coordination`; remove `handover.md` / legacy section fallback in summary and validation paths
- [x] Add service coverage in `tests/test_change_service.py` — new single/root summary cases plus explicit unsupported-legacy cases
**Verification**: `uv run pytest tests/test_change_service.py -q`

### Phase 2: Status CLI cutover ✅
- [x] Update `src/sspec/commands/change.py` — render `Current State`, `Latest Milestone`, and `Coordination`; make unsupported old shapes explicit instead of parsing them
- [x] Add command coverage in `tests/test_change_command.py` — verify new single/root output and missing-memory output
**Verification**: `uv run pytest tests/test_change_command.py -q`

### Phase 3: Docs and template closure ✅
- [x] Update `src/sspec/howto/resume-change.md` — make `State` the primary resume source and stop presenting legacy sections as supported workflow
- [x] Update `src/sspec/howto/write-memory.md` — clarify `State` authority, `Milestones` append-only usage, and root `Coordination` semantics
- [x] Update `src/sspec/templates/change/memory.md` and `src/sspec/templates/change-root/memory.md` — tighten comments so the canonical memory schema is explicit
- [x] Update `src/sspec/templates/skills/sspec-implement/SKILL.md` — replace lingering `Session Log` guidance with `Knowledge` + `Milestones`
- [x] Update `src/sspec/templates/skills/sspec-design/SKILL.md` and `src/sspec/templates/skills/sspec-design/examples-docs.md` — remove remaining phase-level `Research` / `Handover` wording
**Verification**: source wording is internally consistent and no product-facing lifecycle examples describe `Research` or `Handover` as the current workflow contract

### Phase 4: Self-host sync and verification ✅
- [x] Run `uv pip install -e .`
- [x] Run `uv run sspec project update`
- [x] Run `uv run pytest tests/test_change_service.py tests/test_change_command.py -q`
- [ ] Run `uv run ruff check src/`
- [x] Sandbox-check `sspec change new/status` for both single and root changes under `tmp/`, plus one old-shape change status case
**Verification**: self-hosted copies plus sandbox output reflect the repaired contract and explicit old-shape cutoff; focused tests pass. Repository-wide `ruff check src/` still reports pre-existing unrelated `treesitter.py` issues and was intentionally not modified in this change.

---

## Progress

**Overall**: 100%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1: Memory-only summary model | 100% | ✅ |
| Phase 2: Status CLI cutover | 100% | ✅ |
| Phase 3: Docs and template closure | 100% | ✅ |
| Phase 4: Self-host sync and verification | 100% | ✅ |

**Recent**:
- Completed: memory-only summary model in `core.py` + `change_service.py`
- Completed: `change status` cutover to `State` / `Latest Milestone` / `Coordination`
- Completed: surgical wording updates in HOWTOs and SKILL/design examples; no unrelated rewrites performed
- Verified: `uv run pytest tests/test_change_service.py tests/test_change_command.py -q` → 46 passed
- Verified: `uv run sspec project update` synced self-host copies; sandbox single/root/legacy status output matches the cutover design
