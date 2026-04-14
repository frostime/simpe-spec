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
| Implementation reveals design issue | See **Post-Gate Design Changes** below |
| Blocker encountered | Record in `memory.md`, `@align` user |
| Multiple valid approaches | Pick the simpler one, note in memory |
| Design assumption was wrong | Re-enter Clarify posture: "Design says X but I found Y" → re-sync with user before revising |

**Do not guess on blockers.** One `@align` < one rework cycle.

### Post-Gate Design Changes

Apply this test first:
> Can the original spec/design still accurately predict the post-change code?
> **YES** → note in memory, continue | **NO** → revision required

If revision required:

1. **Stop** — do not implement the deviation silently
2. `@align` user: explain the gap, get confirmation
3. `sspec change scaffold revision <change> --title "..."` — create revision file
4. Fill revision: Reason / Spec Impact / Design Impact / Task Impact
5. Update `tasks.md` to reflect new work
6. Resume implementation

This applies whether the issue was triggered by a user comment or self-discovered.

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
