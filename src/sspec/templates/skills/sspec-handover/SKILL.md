---
name: sspec-handover
description: "Save session state. Update handover.md, project.md, and spec-docs index. REQUIRED at session end, recommended mid-session."
metadata:
  author: frostime
  version: 4.0.0
---

# SSPEC Handover

Persist session knowledge so any agent can resume within 30 seconds.

**Handover is a lifecycle participant, not just cleanup.** It preserves context across sessions, context compressions, and agent switches.

---

## When to Trigger

### End of Session (Required)

Before ending any session, the agent MUST perform the full procedure below.

### Mid-Session (Proactive)

Update handover.md when:
- Session is long (>30 exchanges or complex multi-file work)
- Important decision just made with non-trivial reasoning
- Key file discovered that future work depends on
- Design tradeoff resolved after discussion
- Any user interaction that changes direction (feedback, @align gate, @argue)
- About to switch between major phases (e.g. design → plan)

**Rule**: If you'd struggle to reconstruct info after context compression, you MUST write it now.

## Procedure

### 1. Update handover.md

handover.md is the resume entry point. **Preserve causal and temporal relationships** — the reader must understand not just the current state, but how and why we got here.

**Timestamp rule**: ISO timestamps with minute precision. If uncertain, use `sspec tool now`.

**Session Log (Append-Only)**:
- Add a new entry (newest-first). Each entry = one atomic work batch.
- Each entry MUST include both **Accomplished** and **Next**
- User interactions (feedback, @align, @argue) MUST start a new entry
- → `sspec howto write-handover-log`

**Working Memory (Stable)**:
- **Key Files**: critical file paths with a 1-line why
- **Durable Memory**: typed, timestamped facts that survive sessions
- Prefer types: `Alignment`, `Decision`, `VitalFinding`, `Constraint`, `Risk`, `VerificationShortcut` (single/sub) or `CoordinationDecision`, `Dependency`, `CrossChangeFinding` (root)
- → `sspec howto write-handover-memory`

**Git Baseline (Immutable)**: MUST NOT be edited during later handovers — read-only origin snapshot.

### 2. Sync tasks.md

Verify progress percentage matches reality. All completed tasks MUST be marked `[x]`.

### 3. Promote to project.md (if applicable)

- **Notes section**: project-wide discovery → append with date
- **Spec-Docs Index**: if spec-docs were created/updated → update index

### 4. Suggest spec-doc update (if applicable)

If the change produced architectural knowledge → `@align` user: "Should I create/update a spec-doc?" → `write-spec-doc` SKILL

### 5. Quality Check

| Test | Pass? |
|------|-------|
| New agent reads only handover.md — can resume in <30s? | |
| If context compressed now — could you continue from handover.md alone? | |
| For each durable cross-session fact — is it in Durable Memory? | |
| Newest Session Log has a concrete **Next** action? | |
| Durable Memory entries are typed and timestamped? | |

If any test fails → update handover before ending.

## Anti-Patterns

| Bad | Good |
|-----|------|
| Skip handover at session end | Handover MUST happen at session end |
| Only update at session end | Update Working Memory DURING work |
| Promote batch-local status into Durable Memory | Keep transient progress in Session Log |
| No file paths in Key Files | List files you'd need to re-find after compression |
| Mix unrelated work in one Session Log entry | One entry = one atomic batch |
| User feedback not recorded as its own entry | New log entry with `user-feedback` / `argue` tag |
