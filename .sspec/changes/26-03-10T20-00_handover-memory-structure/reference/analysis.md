# Research Notes

## Goal

Assess whether the default `handover.md` structure creates avoidable duplication between
`Working Memory` and `Session Log`, especially around `Decisions` / `Notes`.

## Files Reviewed

- `src/sspec/templates/change/handover.md`
- `src/sspec/templates/change-root/handover.md`
- `src/sspec/templates/skills/sspec-handover/SKILL.md`
- `src/sspec/howto/write-handover.md`
- `.sspec/changes/26-03-09T23-41_add-howto-cli/handover.md`
- `.sspec/changes/26-03-10T14-16_howto-integration-optimize/handover.md`
- `.sspec/changes/archive/26-03-06T23-39_refresh-spec-docs/handover.md`
- `.sspec/changes/archive/26-03-06T00-34_handover-template-v2/spec.md`
- `src/sspec/services/change_service.py`

## Current Structure

Single change template:

- `Background`
- `Git Baseline (Immutable)`
- `Working Memory (Stable)`
  - `Key Files`
  - `Decisions (Timestamped)`
  - `Notes (Timestamped)`
- `Session Log (Append-Only)`

The current intent is already "stable vs volatile" separation, introduced by
`handover-template-v2`.

## What Is Working

- `Session Log` is a strong resume entry point.
- `Key Files` is consistently useful and low ambiguity.
- `change_service.py` currently parses `Updated`, `Session Log`, and `Next`; it does not depend
  on `Decisions` / `Notes`, so Memory-side refactors are low-risk as long as `Session Log`
  headings stay compatible.

## Observed Duplication Patterns

### 1. "Next action" leaks into Memory Notes

Example: `.sspec/changes/26-03-09T23-41_add-howto-cli/handover.md`

- Memory note: "Before implementation starts, align on the first builtin HOWTO batch..."
- Session Log `Next`: "Align the HOWTO design with the user..."

These serve the same resume purpose, but one is stable memory and the other is volatile state.

### 2. Session outcomes leak into Memory Notes

Same handover contains Memory notes like:

- validation passed
- smoke checks passed
- tests were updated
- builtin docs were rewritten/compressed

Those are usually session outcomes, already represented better in `Session Log -> Accomplished`
or `Session Log -> Notes`.

### 3. Process state leaks into Decisions

Example: `.sspec/changes/archive/26-03-06T23-39_refresh-spec-docs/handover.md`

- `Decision`: "Close the implementation phase in one batch and hand the change to review."

That is a phase transition / work-state choice, not long-lived change knowledge.

### 4. The meaning of Memory Notes is too broad

Current guidance says Notes can hold gotchas, edge cases, risks, and verification shortcuts.
Real usage expands further into:

- future reminders
- completed verification records
- implementation progress summaries
- one-off review context

This makes `Notes` a catch-all bucket.

## Likely Root Causes

1. `Notes` is semantically overloaded.
2. There is no explicit "promotion rule" from Session Log into Working Memory.
3. Both places allow timestamped bullets, so the visual shape is almost identical.
4. Session Log also has an optional `Notes` block, which increases overlap with Memory `Notes`.
5. `Decisions` currently mixes enduring design choices with temporary workflow decisions.

## Design Directions Worth Discussing

### Option A - Keep sections, tighten meaning

Keep `Decisions` + `Notes`, but redefine them more narrowly:

- `Decisions` = enduring change decisions only
- `Notes` = durable gotchas / invariants / resume-critical caveats only
- everything session-specific stays in `Session Log`

Pros: smallest migration, lowest disruption.
Cons: relies heavily on discipline; the template shape still invites drift.

### Option B - Replace `Notes` with a narrower bucket

Example replacements:

- `Constraints / Gotchas`
- `Resume Risks`
- `Invariants / Caveats`

Pros: removes the catch-all label.
Cons: still leaves `Decisions` vs the new bucket boundary to define.

### Option C - Merge `Decisions` + `Notes` into one durable memory section

Example:

- `Working Memory`
  - `Key Files`
  - `Durable Knowledge`

Each entry could carry a type label such as `Decision`, `Constraint`, `Risk`, `Shortcut`.

Pros: reduces section-boundary confusion and duplicate placement decisions.
Cons: weaker scannability unless entry format is very disciplined.

## Initial Recommendation

Option B looks like the best next design candidate.

Reason:

- The main problem is not that `Decision` exists; it is that `Notes` is too broad.
- Keeping `Decision` preserves an explicit place for rationale-bearing choices.
- Replacing `Notes` with a narrower label should reduce duplicate content without collapsing all
  durable memory into one mixed list.

Candidate shape to discuss:

- `Key Files`
- `Decisions (Timestamped)`
- `Constraints / Gotchas (Timestamped)`
- `Session Log (Append-Only)`

## Likely Implementation Surface

- `src/sspec/templates/change/handover.md`
- `src/sspec/templates/change-root/handover.md`
- `src/sspec/templates/skills/sspec-handover/SKILL.md`
- `src/sspec/howto/write-handover.md`
- possibly `tests/test_change_service.py` if we want stronger template coverage

## Compatibility Note

`src/sspec/services/change_service.py` extracts the latest session summary from `## Session Log`
and `**Next**`. If those stay unchanged, the dashboard / resume behavior should not need service
changes for a Memory-only restructure.
