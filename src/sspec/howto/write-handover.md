---
name: write-handover
desc: Write effective handover entries so any agent can resume in 30 seconds.
---

## Session Log rules (append-only, newest-first)

Each entry MUST have:
- **Header**: `### <ISO-timestamp> [tag] <title>` — tag examples: `work-log`, `user-feedback`, `argue`, `risk`
- **Accomplished**: bullet list of what was done this batch
- **Next**: concrete next action(s) — enough to start work without re-reading everything
- **Notes** (optional): gotchas, edge cases, risks discovered this batch

**Immutable rule**: Never edit or delete old entries. Mark obsolete items with a timestamp note instead.

**New entry triggers**: any user feedback, @align gate, @argue event, or major phase switch — each MUST start a new log entry.

## Working Memory rules

**Key Files** — list only files that future work directly depends on, one line per file: `path/file — why it matters`.

**Decisions** — timestamp every entry. Format: `[YYYY-MM-DDTHH:MM] **Decision** — what. **Why**: reason.`
If a decision is superseded, mark old entry `(superseded at <timestamp>)` — do not delete.

**Notes** — timestamp every entry. Capture gotchas, edge cases, verification shortcuts. If something caused a surprise or wasted time, write it here.

## When to promote to project.md

Write to `project.md` Notes when the discovery applies to the whole codebase, not just this change.
Format: `- YYYY-MM-DD: <learning>`

## Anti-patterns

- Writing future tense in Accomplished ("will do X") — Accomplished is past tense only
- Leaving Next empty or vague ("continue work") — Next must be a concrete starting action
- Deleting or rewriting old Session Log entries — append only, always
- Skipping handover at session end — it is mandatory, no exceptions
