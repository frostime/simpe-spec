---
name: handle-obsolete-memory
desc: Clean up obsolete durable memory without destroying useful history.
---

Use this when an existing durable-memory entry is no longer valid.

## Default posture

Keep history visible.

- Prefer marking the entry obsolete with a timestamp
- Delete only pure noise, accidental duplicates, or placeholder residue with no lasting value

## Mark obsolete when

- The fact used to be true and explains earlier decisions
- Future agents may need to know why the rule changed
- Removing it would hide meaningful change history

Example:
- `[2026-03-10T20:12] [Constraint] Use temporary YAML bridge during migration. (obsolete at 2026-03-12T09:40 - bridge removed in Phase 2)`

## Delete when

- The line is an obvious duplicate of a better entry
- The line is leftover template filler
- The line is accidental noise with no resume value
