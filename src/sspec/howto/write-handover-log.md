---
name: write-handover-log
desc: Write one atomic Session Log entry in handover.md.
---

Use this when updating `## Session Log (Append-Only)`.

## Rules

- Newest-first, append-only. Never rewrite or delete old log entries.
- One entry = one cohesive batch of work.
- Header format: `### <ISO-timestamp> [tag] <short title>`
- Every entry MUST include both `**Accomplished**` and `**Next**`
- Any user interaction (`@align`, feedback, `@argue`) MUST start a fresh log entry

## What belongs here

- What you completed this batch
- The real next action that an agent should start with next time
- Batch-local notes, surprises, review outcomes, or temporary reminders

## Anti-patterns

- Vague `Next` like "continue work"
- Future tense inside `Accomplished`
- Mixing multiple unrelated work batches into one entry
- Promoting immediate next-step state into Durable Memory instead of the log
