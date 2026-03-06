# Handover: refresh-spec-docs

**Updated**: 2026-03-07T00:53

---

## Background
<!-- Write once on first session. What this change does and why (1-3 sentences).
Update only if scope fundamentally changes. Details belong in spec.md. -->

Refresh the current self-hosted documentation set under `.sspec/`.
This change fixes factual drift in `.sspec/project.md` and existing spec-docs, then adds missing long-lived docs for stable workflow and on-disk contracts.

## Working Memory (Stable)
<!-- Curated, long-lived context. Survives context compression and session boundaries.
If something becomes obsolete, mark it as obsolete with a timestamp instead of deleting silently. -->

### Key Files
<!-- Files critical to understanding/continuing this change.
- `path/file` - what it contains, why it matters -->

- `.sspec/changes/26-03-06T23-39_refresh-spec-docs/spec.md` - design scope, proposed docs, and file-level documentation targets
- `.sspec/changes/26-03-06T23-39_refresh-spec-docs/tasks.md` - phased execution plan for the documentation refresh
- `.sspec/changes/26-03-06T23-39_refresh-spec-docs/reference/doc-audit.md` - initial audit of stale facts and missing contract coverage
- `.sspec/project.md` - stable project identity doc to be corrected in this change
- `.sspec/spec-docs/README.md` - spec-doc entry index that must be expanded alongside new docs
- `.sspec/spec-docs/change-lifecycle.md` - new long-lived contract for `.sspec/changes/` structure, status, and archive rules
- `.sspec/spec-docs/interaction-records.md` - new long-lived contract for request/ask records and archive rewrites
- `.sspec/spec-docs/cmd-registry.md` - new contract for `.sspec/commands/registry.yaml` and script strategies
- `.sspec/spec-docs/agents-sync.md` - new contract for root `AGENTS.md` managed block behavior

### Decisions (Timestamped)
<!-- Timestamp every entry (minute precision).
- [2026-03-06T20:39] **Decision** - Redis over Memcached
  **Why**: Need per-key TTL + persistence -->

- [2026-03-06T23:40] **Decision** - Treat the documentation refresh as a single change.
  **Why**: The work stays within roughly 9 `.sspec` docs, is tightly cross-linked, and benefits from one coordinated design/plan instead of a root change.
- [2026-03-06T23:40] **Decision** - Scope this change to current self-hosted `.sspec` docs, not template sources.
  **Why**: The user explicitly requested updates to `.sspec/project.md` and `.sspec/spec-docs/`, and the confirmed drift is in the live repo docs.
- [2026-03-07T00:15] **Decision** - Close the implementation phase in one batch and hand the change to review.
  **Why**: Existing-doc drift, new spec-doc creation, and reindexing are all complete and have already been cross-checked against the current code paths.

### Notes (Timestamped)
<!-- Gotchas, edge cases, risks, verification shortcuts. Timestamp every entry.
Project-wide items -> ALSO append to project.md Notes. -->

- [2026-03-06T23:40] Existing drift already confirmed in `skill-installation.md`, `builtin-tools.md`, and `testing-standards.md`; fix stale facts before adding any new spec-doc.
- [2026-03-06T23:40] New spec-docs should follow `write-spec-doc` frontmatter rules and list concrete runtime code paths in `scope`.
- [2026-03-07T00:15] Verification for this change is documentation-focused: `sspec tool mdtoc .sspec/spec-docs`, targeted greps for stale terms, and code/doc cross-checks; no runtime tests were needed because no code changed.

## Session Log (Append-Only)
<!-- Newest entry first. Each entry is an atomic batch (one cohesive work record).

Header format:
### 2026-03-06T20:39 [work-log] <short title>

Tags are freeform but must be readable. Examples: work-log, user-feedback, argue, risk.
Any user interaction (feedback, @align, @argue) MUST start a new log entry. -->

### 2026-03-07T00:53 [user-feedback] review accepted and finalize change

**Accomplished**
- User accepted the documentation update batch as-is.
- Change status can be finalized from `REVIEW` to `DONE`.
- Next action is to create the requested git commit.

**Next**
- Commit the `.sspec` documentation updates.
- No further documentation edits are pending unless new feedback arrives.

**Notes** (optional)
- This change completed without runtime code changes; verification remained documentation-only.

### 2026-03-07T00:15 [work-log] completed spec-doc refresh implementation

**Accomplished**
- Refreshed `.sspec/project.md`, `.sspec/spec-docs/README.md`, `skill-installation.md`, `builtin-tools.md`, and `testing-standards.md` to match current code.
- Added new spec-docs: `change-lifecycle.md`, `interaction-records.md`, `cmd-registry.md`, and `agents-sync.md`.
- Reindexed the spec-doc set and ran consistency checks with `mdtoc`, grep, and code/doc spot verification.

**Next**
- Ask the user to review the documentation update batch.
- If feedback arrives, add review tasks under `Feedback Tasks` and return to DOING.

**Notes** (optional)
- Change is now in `REVIEW`; all planned tasks are complete.

### 2026-03-06T23:49 [user-feedback] approved current doc refresh scope

**Accomplished**
- Presented the proposed doc refresh scope and task breakdown for alignment.
- User approved the recommended scope: repair existing docs and add 4 new contract spec-docs.
- Change status now moves from `PLANNING` to `DOING`.

**Next**
- Implement Phase 1 updates in `.sspec/project.md` and the existing drifted spec-docs.
- Keep `tasks.md` and `handover.md` updated as implementation progresses.

**Notes** (optional)
- Approved new docs: `change-lifecycle.md`, `interaction-records.md`, `cmd-registry.md`, `agents-sync.md`.

### 2026-03-06T23:40 [work-log] created change and drafted doc refresh plan

**Accomplished**
- Created change `.sspec/changes/26-03-06T23-39_refresh-spec-docs/`.
- Audited current `.sspec/project.md` and `.sspec/spec-docs/` against live code paths.
- Drafted `spec.md`, `tasks.md`, and `reference/doc-audit.md` for the documentation refresh transaction.

**Next**
- Align with the user on the proposed documentation scope and planned new spec-docs.
- After approval, implement the doc updates in phase order and keep handover/tasks in sync.

**Notes** (optional)
- Expected new docs: `change-lifecycle.md`, `interaction-records.md`, `cmd-registry.md`, `agents-sync.md`.
