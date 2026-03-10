# Handover: review-feedback-sync

**Updated**: 2026-03-10T23:13

---

## Background
<!-- Write once on first session. What this change does and why (1-3 sentences).
Update only if scope fundamentally changes. Details belong in spec.md. -->

This change tightens how SSPEC handles review-stage scope growth. The goal is to keep accepted review work visible in `spec.md` / `tasks.md` instead of letting it live only in `handover.md`, while still allowing true follow-up work to split into a new change.

## Git Baseline (Immutable)
<!-- Captured during `sspec change new` before any change files are written.
This section records the change starting point in git and must not be edited or refreshed later. -->

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `main`
- HEAD: `46e74443434b8e7e47afac5f97108b86924b721e`
- Worktree: `clean`
- Status Snapshot: raw `git status --short --branch` output

```text
## main...origin/main
```

## Working Memory (Stable)
<!-- Curated, long-lived context. Survives context compression and session boundaries.
If something becomes obsolete, mark it as obsolete with a timestamp instead of deleting silently. -->

### Key Files
<!-- Files critical to understanding/continuing this change.
- `path/file` - what it contains, why it matters -->

- `.sspec/changes/26-03-10T22-06_review-feedback-sync/spec.md` - Chinese design proposal for review-stage scope sync.
- `.sspec/changes/26-03-10T22-06_review-feedback-sync/tasks.md` - approved implementation plan and live progress for this change.
- `src/sspec/templates/skills/sspec-review/SKILL.md` - current review guidance and `Feedback Tasks` behavior.
- `src/sspec/templates/skills/sspec-align/SKILL.md` - alignment rules now include mandatory user approval before split / replacement changes.
- `src/sspec/templates/change/tasks.md` - existing task template with `Feedback Tasks` placeholder.
- `src/sspec/templates/change/spec.md` - current spec template; likely place to define how review amendments become official design.
- `src/sspec/howto/handle-review-scope-change.md` - new operational guide for amend vs follow-up vs supersede decisions.
- `src/sspec/howto/update-change-status.md` - updated state-machine guide including REVIEW->PLANNING / BLOCKED cases.
- `src/sspec/templates/AGENTS.md` - updated global guardrails for `@sync` and mandatory `@align` before split / replacement changes.

### Durable Memory (Typed, Timestamped)
<!-- Promote only facts still useful after the current batch ends.
Single/sub change preferred types: Alignment, Decision, VitalFinding, Constraint, Risk, VerificationShortcut.
Use a custom type only when none fit well; keep it short and clear.
- [2026-03-06T20:39] [Decision] Redis over Memcached because per-key TTL + persistence matter.
- [2026-03-06T20:39] [Constraint] Session Log stays append-only; real next action lives there.
Project-wide items -> ALSO append to project.md Notes. -->

- [2026-03-10T22:10] [VitalFinding] Repo already has `Feedback Tasks`; the real gap is missing spec-sync and missing guidance for when accepted review work should become a follow-up change.
- [2026-03-10T22:10] [Decision] Design starts from explicit review-stage classification instead of letting handover absorb accepted scope drift.
- [2026-03-10T22:27] [Alignment] User added a fourth case: if the current change is fundamentally wrong, mark it `BLOCKED` and continue in a new replacement change.
- [2026-03-10T22:33] [Alignment] Any split into a new change, including follow-up or replacement after `BLOCKED`, must be user-approved through `@align`; the agent cannot self-decide.
- [2026-03-10T22:37] [Alignment] User approved the revised design and asked to move into plan phase.
- [2026-03-10T22:53] [VerificationShortcut] Validation sandbox lives at `tmp/test_review_feedback_sync`; use it to inspect generated `spec.md` / `tasks.md` plus `sspec howto handle-review-scope-change update-change-status` output.
- [2026-03-10T23:08] [Alignment] User requested that subagent audit become a named review directive, exposed as `@subagent-audits` with a pointer to `sspec howto make-subagent-audit`.
- [2026-03-10T23:13] [Decision] Use the normalized directive name `@subagent-audits` and keep it lightweight: shortcut only, with procedural detail delegated to `sspec howto make-subagent-audit`.

## Session Log (Append-Only)
<!-- Newest entry first. Each entry is an atomic batch (one cohesive work record).

Header format:
### 2026-03-06T20:39 [work-log] <short title>

Tags are freeform but must be readable. Examples: work-log, user-feedback, argue, risk.
Any user interaction (feedback, @align, @argue) MUST start a new log entry. -->

### 2026-03-10T23:13 [work-log] Added subagent audit review shortcut

**Accomplished**
- Added `@subagent-audits` to the directive shortcuts in `src/sspec/templates/AGENTS.md`.
- Added a point-of-need directive mention to `src/sspec/templates/skills/sspec-review/SKILL.md` that points to `sspec howto make-subagent-audit`.
- Re-synced root and sandbox projects, then verified the generated `AGENTS.md` and review skill expose the directive without duplicating HOWTO details.

**Next**
- User review whether the naming and placement of `@subagent-audits` feel right.
- If accepted, return the change to `DONE` and optionally rerun subagent audit for the final staged diff.

**Notes** (optional)
- This feedback stayed within the current change because it improves the same review workflow rather than creating a separate follow-up feature.

### 2026-03-10T23:08 [user-feedback] Add subagent audit directive shortcut

**Accomplished**
- User proposed promoting subagent audit into a first-class review directive so Agents can discover it more reliably.
- Reopened the current change as in-scope review feedback and added feedback tasks for the directive shortcut, template sync, and validation.

**Next**
- Update review-facing docs to expose `@subagent-audits` and point to `sspec howto make-subagent-audit`.
- Re-sync templates and verify generated AGENTS / review skill output in the sandbox.

**Notes** (optional)
- The user only wants a lightweight directive entry plus HOWTO reference, not a duplicated procedural write-up.

### 2026-03-10T22:53 [work-log] Implemented review-scope guidance update

**Accomplished**
- Completed all planned tasks and moved the change to `REVIEW`.
- Updated review / align / implement guidance, single-change spec/tasks templates, `@sync` wording in `src/sspec/templates/AGENTS.md`, and `src/sspec/howto/update-change-status.md`.
- Added `src/sspec/howto/handle-review-scope-change.md`, ran template sync, and validated generated output in `tmp/test_review_feedback_sync`.

**Next**
- User review the wording and workflow boundaries across the updated docs.
- If accepted, mark the change `DONE` and archive it.

**Notes** (optional)
- During validation, `sspec howto update-change-status` showed Unicode arrow mojibake in the Windows terminal, so the touched HOWTO was normalized to ASCII arrows.

### 2026-03-10T22:33 [user-feedback] Require align before split or replace

**Accomplished**
- User clarified that opening any new change from review feedback is not an agent-autonomous action.
- Updated the design to make `@align` mandatory before either follow-up split or `BLOCKED` replacement flow.

**Next**
- Present the revised design back to the user for confirmation.
- If confirmed, move to plan phase.

**Notes** (optional)
- This user gate applies to both ordinary follow-up changes and superseding replacements.

### 2026-03-10T22:37 [work-log] Draft plan from approved design

**Accomplished**
- User approved the revised design direction and asked to proceed to planning.
- Filled `tasks.md` with three phases covering review classification rules, alignment/status guardrails, and HOWTO plus validation work.

**Next**
- Present the task breakdown to the user for plan approval.
- Keep change status at `PLANNING` until the plan is explicitly approved.

**Notes** (optional)
- Validation is intentionally part of the plan because the work touches templates, generated self-hosted copies, and new HOWTO discovery.

### 2026-03-10T22:27 [user-feedback] Add blocked replacement path

**Accomplished**
- User accepted the general direction but added an extra branch: when the current change is completely off-track, it should not keep growing.
- Revised `spec.md` to include a `BLOCKED` + replacement-change path instead of forcing everything into follow-up vs current-change amendment.

**Next**
- After user confirms the revised design, move to plan phase.
- Keep status-guidance updates in scope during planning / implementation.

**Notes** (optional)
- This case is different from ordinary follow-up: the old change is not "done but extended"; it is superseded.

### 2026-03-10T22:10 [work-log] Draft design for review scope sync

**Accomplished**
- Created change `.sspec/changes/26-03-10T22-06_review-feedback-sync/`.
- Inspected current `sspec-review`, `sspec-implement`, `spec.md`, `tasks.md`, and `@sync` wording.
- Drafted Chinese design in `spec.md` with a triage model for review-stage additions.

**Next**
- Align with user on whether this triage model and file scope are correct.
- If approved, move to plan phase and break the design into concrete template / skill / HOWTO edits.

**Notes** (optional)
- Initial draft used three-way classification; later user feedback added a `BLOCKED` replacement branch.
