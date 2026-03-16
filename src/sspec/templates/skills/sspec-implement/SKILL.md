---
name: sspec-implement
description: "Execute tasks from tasks.md. Implement code changes, update progress. Use after plan approval."
metadata:
  author: frostime
  version: 2.1.0
---

# SSPEC Implement

Execute the approved plan. Work through tasks.md systematically.

---

## Workflow

```
1. Read spec.md B (design context) + tasks.md (execution plan)
2. For each pending task: implement → verify → mark done
3. Update progress after EACH task
4. @align user when all tasks complete
```

## Execution Rules

### Task Loop

For each pending task:
1. Announce which task you're working on
2. Make the code changes
3. Verify the change works
4. Mark task complete: `- [ ]` → `- [x]`
5. Update Progress section
6. Continue to next task

**Update after EACH task** — not in batches.

### When to Pause

| Situation | Action |
|-----------|--------|
| Task is ambiguous | → `@align` for clarification |
| Implementation reveals design issue | → Sync `spec.md` / `tasks.md` before continuing; if the work no longer belongs to the current change, `@align` before split / replacement |
| Blocker encountered | → Record in `handover.md` Durable Memory / Session Log, `@align` user |
| Multiple valid approaches for a task | → Pick the simpler one, note in handover |
| Design assumption was wrong | → `@align` user: "Design says X but I found Y. Revise?" Update `spec.md` / `tasks.md` after the decision |

**Don't guess on blockers.** One `@align` < one rework cycle.

### Keep Changes Focused

- Only modify files relevant to the current task
- Preserve existing code style, comments, and structure
- Don't refactor unrelated code
- If a task grows but still belongs to the current change → split it, add new tasks to tasks.md
- If the work now belongs in a follow-up or replacement change → `@align` user before creating a new change or marking the current one `BLOCKED`

## Progress Updates

After completing each task, update the Progress section:

→ For the allowed status transitions: `sspec howto update-change-status`

```markdown
**Overall**: 40%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 100% | ✅ |
| Phase 2 | 25% | 🚧 |

**Recent**:
- Completed: Create auth middleware `src/middleware/auth.py`
- Completed: Add JWT validation `src/auth/jwt.py`
```

## Handover During Implementation

For long implementation sessions (>30 exchanges or multi-file work):
- Promote durable decisions / constraints to `handover.md` Working Memory → Durable Memory
- Record batch-local blockers, discoveries, or user feedback in `handover.md` Session Log
- Update Key Files as you discover important files

**Test**: "Would I struggle to continue if context was compressed right now?" → Write to handover.

## Exit: @align User (MANDATORY)

When all tasks are complete:

1. Update Progress to show 100%
2. Summarize what was implemented
3. `@align` user: "Implementation complete. Please review. Any issues or feedback?"

This is a hard gate. If a `question`-like tool is available, use it. Otherwise state the review request clearly in normal output and stop.

→ Transition to `sspec-review` phase.
