# sspec/archive

Archive a completed change.

## Arguments

`sspec/archive <change-name>` or `sspec/archive` to select interactively.

## Prerequisites

Before archiving, verify:
- [ ] Status is `DONE` or `REVIEW`
- [ ] All planned tasks completed (or explicitly marked as deferred)
- [ ] No unresolved blockers
- [ ] Success criteria from proposal met

## Workflow

1. **Verify** the change is ready
   ```bash
   sspec status <n>
   ```
   - Check status and progress
   - Review any remaining tasks

2. **Update** final state
   - Ensure `tasks.md` reflects reality
   - Update `handover.md` with final summary
   - Note any learnings or follow-up work needed

3. **Consider knowledge transfer**
   - Any discoveries worth adding to `knowledge/`?
   - Any patterns that should be documented?
   - Any gotchas future work should know about?

4. **Archive** the change
   ```bash
   sspec archive <n> --yes
   ```

5. **Update** global state if needed
   - Update `.sspec/handover.md` with completion note
   - Note any follow-up work in new change or backlog

## Output

```
Archived: <change-name>
Location: .sspec/changes/archive/YYYY-MM-DD_<name>/

Summary:
- [X] tasks completed
- Duration: [start to end]
- Key outcome: [one line]

Follow-up needed: None / [describe]
```

## If Not Ready

If prerequisites aren't met:
```
Cannot archive: <change-name>

Issues:
- [ ] [specific issue 1]
- [ ] [specific issue 2]

Resolve these first, then run sspec/archive again.
```

## Anti-patterns

❌ Archiving with unfinished tasks without explicitly deferring them
❌ Archiving without updating handover
❌ Losing learnings that should go to knowledge/
