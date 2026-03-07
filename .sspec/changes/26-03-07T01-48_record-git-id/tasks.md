---
change: "record-git-id"
updated: "2026-03-07T15:42"
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks
### Phase 1: Git baseline capture design落地 ✅
- [x] Extend `src/sspec/services/change_service.py` so `create_change()` captures git baseline before creating the change directory and passes a rendered `GIT` replacement into template copying.
- [x] Handle non-repo / git-unavailable / detached-HEAD cases in `src/sspec/services/change_service.py` without breaking change creation.
**Verification**: targeted tests cover clean repo, dirty repo, and no-repo behavior; change creation still succeeds in all three cases.

### Phase 2: Template and contract sync ✅
- [x] Add an immutable git baseline section to `src/sspec/templates/change/handover.md` and `src/sspec/templates/change-root/handover.md` using `{{GIT}}`.
- [x] Update `.sspec/spec-docs/change-lifecycle.md` to describe the new pre-creation git snapshot contract and placement in handover.
**Verification**: newly generated change handover files show the git section in both single and root templates, and the spec-doc matches runtime behavior.

### Phase 3: Regression coverage and self-host sync ✅
- [x] Add or update tests in `tests/test_change_service.py` for snapshot rendering and template output.
- [x] Run the required template/code sync flow: `uv pip install -e .`, `uv run ruff check src/`, `uv run ruff format src/`, targeted `uv run pytest ...`, and `uv run sspec project update`.
**Verification**: tests pass, lint/format are clean, and generated self-hosted copies reflect the new handover template.

### Feedback Tasks
- [x] Clarify the raw status code block and remove the extra HEAD subject field from `src/sspec/services/change_service.py`.
**Verification**: sandbox-generated handover shows `Status Snapshot` label and no longer shows `Subject`.
- [x] Update `src/sspec/templates/skills/sspec-handover/SKILL.md` and `src/sspec/templates/skills/sspec-review/SKILL.md` so agents treat the git baseline as immutable handover context and a review anchor for `git diff` / `git log` checks.
**Verification**: `uv run sspec project update` refreshed the self-hosted skills, and a fresh sandbox init showed the new guidance in generated skill files.

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
- Completed: pre-creation git snapshot rendering in `src/sspec/services/change_service.py`.
- Completed: immutable git section in both handover templates plus contract update in `.sspec/spec-docs/change-lifecycle.md`.
- Completed: regression tests, lint/format, `uv pip install -e .`, `uv run pytest tests/test_change_service.py`, and sandbox CLI verification.
- Completed: review follow-up that labels the raw status block and removes the redundant commit subject line.
- Completed: final review approval from the user; change is ready to close.
- Completed: follow-up skill guidance so handover/review phases explicitly use the recorded git baseline correctly.
