# Handover: record-git-id

**Updated**: 2026-03-07T15:42

---

## Background
This change adds an immutable git baseline snapshot to newly created change handovers. The goal is to let future Agents see the branch / HEAD / dirty-worktree state that existed before the change itself modified `git status`.

## Working Memory (Stable)
<!-- Curated, long-lived context. Survives context compression and session boundaries.
If something becomes obsolete, mark it as obsolete with a timestamp instead of deleting silently. -->

### Key Files
- `src/sspec/services/change_service.py` - `create_change()` owns template rendering timing, so pre-creation git capture must happen here.
- `src/sspec/templates/change/handover.md` - single-change handover template that will expose the immutable git baseline section.
- `src/sspec/templates/change-root/handover.md` - root-change variant that needs the same baseline contract.
- `tests/test_change_service.py` - primary regression coverage for change creation behavior and template output.
- `.sspec/spec-docs/change-lifecycle.md` - documents the on-disk creation contract for change directories.

### Decisions (Timestamped)
- [2026-03-07T01:50] **Decision** - Store the git origin snapshot in `handover.md`, not `spec.md`.
  **Why**: The snapshot is stable execution context for future Agents, while `spec.md` should stay focused on problem/solution design.
- [2026-03-07T01:52] **Decision** - Do not update AGENTS.md or SKILLs for this change.
  **Why**: The existing protocol already instructs agents to resume from `handover.md`, so the new baseline becomes visible without extra workflow rules.

### Notes (Timestamped)
- [2026-03-07T01:50] Git state must be captured before creating the change directory; otherwise the new `.sspec/changes/<dir>/` files will dirty the repository and corrupt the baseline.
- [2026-03-07T01:50] Dirty worktrees should be recorded verbatim rather than rejected; staged/modified/untracked entries are part of the change starting point.
- [2026-03-07T02:11] Manual sandbox verification in `tmp/test_record_git_id_cli/` confirmed a fresh `sspec change new` writes the git baseline section with the pre-creation clean status block.
- [2026-03-07T02:18] Review feedback showed the raw status block needed clearer labeling; the final format now keeps the raw `git status --short --branch` output but removes the extra HEAD subject line.
- [2026-03-07T15:42] Follow-up guidance now lives in the skill templates too: handover treats the baseline as immutable, and review uses it as the anchor for deeper `git diff` / `git log` comparison.

## Session Log (Append-Only)
<!-- Newest entry first. Each entry is an atomic batch (one cohesive work record).

Header format:
### 2026-03-06T20:39 [work-log] <short title>

Tags are freeform but must be readable. Examples: work-log, user-feedback, argue, risk.
Any user interaction (feedback, @align, @argue) MUST start a new log entry. -->

### 2026-03-07T15:42 [user-feedback] Add skill guidance for git baseline usage

**Accomplished**
- Updated the handover skill template to explicitly say `Git Baseline (Immutable)` must not be rewritten during later handovers.
- Updated the review skill template to tell agents to use the recorded baseline as the anchor for `git diff` / `git log` comparisons.
- Reinstalled the package, synced self-hosted skills, and verified the new wording via a fresh sandbox init.

**Next**
- Commit the finished change set.

### 2026-03-07T02:19 [user-feedback] Final format approved

**Accomplished**
- User approved the clarified git baseline format.
- Change status can now move from `REVIEW` to `DONE`.

**Next**
- Archive the change when convenient, or keep it as a recent reference until the next cleanup pass.

### 2026-03-07T02:18 [user-feedback] Simplify git baseline wording

**Accomplished**
- User asked what the raw code block represented and whether the `Subject` line was necessary.
- Simplified the output by removing `Subject` and adding an explicit `Status Snapshot` label above the raw `git status --short --branch` block.

**Next**
- Ask the user to review the clarified output format.

### 2026-03-07T02:11 [work-log] Implementation and verification complete

**Accomplished**
- Implemented pre-creation git snapshot capture in `src/sspec/services/change_service.py` and injected it into template rendering via `{{GIT}}`.
- Added immutable git baseline sections to both handover templates and documented the contract in `.sspec/spec-docs/change-lifecycle.md`.
- Added regression coverage, ran install/lint/format/tests, and verified generated output in `tmp/test_record_git_id_cli/`.

**Next**
- Ask the user to review the implementation and confirm whether any wording/content in the git baseline should change.

### 2026-03-07T01:52 [user-feedback] Design approved with protocol follow-up

**Accomplished**
- User approved the handover-based git baseline direction.
- Confirmed that AGENTS/SKILL updates are unnecessary because resume flow already prioritizes `handover.md`.

**Next**
- Implement the service, template, test, and spec-doc changes.
- Run verification and return for implementation review.

### 2026-03-07T01:50 [work-log] Research and draft design

**Accomplished**
- Read the request, project context, change lifecycle docs, and relevant change/request services.
- Created change `26-03-07T01-48_record-git-id` from the request file.
- Drafted `spec.md` and `tasks.md` with the current recommendation: capture pre-creation git state into an immutable handover section.

**Next**
- Align with the user on the placement/content of the git baseline.
- After approval, implement service/template/test/spec-doc updates and run the required sync + verification flow.

**Notes** (optional)
- Current design intentionally treats “not a git repo” as a non-fatal fallback so `sspec change new` keeps working for non-git projects.
