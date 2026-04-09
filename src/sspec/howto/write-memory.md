---
name: write-memory
desc: How to write and maintain memory.md — the change-scoped memory store.
---

memory.md captures information that doesn't belong in spec/design/tasks/revisions but is essential for continuity. It is NOT a handover document — it's a living memory that agents maintain throughout the change lifecycle.

## Sections

### State
One to three lines: where are we, what's next. First thing the next agent reads.
```
Implementing Phase 3 task 2. Next: create `services/cache.py` per spec.
```

### Key Files
Files critical to this change, NOT already in spec Scope Summary.
```
- `src/services/auth.py` — core auth logic being refactored
- `tests/test_auth.py` — regression tests, must pass before merge
```

### Knowledge
Facts that would cause wrong decisions if lost. NOT duplicates of spec/design/tasks.

Types: `Decision`, `Constraint`, `Gotcha`, `Rejected`, `VitalFinding` etc. Use a custom type only when the recommended labels are not clear enough.
```
- [2026-04-09T02:00] [Rejected] Considered "Understand" — too passive
- [2026-04-09T02:30] [Gotcha] sspec-align §1 had proto-Clarify content
```

Rules:
- Project-level discoveries → ALSO append to project.md Notes
- Obsolete items → mark with timestamp, don't silently delete

### Milestones
One line per session. Pure facts.
```
- [2026-04-09T01:00] Clarify: Research→Clarify rename decided
- [2026-04-09T02:15] Design+Implement: rename complete
```

### Coordination (Root Only)
Sub-change status table. MUST update when status changes.

## Quality Check

- New agent reads State → knows what to do in <10s?
- Knowledge contains ONLY items NOT in spec/design/tasks?
- No redundancy with Scope Summary in Key Files?
- Milestones has an entry for this session?

## Anti-Patterns

| Bad | Good |
|-----|------|
| Repeat spec Problem Statement | Reference: "see spec.md" |
| Detailed session narrative | One-line Milestone |
| Skip memory at session end | MUST write State + Milestones |
| Transient progress in Knowledge | Knowledge = durable cross-session facts only |
