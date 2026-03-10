---
name: find-change
desc: Find the exact change the user is talking about before resuming work.
---

Do not guess the target change from natural language alone. Prove it with CLI output plus filesystem checks.

## What actually helps

- `sspec change list` to see current active / archived candidates
- `sspec change find <name>` to probe one likely candidate quickly
- a shell or filesystem listing of `.sspec/changes/`
- the change directory naming rule itself

## Filesystem facts that matter

Active changes live under `.sspec/changes/`; archived ones live under `.sspec/changes/archive/`.

Change directory names follow this shape:
`<yy-MM-ddTHH-mm>_<slug>`

Examples:
- `26-03-09T23-41_add-howto-cli`
- `26-03-06T16-25_rename-ask`

This means the suffix usually carries the human topic, while the prefix tells you recency.

## Failure rule

If two candidates still look plausible, stop and disambiguate. Ask the user which change they mean.
