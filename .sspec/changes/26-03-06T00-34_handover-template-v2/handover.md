# Handover: handover-template-v2

**Updated**: 2026-03-06T01:30

---

## Background
<!-- Write once on first session. What this change does and why (1-3 sentences).
Update only if scope fundamentally changes. Details belong in spec.md. -->

Improve `handover.md` templates and the handover SKILL so resumes are fast and predictable.
Main focus: separate stable context from volatile state and make per-session progress traceable.

## This Session

### Accomplished
<!-- Specific list of what got done this session -->

- Reviewed archived handovers and identified drift sources: mixed stable/volatile info and overwrite-prone session sections.
- Updated templates:
  - `src/sspec/templates/change/handover.md`
  - `src/sspec/templates/change-root/handover.md`
- Updated handover guidance:
  - `src/sspec/templates/skills/sspec-handover/SKILL.md`
  - `src/sspec/templates/AGENTS.md` (resume tip: newest Session Log entry)
- Reinstalled (`uv pip install -e .`) and validated in sandbox `tmp/test_handover_template_v2`.

### Next Steps
<!-- 1-3 specific file-level actions for the next agent -->

1. Ask user to review/accept the new handover template structure (Session Log + timestamped memory).
2. If accepted, archive this change.

## Working Memory
<!-- Agent's external memory. Survives context compression and session boundaries.
Update PROACTIVELY: important decision, key file found, non-obvious insight.
Test: "Would I struggle to reconstruct this after losing context?" → Write NOW. -->

### Key Files
<!-- Files critical to understanding/continuing this change.
- `path/file` — what it contains, why it matters -->

- `src/sspec/templates/change/handover.md` - single/sub handover template (Session Log + timestamps)
- `src/sspec/templates/change-root/handover.md` - root handover template (+ volatile snapshot table)
- `src/sspec/templates/skills/sspec-handover/SKILL.md` - handover procedure aligned with new structure
- `src/sspec/templates/AGENTS.md` - added a short resume tip pointing to Session Log

### Decisions
<!-- Important decisions with reasoning.
- **Decision**: Redis over Memcached
  **Why**: Need per-key TTL + persistence -->

- [2026-03-06T00:40] **Decision** - Prefer Session Log (source of truth) over a separate Resume Card.
  **Why**: Avoid duplicated "current state" summaries drifting out of sync.

### Notes
<!-- Non-obvious findings, edge cases, gotchas, risks.
Project-wide items → ALSO append to project.md Notes. -->
