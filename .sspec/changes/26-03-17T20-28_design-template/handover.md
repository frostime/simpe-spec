# Handover: design-template

**Updated**: 2026-03-17T22:00

---

## Background

Replace the fixed sub-section template (Interface Design / Data Flow / Key Logic) in sspec-design SKILL Step 3A with a "predictability dimensions" menu. Each dimension is a howto card that agents load on demand. Also adds `type` field to howto system for classification and filtering.

## Git Baseline (Immutable)

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `feat/better-design`
- HEAD: `d2d496efc7e92ddcf52c43d68eca3b091d9f7200`
- Worktree: `dirty`
- Status Snapshot: raw `git status --short --branch` output

```text
## feat/better-design
A  .sspec/requests/26-03-17T19-42_design-template.md
```

## Working Memory (Stable)

### Key Files
- `src/sspec/templates/skills/sspec-design/SKILL.md` - Core SKILL rewritten with dimension menu + universal rules
- `src/sspec/templates/change/spec.md` - Template comment updated to reference dimensions
- `src/sspec/services/howto_service.py` - HowtoInfo.type field + parsing
- `src/sspec/commands/howto.py` - --type filter on list_cmd
- `src/sspec/howto/write-dim-*.md` - 8 dimension howto cards
- `src/sspec/templates/skills/sspec-design/examples-*.md` - 3 scenario example files + root

### Durable Memory (Typed, Timestamped)
- [2026-03-17T20:00] [Alignment] spec.md is a "prediction contract" — user reads it to form expectations of execution result. Different changes need different prediction dimensions.
- [2026-03-17T20:00] [Decision] Dimensions delivered as typed howtos (not examples files) to avoid "template anchoring effect" — agents see building blocks, not fixed patterns to copy.
- [2026-03-17T20:00] [Decision] Old Presentation Rules split: Rules 3-4 (Scope Summary + Item Labeling) stay as Universal Rules in SKILL; Rules 1-2 (code blocks + ASCII diagrams) move to dimension howto cards.
- [2026-03-17T20:00] [Decision] Template files not split — single `change/spec.md` with updated comment. Agent decides dimensions at design time, not at `sspec change new` time.
- [2026-03-17T20:00] [Decision] howto system gains `type` field (optional, backward compatible) + `--type` filter on `sspec howto list`.
- [2026-03-17T22:00] [VitalFinding] examples-root.md had stale Rule 1-4 references — caught by subagent audit, fixed.

## Session Log (Append-Only)

### 2026-03-17T22:00 [work-log] Subagent audit fixes

**Accomplished**
- Ran 3 subagent audits (Python code, examples/cards, SKILL/template)
- Fixed C1: examples-root.md stale Rule 1-4 references
- Fixed W1-code: whitespace-only type → None normalization
- Fixed W3-code: better message when --type filter matches nothing
- Fixed W1-root: sub-change guidance uses dimension-neutral language
- Fixed W2-SKILL: added note to read dimension howto writing norms
- Fixed S1/S2/S3: type annotation, Step 4 wording, Behavioral Spec pairs

**Next**
- Change is REVIEW → user satisfied → handover + close

### 2026-03-17T21:00 [work-log] Implementation complete

**Accomplished**
- Phase 1: Added `type` field to HowtoInfo + `--type` filter on howto list
- Phase 2: Created 8 dimension howto cards (write-dim-*)
- Phase 3: Rewrote SKILL Step 3A with dimension menu + universal rules
- Phase 4: Split examples-single.md into examples-feature/docs/refactor.md
- Phase 5: Updated spec.md template Key Design comment
- Phase 6: Sync + smoke test passed (lint clean, init produces updated template)

**Next**
- Subagent audit on full diff

### 2026-03-17T20:28 [work-log] Design phase

**Accomplished**
- Discussed design direction with user: prediction contract framing, dimension menu, howto delivery
- Created change from request, filled spec.md with 7 change items (A-G)
- User approved design

**Next**
- Plan and implement
