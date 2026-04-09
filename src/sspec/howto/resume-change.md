---
name: resume-change
desc: Resume an in-progress change from memory.md in 30 seconds.
---

Do not guess state from memory. Reconstruct it from the change files.

## Read order

1. **memory.md** — read `## State` first; then scan `Key Files`, `Knowledge`, and the newest line in `Milestones`
2. **tasks.md** — locate the first unchecked `[ ]` task; skip completed `[x]` items
3. **revisions/** — if the directory exists, scan revision files (newest first) to understand scope/design changes since the original spec
4. **spec.md** — brief context scan of the Problem Statement and Approach if the task scope is unclear
5. **design.md** — read if it exists and the current task involves technical design context

If the change has no `memory.md`, treat it as an old unsupported shape and read the raw markdown files directly instead of relying on CLI summaries.

Stop reading when you can answer: what was I about to do next?

## Locating the change

If the exact change path is uncertain, run `sspec howto find-change` first, then come back here.

Once path is known:
```
sspec change status <name>   # verify status, shows spec/tasks/memory paths
```

## Quick rules

- Start from `State` — that is the authoritative resume pointer.
- Do **not** read spec.md from the top unless you genuinely cannot reconstruct intent from memory + tasks alone.
- If `State` says you're awaiting user approval, your first action is alignment — not implementation.
- If tasks.md progress and `State` conflict, `State` wins (more recent intent).
