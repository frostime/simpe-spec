---
name: use-sspec-ask
desc: Record decisions with `sspec ask` when the answer must survive the current turn.
---

# use-sspec-ask

Use `sspec ask` when the answer must still be available next session.

- Design approval gates
- Blockers or conflicting requirements
- Decisions future agents may need to trace
- Long tradeoff questions that deserve a durable record

1. `sspec ask create <topic>`
2. Fill `reason` and `question`
3. `sspec ask prompt <file>`

- Put long analysis in `.sspec/tmp/` and link it.
- Ask for one decision, not a whole meeting.
- Batch closely related questions together.

If losing the answer would cause rework next session, record it with `sspec ask`.
