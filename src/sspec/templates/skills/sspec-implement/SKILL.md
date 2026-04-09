---
name: sspec-implement
description: "Execute tasks from tasks.md. Implement code changes, update progress. Use after plan approval."
metadata:
  author: frostime
  version: 3.0.0
---

# SSPEC Implement

Execute the approved plan. Work through tasks.md systematically.

---

## Core Rules

- **Implement → verify → mark done** for each task
- **Update progress after EACH task** — do not batch
- Only modify files relevant to the current task
- Preserve existing code style, comments, and structure
- MUST NOT refactor unrelated code

## When to Pause

| Situation | Action |
|-----------|--------|
| Task is ambiguous | `@align` for clarification |
| Implementation reveals design issue | Re-enter Clarify posture to understand the gap; create `revisions/NNN-*.md` if spec/design already gated, then update tasks.md; `@align` if scope changes |
| Blocker encountered | Record in `memory.md`, `@align` user |
| Multiple valid approaches | Pick the simpler one, note in memory |
| Design assumption was wrong | Re-enter Clarify posture: "Design says X but I found Y" → re-sync with user before revising |

**Do not guess on blockers.** One `@align` < one rework cycle.

## Keep Changes Focused

- If a task grows but still belongs to the current change → split it, add new tasks to tasks.md
- If the work now belongs in a follow-up or replacement change → `@align` user before creating a new change

## Memory During Implementation

For long sessions (>30 exchanges or multi-file work):
- Promote durable decisions / constraints to `memory.md` Knowledge
- Record session facts and checkpoints in `memory.md` Milestones
- Update Key Files as you discover important files

**Test**: "Would I struggle to continue if context was compressed right now?" → Write to memory.

## Exit: @align User

When all tasks are complete:

1. Update Progress to 100%
2. Summarize what was implemented
3. `@align` user: "Implementation complete. Please review."

This is a **hard gate**. → Transition to `sspec-review` phase.

→ Status transitions: `sspec howto update-change-status`
