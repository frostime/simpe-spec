---
name: write-handover-memory
desc: Write durable memory entries that survive across sessions.
---

Use this when updating `### Durable Memory (Typed, Timestamped)`.

## Core rule

Promote only facts that are still useful after the current batch ends.

Format:
- `[YYYY-MM-DDTHH:MM] [Type] <content>`

## Prefer these types

- Single/sub: `Alignment`, `Decision`, `VitalFinding`, `Constraint`, `Risk`, `VerificationShortcut`
- Root: `Alignment`, `CoordinationDecision`, `Dependency`, `CrossChangeFinding`, `Constraint`, `Risk`, `VerificationShortcut`
- Use a custom type only when the recommended labels are not clear enough

## Minimal chooser

- `Decision` / `CoordinationDecision` = durable choice to follow
- `Constraint` = hard limit or invariant
- `Dependency` = ordering or coupling rule
- `VitalFinding` / `CrossChangeFinding` = discovery that changes later work
- `Risk` = known failure mode or caution

## Examples

- Single/sub: `[2026-03-10T20:12] [Decision] Keep Session Log structure unchanged so resume parsing stays stable.`
- Root: `[2026-03-10T20:12] [CrossChangeFinding] Both Phase 1 and Phase 3 depend on the same config-version rule.`

Project-wide learning still goes to `project.md` Notes as well.
