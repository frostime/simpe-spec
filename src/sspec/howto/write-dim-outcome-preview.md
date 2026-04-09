---
name: write-dim-outcome-preview
desc: "Design dimension: Outcome Preview — show what the result looks like after the change."
type: design-dimension
---

# Outcome Preview

## What It Answers

User's question: "What will it look like when done?"

## When to Choose

- The change produces a visible result (CLI output, UI, formatted text)
- Bug fix where before/after contrast clarifies the fix
- Performance optimization with measurable before/after metrics
- Configuration or deployment change where the end state matters more than internals

## How to Write

Show concrete result examples. Prefer actual output over description.

**Before/after pattern** — best for fixes and optimizations:

```text
# Before
$ sspec howto list
(no output, crashes with KeyError)

# After
$ sspec howto list
- name: resume-change
  source: builtin
  desc: Resume an in-progress change from memory.md in 30 seconds.
```

**Result demo pattern** — best for new features:

```text
$ sspec change new my-feature --tag frontend --tag backend
[OK] Created single change: 26-03-17T20-00_my-feature
     tags: [frontend, backend]
```

**Metric pattern** — best for performance:

```text
Before: API p95 latency 4.2s, DB CPU 85% at peak
After:  API p95 latency <200ms, DB CPU <40% at peak
```

Keep it short. One or two examples are enough. The goal is to anchor the user's
expectation of the end state, not to exhaustively document every output variation.

## Pairs Well With

- Behavioral Spec (outcome shows "what", behavior shows "how it gets there")
- Migration Path (outcome shows the target, migration shows how to reach it)
