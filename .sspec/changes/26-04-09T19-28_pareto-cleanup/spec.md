---
name: pareto-cleanup
status: PLANNING
change-type: single
created: 2026-04-09T19:28:11
reference:
  - source: ".sspec/changes/26-04-08T17-37_sspec-vnext"
    type: "prev-change"
    note: "Follow-up to sspec-vnext. Closes review-discovered contract drift by enforcing a single post-vnext schema."
---

# pareto-cleanup

## Problem Statement

At least 3 product-facing contract drifts remain after `sspec-vnext`, and they all come from the same root cause: the repo currently tries to move to the new workflow while still half-parsing the old one.

1. `memory.md` is supposed to be the canonical continuity artifact, but parts of the CLI and HOWTO layer still depend on legacy `handover.md`, `Session Log`, and `Sub-Change Status` concepts.
2. Root-change memory now uses `## Coordination`, but status rendering still looks for old root snapshot shapes, so the default root template and the dashboard disagree.
3. `Research → Clarify` and `handover.md → memory.md` renames are only partially propagated. Some skill metadata and examples still teach obsolete lifecycle terms.

This leaves the system in an internally inconsistent state: templates say one thing, parser/CLI say another, and examples say a third. The result is not a clean vNext contract.

## Proposed Solution

### Approach

Treat this as a contract-closure change, not another methodology redesign. Keep the vNext direction (`memory.md`, `Clarify`, `design.md`, `revision`) and remove the remaining mixed-schema behavior.

The core strategy is a hard cutover:
- **single canonical contract** — only `memory.md` with `State`, `Milestones`, and root `Coordination` is recognized by the supported product surface;
- **no legacy parsing** — old `handover.md` / `Session Log` / `Sub-Change Status` shapes are treated as historical raw files, not a supported runtime contract.

This intentionally gives up backward compatibility in exchange for a simpler and internally consistent system. Ground truth remains the files themselves; CLI summaries are allowed to stop understanding old shapes.

### Key Change

**Fix A: Memory-only runtime contract** — Standardize the supported continuity schema around `memory.md` sections (`State`, `Key Files`, `Knowledge`, `Milestones`, `Coordination`) across templates, HOWTOs, and parser logic.

**Fix B: Status dashboard cutover** — Make `sspec change status` render only the new `memory.md` contract (`Current State`, `Latest Milestone`, `Coordination`) and explicitly show when a change has no supported memory artifact.

**Fix C: Clarify terminology closure** — Remove remaining phase-level `Research` / `Handover` wording from product-facing skill metadata and examples so lifecycle naming is internally consistent.

**Fix D: Self-host and regression closure** — Add focused tests for the new-format contract and explicit unsupported-old-shape behavior, then run `project update` so the self-hosted copies match the repaired source templates.

### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/core.py` | Simplify `ChangeStatusSummary` around the supported `memory.md` contract and remove legacy summary fields |
| `src/sspec/services/change_service.py` | Parse `State`, `Milestones`, and `Coordination`; remove `handover.md` / session-log fallback in summary and validation paths |
| `src/sspec/commands/change.py` | Render only new-format status blocks and make missing/unsupported memory explicit |
| `src/sspec/howto/resume-change.md` | Make `State` the primary resume source and stop presenting legacy sections as supported workflow |
| `src/sspec/howto/write-memory.md` | Clarify `State` authority, `Milestones` append-only usage, and root `Coordination` semantics |
| `src/sspec/templates/change/memory.md` | Tighten comments so the single-change memory schema is explicit |
| `src/sspec/templates/change-root/memory.md` | Tighten comments so `Coordination` is the authoritative root summary |
| `src/sspec/templates/skills/sspec-implement/SKILL.md` | Replace lingering `Session Log` continuity guidance with `Knowledge` + `Milestones` guidance |
| `src/sspec/templates/skills/sspec-design/SKILL.md` | Remove remaining `after research` wording |
| `src/sspec/templates/skills/sspec-design/examples-docs.md` | Remove remaining lifecycle examples that still say `Research` / `Handover` |
| `tests/test_change_service.py` | Add new-format summary tests and explicit unsupported-legacy tests |
| `tests/test_change_command.py` | Add CLI status rendering tests for new single/root and missing-memory behavior |

### What Stays Unchanged

- `memory.md` remains the canonical new continuity artifact; this change does **not** revert to `handover.md`
- `Clarify` remains the lifecycle entry posture; this change does **not** reintroduce `Research` as a phase name
- `design.md`, `revisions/`, and `scaffold` stay as the vNext structure
- Old historical changes are not migrated; if they still use `handover.md`, users/agents read the raw files directly

### Design Reference

→ Detailed technical design: [design.md](./design.md)
