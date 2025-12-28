# /status

Summarize current state.

## Task

Provide a concise status report covering:

1. **Current Change**: Name and brief description
2. **Status**: PLANNING / IN_PROGRESS / BLOCKED / REVIEW / DONE
3. **Progress**: X/Y tasks completed
4. **Recent**: What was done in recent work
5. **Next**: Immediate next step
6. **Blockers**: Anything blocking progress (if any)
7. **Pivots**: Recent direction changes (if any)

## Format

```
## Status: [change-name]

**State**: [STATUS] | Progress: [X/Y]

**Recent**:
- [latest accomplishment]

**Next**: [immediate next action]

**Blockers**: [none / list]
```

## Source

Read from:
- `changes/<n>/tasks.md` for current state
- `changes/<n>/proposal.md` for context if needed
