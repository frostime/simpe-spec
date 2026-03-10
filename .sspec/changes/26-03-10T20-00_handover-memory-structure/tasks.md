---
change: "handover-memory-structure"
updated: "2026-03-10T21:23"
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Handover Templates ✅
- [x] Update `src/sspec/templates/change/handover.md` - replace `Decisions` / `Notes` with `Durable Memory (Typed, Timestamped)` and add inline type examples per `spec.md` B
- [x] Update `src/sspec/templates/change-root/handover.md` - apply the same typed durable-memory model while preserving root-only coordination sections
- [x] Verify `src/sspec/services/change_service.py` assumptions stay satisfied by leaving `Session Log` headings and `**Next**` structure unchanged
**Verification**: Template diffs show only durable-memory structure changes; `Session Log` heading format and `Next` block remain intact in both handover templates

### Phase 2: Writing Guidance ✅
- [x] Update `src/sspec/templates/skills/sspec-handover/SKILL.md` - teach durable-vs-batch triage, recommended canonical types, and the rare custom-type escape hatch
- [x] Refactor handover HOWTO guidance under `src/sspec/howto/` - split concrete writing jobs away from the phase-level SKILL
- [x] Align wording across template comments, SKILL guidance, and HOWTO examples so they use the same section name, entry format, and promotion rule
**Verification**: No guidance file still instructs agents to write `Decisions` / `Notes`; all guidance uses the same typed-memory terminology and promotion rule

### Phase 3: Template Sync and Validation ✅
- [x] Run `uv pip install -e .` - refresh packaged templates after editing source files
- [x] Run `uv run sspec project update` - sync self-hosted generated copies from template sources
- [x] Create a tmp sandbox and run `uv run sspec change new <name>` plus `uv run sspec change new <name> --root` - confirm newly generated handovers contain typed durable memory and unchanged `Session Log`
**Verification**: Self-hosted copies and sandbox-generated `handover.md` files match the new structure for both single and root changes

### Feedback Tasks
- [x] Update `spec.md` plus template comments so root changes use coordination-oriented recommended memory types instead of the single-change type set
- [x] Update `src/sspec/templates/skills/sspec-handover/SKILL.md` and `src/sspec/howto/write-handover.md` to explain the single-vs-root type split clearly
- [x] Re-run template sync and sandbox generation to verify both handover kinds render their own recommended type hints
- [x] Keep `.sspec/changes/26-03-10T20-00_handover-memory-structure/handover.md` on the legacy structure by explicit user exception; do not back-migrate the active change record
- [x] Add modest extra type examples in root template / SKILL / HOWTO, and document obsolete-memory handling with a default "mark obsolete" policy instead of silent deletion
- [x] Refactor `src/sspec/howto/write-handover.md` into a lightweight router instead of a SKILL duplicate
- [x] Add `src/sspec/howto/write-handover-log.md`, `src/sspec/howto/write-handover-memory.md`, and `src/sspec/howto/handle-obsolete-memory.md` as focused handover HOWTOs
- [x] Update `src/sspec/templates/skills/sspec-handover/SKILL.md` to reference the focused HOWTOs at the point of need
- [x] Re-sync and validate `sspec howto list` plus targeted `sspec howto ...` reads for the new handover HOWTO set

---

## Progress

**Overall**: 100%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 100% | ✅ |
| Phase 2 | 100% | ✅ |
| Phase 3 | 100% | ✅ |
| Feedback follow-up | 100% | ✅ |
| HOWTO refactor follow-up | 100% | ✅ |

**Recent**:
- 2026-03-10: Replaced the overlapping `write-handover` HOWTO with a router plus focused handover HOWTOs, then validated discovery and targeted reads through `sspec howto`.
