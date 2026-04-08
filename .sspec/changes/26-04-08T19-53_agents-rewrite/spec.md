---
name: agents-rewrite
status: DOING
change-type: sub
created: 2026-04-08T19:53:24
reference:
  - source: ".sspec/changes/26-04-08T17-37_sspec-vnext"
    type: "root-change"
    note: "Phase 3: AGENTS.md Rewrite"
---

# agents-rewrite

## Problem Statement

Current AGENTS.md template (~160 lines) has structural issues after Phase 1+2 changes:
1. File tree doesn't reflect new structure (design.md, revisions/)
2. Phase contracts table references outdated SKILL outputs
3. No constitution layer — Presentation Rules, immutable baseline, revision protocol are absent
4. Change evolution (amend/follow-up/supersede) buried in HOWTO instead of first-class
5. Research/Design descriptions don't match updated SKILLs (alignment at beginning, solution discovery)

## Proposed Solution

### Approach

Rewrite `src/sspec/templates/AGENTS.md` following the three-layer rule model:
- **Constitution** (in AGENTS.md): predictability principle, Presentation Rules, immutable baseline + revision, change evolution protocol
- **Stage Contract** (SKILL refs): phase table points to updated SKILLs
- **Optional Lens** (HOWTO refs): detailed guidance on-demand

### Key Change

**Rewrite A: Constitution Layer** — Add §1.5 or embed in §0: Presentation Rules (code block, ASCII diagram, table, labeled items as minimum quality bar), immutable baseline rule, revision protocol summary.

**Rewrite B: Change Workflow Update** — Update file tree, phase contracts table (Research output = aligned understanding, Design output = spec.md + design.md), lifecycle diagram to show Research alignment + Design solution discovery.

**Rewrite C: Change Evolution Protocol** — Promote amend/follow-up/supersede from HOWTO to AGENTS.md as first-class section. Three actions with clear triggers + procedures.

**Rewrite D: Reference Cleanup** — Update directive shortcuts, CLI reference, SKILL list to match current state.

### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/templates/AGENTS.md` | Full rewrite |

### Design Reference

No separate design.md needed — this is a single-file template rewrite. Design decisions are already locked in root spec.md D4-D6.
