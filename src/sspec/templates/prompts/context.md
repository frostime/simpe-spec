# sspec/context

Reload project context and current state.

## When to Use

- Starting a new session
- After a long tangent or context switch
- Before making significant decisions
- When feeling lost about project state

## Workflow

1. **Read project knowledge**
   - `.sspec/knowledge/index.md` — project overview, tech stack, conventions
   - Other `.sspec/knowledge/*.md` files as relevant

2. **Check active work**
   - `.sspec/changes/` — list active changes
   - Identify which change is current focus

3. **Load current change context**
   - `proposal.md` — why and what
   - `tasks.md` — plan, progress, current state
   - `handover.md` — previous session state

4. **Check global state**
   - `.sspec/handover.md` — cross-change context

## Output

Provide a brief confirmation:

```
## Context Loaded

**Project**: [name] — [one-line description]
**Tech**: [key technologies]
**Conventions**: [critical conventions to follow]

**Active Change**: [name] ([STATUS])
**Progress**: [X/Y] tasks
**Current Task**: [what's in progress or next]

**Key Constraints**:
- [important constraint 1]
- [important constraint 2]

Ready to continue.
```

## Guidelines

- Keep confirmation brief — user knows their project
- Highlight anything that might be easy to forget
- Note any blockers or pivots from previous session
- Don't dump entire file contents — summarize
