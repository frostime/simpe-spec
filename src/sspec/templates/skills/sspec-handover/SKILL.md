---
name: sspec-handover
description: "Save session state. Update handover.md, project.md, and spec-docs index. MANDATORY at session end, recommended mid-session."
metadata:
  author: frostime
  version: 3.3.0
---

# SSPEC Handover

Persist session knowledge so any agent can resume within 30 seconds.

**Handover is a lifecycle participant, not just cleanup.** It preserves context across sessions, context compressions, and agent switches.

---

## When to Trigger

### End of Session (MANDATORY)

Before ending ANY session, perform the full procedure below. No exceptions.

### Mid-Session (Proactive)

Update handover.md when:
- Session is long (>30 exchanges or complex multi-file work)
- Important decision just made with non-trivial reasoning
- Key file discovered that future work depends on
- Design tradeoff resolved after discussion
- Any user interaction that changes direction (feedback, @align gate, @argue)
- About to switch between major phases (e.g. design -> plan)

**Rule**: If you'd struggle to reconstruct info after context compression → write it NOW.

## Procedure

### 1. Update handover.md

handover.md is the resume entry point.

**Timestamp rule**: Use ISO timestamps with at least minute precision (example: `2026-03-06T20:39`). If current time is uncertain, use `sspec tool now` instead of guessing.

**Updated field**: Set `**Updated**:` to the current timestamp (should match your newest Session Log entry).

**Session Log (Append-Only)**:
- Add a new Session Log entry (newest-first)
- Each entry is an atomic batch (one cohesive work record)
- Each entry MUST include both **Accomplished** and **Next**
- Any user interaction (feedback, @align gate, @argue) MUST start a new log entry with a clear tag (for example: `user-feedback`, `argue`)
- Need concrete log-writing rules? → `sspec howto write-handover-log`

**Working Memory (Stable)**:
- **Key Files**: List critical file paths with a 1-line why
- **Durable Memory**: Use typed entries in the form `[YYYY-MM-DDTHH:MM] [Type] <content>`
- For single/sub changes, prefer: `Alignment`, `Decision`, `VitalFinding`, `Constraint`, `Risk`, `VerificationShortcut`
- For root changes, prefer: `Alignment`, `CoordinationDecision`, `Dependency`, `CrossChangeFinding`, `Constraint`, `Risk`, `VerificationShortcut`
- Use a custom type only when none of the canonical types fit; keep custom labels short and rare
- Promote only facts still useful after the current batch ends; keep batch-local progress, review outcomes, and reminders in `Session Log`
- If something becomes obsolete, default to marking it obsolete with a timestamp; delete only pure noise or obvious duplicates with no lasting value
- If handover has a `Git Baseline (Immutable)` section, treat it as **read-only** origin context from change creation; do not refresh, rewrite, or "fix" it during later handovers
- Need durable-memory type choice or examples? → `sspec howto write-handover-memory`
- Need obsolete-memory cleanup rules? → `sspec howto handle-obsolete-memory`

**Root change only**:
- Update `Sub-Change Status (Volatile Snapshot)` when coordination state changes
- Record durable coordination knowledge with root-oriented types such as `CoordinationDecision`, `Dependency`, or `CrossChangeFinding`
- Quick chooser: `CoordinationDecision` = durable orchestration choice, `Dependency` = ordering/coupling rule, `CrossChangeFinding` = one finding that matters to multiple sub-changes

### 2. Sync tasks.md

Verify tasks.md progress percentage matches reality. All completed tasks marked `[x]`.

### 3. Promote to project.md (if applicable)

Two promotion targets:

**Notes section**: If any discovery applies beyond this change → append with date.
- Format: `- YYYY-MM-DD: <learning>` (project-level notes can stay date-only)

**Spec-Docs Index section**: If spec-docs were created or updated during this session → update the index.
- Format: `- [name](spec-docs/<file>) — one-line description`

### 4. Suggest spec-doc update (if applicable)

If the change produced architectural knowledge (new interfaces, data models, patterns):
- `@align` user: "This change produced knowledge about X. Should I create/update a spec-doc?"
- If yes → use `write-spec-doc` SKILL

### 5. Quick Quality Check

| Test | Pass? |
|------|-------|
| New agent reads only handover.md — can resume in <30s? | |
| If context compressed right now — could you continue from handover.md alone? | |
| For each durable cross-session fact — can you find it in typed Durable Memory? | |
| Newest Session Log entry includes the real Next action (and is a single atomic batch)? | |
| New Durable Memory entries are typed and timestamped (minute precision)? | |

If any test fails → update handover before ending.

## handover.md Quality

**Thin** (simple change, ≤5 files): 3-5 bullet points across Working Memory sections.
**Rich** (complex change, many decisions): Numbered items with sub-structure, evidence, tradeoff analysis.

Use the template structure. Keep Durable Memory compact and keep Session Log entries short and cohesive.

### Anti-Patterns

| Bad | Good |
|-----|------|
| Skip handover at session end | ALWAYS handover — no exceptions |
| Only update at session end | Update Working Memory DURING work |
| Promote batch-local status into Durable Memory | Keep transient progress, review outcomes, and reminders in Session Log |
| No file paths in Key Files | List files you'd need to re-find after compression |
| Put architecture docs in project.md | project.md ≤10s scan; use spec-docs for detailed content |
| Split one durable fact across multiple memory buckets | Use one typed Durable Memory section and choose the clearest type |
| Mix unrelated work in one Session Log entry | Keep each entry as one cohesive atomic batch |
| User feedback not recorded as its own entry | New log entry with `user-feedback` / `argue` tag |
