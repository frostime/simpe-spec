---
name: sspec-memory
description: "Maintain change-scoped memory (memory.md). Update State/Knowledge/Milestones at session end and @align gates."
metadata:
  author: frostime
  version: 5.0.0
---

# SSPEC Memory

memory.md is a **scoped memory store**, not a handover document. It captures information that doesn't belong in spec/design/tasks/revisions but is essential for continuity.

---

## When to Update

| Trigger | What to write | Required? |
|---------|--------------|-----------|
| Session ending | State + Milestones | MUST |
| @align gate (if Knowledge changed) | Knowledge entries | SHOULD |
| Sub-change status change (root only) | Coordination table | MUST |

**Timestamp rule**: ISO timestamps with minute precision. If uncertain, use `sspec tool now`.

## What to Write

### State

One to three lines: where are we, what's next. This is the first thing the next agent reads.

```markdown
## State
Implementing Phase 3 task 2. Next: create `services/cache.py` per spec.
```

### Key Files

Files critical to understanding or continuing this change. Only list files NOT already in Scope Summary.

```markdown
## Key Files
- `src/services/auth.py` — core auth logic being refactored
- `tests/test_auth.py` — regression tests, must pass before merge
```

### Knowledge

Facts that don't belong in spec/design/tasks/revisions. The test: "Would losing this information cause the next agent to make a wrong decision?"

Types: `Decision`, `Constraint`, `Gotcha`, `Rejected`

```markdown
## Knowledge
- [2026-04-09T02:00] [Rejected] Considered renaming to "Understand" — too passive, doesn't imply action
- [2026-04-09T02:30] [Gotcha] sspec-align §1 had proto-Clarify content — moved to sspec-clarify
- [2026-04-09T03:00] [Decision] memory.md replaces handover.md — scoped memory framing
```

**Rules**:
- Project-level discoveries → ALSO append to project.md Notes
- Obsolete items → mark with timestamp, don't silently delete
- If it belongs in spec/design/tasks → put it there, not here

### Milestones

One line per session. Pure facts, no elaboration.

```markdown
## Milestones
- [2026-04-09T01:00] Clarify: Research→Clarify rename decided after 6-framework survey
- [2026-04-09T02:15] Design+Implement: rename complete, align refactored to v12
```

### Coordination (Root Only)

The primary coordination memory for root changes. MUST update when sub-change status changes.

```markdown
## Coordination
| Phase | Sub-Change | Status | Blocker |
|-------|------------|--------|---------|
| Phase 1 | `changes/26-04-09_auth/` | DOING | — |
| Phase 2 | `changes/26-04-09_cache/` | ⏳ | Depends on Phase 1 API |
```

## Quality Check

| Test | Pass? |
|------|-------|
| New agent reads State — knows what to do next in <10s? | |
| Knowledge only contains items NOT in spec/design/tasks? | |
| No redundancy with Scope Summary in Key Files? | |
| Milestones has an entry for this session? | |

## Anti-Patterns

| Bad | Good |
|-----|------|
| Repeat spec Problem Statement in Knowledge | Reference: "see spec.md" |
| Detailed session narrative | One-line Milestone |
| Skip memory at session end | MUST write State + Milestones |
| Store transient progress in Knowledge | Knowledge = durable cross-session facts only |
