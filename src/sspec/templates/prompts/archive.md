# /archive

Archive a completed change.

## Arguments

`/archive <change-name>` or `/archive` to select interactively.

## Task

1. **Verify** the change is ready:
   - Status should be `DONE` or `REVIEW`
   - All tasks completed
   - No unresolved blockers
   
2. **Update** final state:
   - Ensure `tasks.md` reflects reality
   - Update `handover.md` with final summary
   
3. **Archive**:
   ```bash
   sspec archive <n> --yes
   ```

4. **Confirm** archive location and update global `handover.md` if needed

## Pre-Archive Checklist

- [ ] All planned tasks completed or explicitly deferred
- [ ] No open blockers
- [ ] Handover document updated
- [ ] Any learnings captured in `knowledge/` if relevant
