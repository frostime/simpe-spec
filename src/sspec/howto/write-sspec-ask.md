---
name: write-sspec-ask
desc: Write a properly structured `sspec ask` for phase gates and durable decisions.
---

**Workflow** — treat as one atomic unit, do not split:

```bash
sspec ask create <topic>      # creates .yml template
# → edit file: fill reason + question fields
sspec ask prompt <path>       # user answers → converted to .md record
```

## Skeleton

```yaml
reason: |
  <why alignment is needed — 1-2 sentences>
question: |
  <change-name>:
  **Context**: <key state / problem>
  **Decision**: <what needs approval>
  **See**: <file path if helpful>

  <explicit question>
```

## What to include by phase

| Phase | Include in question |
|-------|---------------------|
| Design | Problem summary, approach, key design decisions, Scope, link to `spec.md` |
| Plan | Phase count, total tasks, key files, verification criteria, link to `tasks.md` |
| Implement review | What was done, tasks completed, what to review |
| Blocker | "Design says X, found Y — which direction?" |
| Mid-research | Interpretation A vs B — which is correct? |

## Anti-pattern

```yaml
# Bad: dump 200 lines of analysis into the question field
# Correct: write analysis to .sspec/tmp/<topic>.md, reference path in question
question: |
  See draft at .sspec/tmp/design-draft.md.
  Option A: <brief>. Option B: <brief>.
  Which approach?
```
