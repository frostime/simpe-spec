# Handover: local-change-status-strategy

**Updated**: 2026-03-06T14:11

---

## Background
<!-- Write once on first session. What this change does and why (1-3 sentences).
Update only if scope fundamentally changes. Details belong in spec.md. -->

Evaluate whether sspec should add a richer local `change status` view, and define a design
that fits sspec's doc-driven, change-local philosophy without adopting openspec-style global schema control.

## Working Memory (Stable)
<!-- Curated, long-lived context. Survives context compression and session boundaries.
If something becomes obsolete, mark it as obsolete with a timestamp instead of deleting silently. -->

### Key Files
<!-- Files critical to understanding/continuing this change.
- `path/file` - what it contains, why it matters -->

- `src/sspec/commands/change.py` - current `find` command, commented `status` skeleton, and existing detail helper
- `src/sspec/services/change_service.py` - current change parsing logic (frontmatter + tasks checkbox counts)
- `src/sspec/templates/change-root/handover.md` - root snapshot heading/template anchor used by status parsing
- `src/sspec/templates/AGENTS.md` - lightweight quick-dashboard usage hint
- `wip/analysis-report.md` - source report proposing `status --json` and `.state.yaml`
- `.sspec/changes/26-03-06T13-27_local-change-status-strategy/reference/status-research.md` - option comparison and recommendation
- `.sspec/changes/26-03-06T13-27_local-change-status-strategy/spec.md` - proposed direction for local dashboard status

### Decisions (Timestamped)
<!-- Timestamp every entry (minute precision).
- [2026-03-06T20:39] **Decision** - Redis over Memcached
  **Why**: Need per-key TTL + persistence -->

- [2026-03-06T13:36] **Decision** - Recommend a human-readable local `change status` before any JSON/status-cache work.
  **Why**: It matches sspec's current scale and philosophy: documents remain source of truth, CLI is only a read-only projection.
- [2026-03-06T13:36] **Decision** - Reject openspec-style global workflow/schema control for this problem.
  **Why**: It would move the system's center of gravity away from the local change directory and toward a central controller.
- [2026-03-06T13:39] **Decision** - Status output should include relative source-file links and only light protocol nudges.
  **Why**: The summary should invite agents back to original files for detail, without bloating AGENTS/SKILL instructions.
- [2026-03-06T14:07] **Decision** - Ignore commented template examples when extracting the latest Session Log.
  **Why**: Fresh handover templates contain example headings inside comments; status must not mistake them for real progress.

### Notes (Timestamped)
<!-- Gotchas, edge cases, risks, verification shortcuts. Timestamp every entry.
Project-wide items -> ALSO append to project.md Notes. -->

- 2026-03-06T13:36: `sspec change status` is not publicly available right now, but `_show_change_detail()` still exists and one help string still references the missing command.
- 2026-03-06T13:36: `find` and `status` are not duplicates if roles stay separate: `find` answers where, `status` answers what now.
- 2026-03-06T13:36: Markdown parsing risk is manageable if extraction is limited to frontmatter, checkbox counts, fixed headings, and the newest Session Log block.

## Session Log (Append-Only)
<!-- Newest entry first. Each entry is an atomic batch (one cohesive work record).

Header format:
### 2026-03-06T20:39 [work-log] <short title>

Tags are freeform but must be readable. Examples: work-log, user-feedback, argue, risk.
Any user interaction (feedback, @ask, @argue) MUST start a new log entry. -->

### 2026-03-06T14:07 [work-log] implement and validate local change status

**Accomplished**
- Added status summary types in `src/sspec/core.py` and bounded extraction helpers in `src/sspec/services/change_service.py`.
- Restored `sspec change status <name>` in `src/sspec/commands/change.py` as a local dashboard with source links and latest Session Log summary.
- Fixed task progress extraction to ignore checkbox examples inside HTML comments, so dashboard counts reflect real tasks.
- Added a short quick-dashboard hint in `src/sspec/templates/AGENTS.md`.
- Reintroduced the root `Sub-Change Status (Volatile Snapshot)` heading in `src/sspec/templates/change-root/handover.md` so the snapshot has a stable parse anchor.
- Reinstalled, linted, formatted, and smoke-tested status output in `tmp/test_change_status_dashboard`.

**Next**
- Ask the user to review the new `change status` behavior and confirm whether this direction feels right.

**Notes** (optional)
- Verified real change output (`local-change-status-strategy`) and fresh single/root changes in sandbox.

### 2026-03-06T14:11 [user-feedback] implementation accepted

**Accomplished**
- User reviewed the implementation and confirmed it is OK.
- Change status moved from `REVIEW` to `DONE`.

**Next**
- Archive the change when ready.
- Commit the implementation if the user wants to save it now.

**Notes** (optional)
- Current working tree still contains uncommitted changes for this feature.

### 2026-03-06T13:39 [user-feedback] refine status design after alignment

**Accomplished**
- Asked user to review the proposed local-dashboard direction.
- Got alignment with two adjustments: include source-file links in status output, and keep any AGENTS/SKILL note very short.
- Updated `spec.md`, `tasks.md`, and `reference/status-research.md` accordingly.

**Next**
- Wait for user to decide whether to stop at design or proceed into a follow-up implementation change.

**Notes** (optional)
- Added frontmatter references to `wip/analysis-report.md` and `.sspec/tmp/gpt对report的解释.md` so later agents understand the openspec / `--json` context.

### 2026-03-06T13:36 [work-log] research and design for local status strategy

**Accomplished**
- Created change `local-change-status-strategy`.
- Read current command/service code for `project status`, `change find`, and the commented `change status` skeleton.
- Compared options: no status, local human-readable status, JSON status, local `.state.yaml`, and openspec-style global schema.
- Wrote research notes and drafted a design recommendation in `spec.md`.

**Next**
- Ask the user whether this design direction is feasible before any implementation work.
- If approved, decide whether to start with a design-only doc update or directly implement a minimal `change status` command.

**Notes** (optional)
- Core recommendation: keep change-local truth in markdown docs, and treat any future CLI status as a bounded summary view rather than a controller API.
