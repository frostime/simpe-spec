---
name: resume-change
desc: Resume an in-progress change from handover.md in 30 seconds.
---

Do not guess state from memory. Reconstruct it from the change files.

## Read order

1. **handover.md** — find newest Session Log entry → read **Next** items; scan Working Memory for key file list and recent decisions
2. **tasks.md** — locate the first unchecked `[ ]` task; skip completed `[x]` items
3. **spec.md** — brief context scan of the Problem Statement and Approach if the task scope is unclear

Stop reading when you can answer: what was I about to do next?

## Locating the change

If the exact change path is uncertain, run `sspec howto find-change` first, then come back here.

Once path is known:
```
sspec change status <name>   # verify status, shows spec/tasks/handover paths
```

## Quick rules

- Start from Session Log **Newest entry first** — that is where the freshest state lives.
- Do **not** read spec.md from the top unless you genuinely cannot reconstruct intent from handover + tasks alone.
- If handover.md says `Next: awaiting user approval`, your first action is alignment — not implementation.
- If tasks.md progress and handover.md `Next` conflict, handover.md wins (more recent).
