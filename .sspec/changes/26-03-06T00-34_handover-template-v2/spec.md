---
name: handover-template-v2
status: DONE
type: ""
change-type: single
created: 2026-03-06T00:34:26
reference: null
---

<!-- @RULE: Frontmatter
status: PLANNING | DOING | REVIEW | DONE | BLOCKED
change-type: single | sub
reference?: Array<{source, type: 'request'|'root-change'|'sub-change'|'prev-change' |'doc', note?}>

Sub-change MUST link root:
reference:
  - source: ".sspec/changes/<root-change-dir>"
    type: "root-change"
    note: "Phase <n>: <phase-name>"

Single-change common reference:
reference:
  - source: ".sspec/requests/<request-file>.md"
    type: "request"
  - source: ".sspec/changes/<change-dir>"
    type: "prev-change"
    note: "This change is a follow-up to <change-name> which introduced <feature/bug>. This change addresses <issue> with that feature/bug."
-->

# handover-template-v2

## A. Problem Statement
handover.md is the change's "external memory" and is supposed to enable a <30s resume.
In practice, archived changes show handover content drifting into inconsistent structures
and mixing two kinds of information:

1) Stable knowledge (key files, decisions, constraints) that stays useful across sessions
2) Volatile state (what happened this session, next steps, current blockers) that becomes stale fast

When these are mixed, the "current next action" is hard to locate and older "next steps"
silently expire, making resume slower and more error-prone.

User feedback: handover entries often look "messy" and are hard to track across sessions.

Goal: make handover predictable and traceable across sessions by separating stable vs volatile,
and by making session progress append-only.

<!-- @RULE: Quantify impact. Format: "[metric] causing [impact]".
Simple: single paragraph. Complex: split "Current Situation" + "User Requirement". -->

## B. Proposed Solution
### Approach

Make handover predictable and trackable by separating:

- Stable context: key files, decisions, constraints (curated, long-lived)
- Volatile progress: what happened + what to do next (append-only, timestamped)

The key change is to remove the overwrite-prone "This Session" block and make a
"Session Log" the single source of truth for current state.

Design constraints from user feedback:
- Avoid duplicated "current state" summaries that can drift out of sync
- Every new Decision/Note entry must carry a timestamp
- Session Log entries must be "atomic batches" (highly cohesive work records)
- Any user interaction (review feedback, @ask, @argue) must start a new log entry

### Key Design

**Feat A: Session Log as source of truth**

New handover structure for single/sub changes:

```markdown
# Handover: {{CHANGE_NAME}}

**Updated**: <!-- set to ISO timestamp (minute precision) at session end, e.g. 2026-03-06T20:39 -->

---

## Background
<!-- Stable. Write once (edit only if scope changes). 1-3 sentences. -->

## Working Memory (Stable)
<!-- Curated. If something becomes obsolete, mark it as obsolete with a date. -->

### Key Files
- `path/file` - what it contains, why it matters

### Decisions (timestamped)
- [2026-03-06T20:39] **Decision** - <what>
  **Why**: <reason>

### Notes (timestamped)
- 2026-03-06T20:39: <gotcha / risk / verification shortcut>

## Session Log (Append-Only)
<!-- Newest entry first. Each entry is an atomic batch. -->

### <ISO timestamp> [tag] <short title>
<!-- tag examples: work-log | user-feedback | argue | coordination | risk -->

**Accomplished**
- ...

**Next**
- ...

**Notes** (optional)
- ...
```

Rules:
- Newest log entry first. Reading the top entry must be enough to resume.
- Each entry MUST include both **Accomplished** and **Next**.
- Keep each entry cohesive (one topic). If you change topic, start a new entry.
- For any user interaction (feedback, @ask, @argue), start a new entry with a clear tag.
- Use timestamps with at least minute precision everywhere they appear.

**Feat B: Root change snapshot + coordination logs**

Root change handover keeps a volatile snapshot table for coordination, plus the same
append-only Session Log for history:

```markdown
## Sub-Change Status (Volatile Snapshot)
<!-- Update when coordination state changes. -->
| Phase | Sub-Change | Status | Notes |
|-------|------------|--------|------|
| Phase 1 | `changes/<sub>/` | DOING | ... |
```

**Refactor C: Align sspec-handover (and minimal AGENTS note) with the new template**

Update `sspec-handover` to enforce:
- Append one atomic Session Log entry (or more if multiple user interactions happened)
- Ensure the top log entry contains the real next action
- Keep Working Memory curated and timestamp new Decisions/Notes

Optionally add a short note in `AGENTS.md` reminding agents that Session Log is the
resume entry point.

### Scope Summary
| File | Change |
|------|--------|
| `src/sspec/templates/change/handover.md` | Replace "This Session" with append-only Session Log + timestamped memory |
| `src/sspec/templates/change-root/handover.md` | Same + add/clarify volatile sub-change snapshot table |
| `src/sspec/templates/skills/sspec-handover/SKILL.md` | Update procedure + quality checks for atomic logs + timestamps |
| `src/sspec/templates/AGENTS.md` | (Optional) Add a short note pointing to Session Log resume pattern |
