---
created: '2026-03-10T20:19:17'
name: handover_memory_design
why: 'Design phase gate for change `handover-memory-structure`. The durable-memory
  redesign is

  now drafted in spec.md and needs explicit confirmation before planning.'
---

**Ask**: handover_memory_design

# User Answer #

USER_FILL_HERE

# Agent Question History #

handover-memory-structure:
**Context**: Real handovers are duplicating information between `Working Memory -> Decisions / Notes`
and `Session Log`, mainly because `Notes` has become a catch-all bucket.

**Proposed design**:
- Replace `Decisions` + `Notes` with one `Durable Memory (Typed, Timestamped)` section
- Keep `Session Log` unchanged as the only source of current-batch progress + real `Next`
- Use recommended canonical types: `Alignment`, `Decision`, `VitalFinding`, `Constraint`, `Risk`, `VerificationShortcut`
- Allow rare custom types when the canonical set is not expressive enough
- Teach a promotion rule in SKILL/HOWTO: only facts still useful after the current batch ends should be promoted into durable memory

**See**: `.sspec/changes/26-03-10T20-00_handover-memory-structure/spec.md`

Do you approve this design for planning, or do you want any changes to the section name,
recommended types, or entry rules before I move on to `tasks.md`?