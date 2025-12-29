# sspec/status

Report current state summary.

## Arguments

`sspec/status` for overview, `sspec/status <change-name>` for specific change.

## Workflow

1. **Read** current state from:
   - `changes/<n>/tasks.md` for status, progress, blockers
   - `changes/<n>/proposal.md` for context if needed

2. **Calculate** progress:
   - Count completed tasks `[x]` vs total `[ ]`
   - Note any blockers or pivots

3. **Output** concise status report

## Output Format

### For specific change:
```
## Status: [change-name]

**State**: [STATUS] | **Progress**: [X/Y tasks]

**Recent**:
- [latest accomplishment from Progress section]

**Next**: [immediate next action from Plan]

**Blockers**: None / [list blockers]

**Pivots**: None / [recent direction changes]
```

### For overview (no name given):
```
## sspec Status

### Active Changes
- [change-1]: [STATUS] [X/Y] — [one line summary]
- [change-2]: [STATUS] [X/Y] — [one line summary]

### Recently Archived
- [archived-1] (YYYY-MM-DD)

### Global Notes
[any cross-cutting concerns from global handover.md]
```

## Guidelines

- Be concise — this is a quick check, not a report
- Highlight blockers prominently
- Include pivot indicator if direction changed recently
- Don't include full task lists — just progress count
