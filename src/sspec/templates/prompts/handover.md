# sspec/handover

Generate a session handover document for continuity.

## Context

The conversation is ending. Create a handover that enables another AI to resume seamlessly.

## Workflow

1. **Review** what was accomplished this session
2. **Assess** current state — what works, what doesn't
3. **Identify** concrete next steps
4. **Note** any gotchas or context that's easy to miss

## Output Structure

```markdown
## Background
[Brief context: what project/task, why it matters — 1-2 sentences]

## Done
[What was accomplished this session — specific files, features, fixes]

## Current State
[Exact state right now]
- Working: [what functions correctly]
- Not working: [what's broken or incomplete]
- Blocked on: [if any blockers]

## Next Steps
[Concrete actions in priority order]
1. [First thing to do]
2. [Second thing]
3. [Third thing]

## Key Context
[Non-obvious information the next session needs]
- Files: [relevant file paths]
- Gotchas: [things that might trip someone up]
- Decisions: [recent decisions with brief rationale]
```

## Style Guidelines

- **High information density** — no filler phrases
- **Concrete over abstract** — file paths, function names, error messages
- **Actionable next steps** — not "continue working on X"
- **Include failure context** — what was tried and didn't work

## After Writing

Update the relevant handover file:
- Working on specific change → `changes/<n>/handover.md`
- Cross-change or global state → `.sspec/handover.md`

Set the "Updated" timestamp.

## Quality Check

Before finishing, verify:
- [ ] Could another AI continue without asking questions?
- [ ] Are file paths specific, not vague references?
- [ ] Are next steps immediately actionable?
- [ ] Are potential gotchas documented?
