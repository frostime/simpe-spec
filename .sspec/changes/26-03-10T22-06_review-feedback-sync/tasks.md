---
change: "review-feedback-sync"
updated: "2026-03-10T23:13"
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Review Classification Rules ✅
- [x] Update `src/sspec/templates/skills/sspec-review/SKILL.md` - define `minor-fix` / `current-change-amend` / `follow-up-change` / `supersede-change` and the required write-back order for each path
- [x] Update `src/sspec/templates/change/spec.md` - clarify that accepted review changes must become formal design, with `### Review Amendments` as an optional structured section rather than an informal note sink
- [x] Update `src/sspec/templates/change/tasks.md` - clarify that `Feedback Tasks` holds review-added execution work, but does not replace mandatory `spec.md` updates when scope changes are accepted
**Verification**: Review guidance and change templates consistently explain when work stays in the current change, when `spec.md` must change, and when `Feedback Tasks` is the right execution bucket

### Phase 2: Alignment and State Guardrails ✅
- [x] Update `src/sspec/templates/skills/sspec-align/SKILL.md` - mark split / replacement decisions as mandatory `@align` actions with the user
- [x] Update `src/sspec/templates/skills/sspec-implement/SKILL.md` - require spec/tasks sync before continuing after implementation reveals scope drift or review-driven redesign
- [x] Update `src/sspec/howto/update-change-status.md` - document when review feedback returns a change to `PLANNING`, when it becomes `BLOCKED`, and how replacement changes relate to status transitions
- [x] Update `src/sspec/templates/AGENTS.md` - expand `@sync` so it covers `spec.md` as well as `tasks.md` / `handover.md`, and reflect that split / supersede actions require user alignment
**Verification**: Lifecycle guidance no longer permits agent-autonomous split / replace actions or accepted review changes that exist only in `handover.md`

### Phase 3: HOWTO and Validation ✅
- [x] Create `src/sspec/howto/handle-review-scope-change.md` - provide example-driven triage for amend vs follow-up vs supersede, including the mandatory user-approval gate
- [x] Run `uv pip install -e .` and `uv run sspec project update` - refresh packaged templates and sync self-hosted generated copies after editing template sources
- [x] In `tmp/`, generate a sandbox change and read the synced HOWTO / template outputs - verify the new review-scope rules appear in generated guidance and are discoverable through `sspec howto`
**Verification**: Self-hosted copies and sandbox-generated docs reflect the new review-scope rules, and `sspec howto handle-review-scope-change update-change-status` surfaces the expected guidance

### Feedback Tasks

### Feedback Tasks 🚧
- [x] Update `.sspec/changes/26-03-10T22-06_review-feedback-sync/spec.md` - record the accepted `@subagent-audits` directive addition in the current change design
- [x] Update `src/sspec/templates/skills/sspec-review/SKILL.md` and `src/sspec/templates/AGENTS.md` - surface `@subagent-audits` as a review-time directive that points to `sspec howto make-subagent-audit`
- [x] Re-run template sync and validate generated `AGENTS.md` / review skill in `tmp/test_review_feedback_sync` - confirm the directive is discoverable from an Agent's point of view
**Verification**: Review-facing generated docs mention `@subagent-audits` and point Agents to `sspec howto make-subagent-audit` without duplicating the HOWTO content

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
| Feedback follow-up | 100% | ✅ |

**Recent**:
- Completed: Re-sync templates and validate `@subagent-audits` visibility in `tmp/test_review_feedback_sync` generated `AGENTS.md` and review skill
- Completed: Add `@subagent-audits` directive references in `src/sspec/templates/AGENTS.md` and `src/sspec/templates/skills/sspec-review/SKILL.md`
- Completed: Record the accepted `@subagent-audits` addition in the current change spec
- Added: feedback task to expose `@subagent-audits` as a review directive shortcut tied to `sspec howto make-subagent-audit`
- Completed: Validate a sandbox change plus `sspec howto` output in `tmp/test_review_feedback_sync`, including an ASCII cleanup for Windows-friendly status output
- Completed: Run `uv pip install -e .` and `uv run sspec project update` to refresh templates and self-hosted copies
- Completed: Add `src/sspec/howto/handle-review-scope-change.md` with triage rules and mandatory `@align` before split / replacement
- Completed: Update `src/sspec/templates/AGENTS.md` so `@sync` covers `spec.md` and split / replacement decisions stay user-gated
- Completed: Expand `src/sspec/howto/update-change-status.md` with review-to-PLANNING / BLOCKED rules and split approval notes
- Completed: Update `src/sspec/templates/skills/sspec-implement/SKILL.md` with scope-drift sync rules and durable-memory handover guidance
- Completed: Update `src/sspec/templates/skills/sspec-align/SKILL.md` so split / replacement decisions require durable user alignment
- Completed: Update `src/sspec/templates/change/tasks.md` so `Feedback Tasks` only covers in-change work after proper spec sync
- Completed: Update `src/sspec/templates/change/spec.md` so accepted review changes become formal design instead of handover-only notes
- Completed: Update `src/sspec/templates/skills/sspec-review/SKILL.md` with review feedback classification and split/replacement guardrails
