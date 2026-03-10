# Handover: howto-integration-optimize

**Updated**: 2026-03-10T14:17

---

## Background

Integrate HOWTO into the visible sspec agent workflow: add discovery + point-of-need references in AGENTS.md template, add two missing builtin HOWTOs (`resume-change`, `write-handover`), and add delegation lines in three SKILL files. All changes are additive — no existing behavior is removed.

## Git Baseline (Immutable)
<!-- Captured during `sspec change new` before any change files are written.
This section records the change starting point in git and must not be edited or refreshed later. -->

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `feat/howto`
- HEAD: `880ad38c71b932566878b3d9bdadf07734a3d8a8`
- Worktree: `clean`
- Status Snapshot: raw `git status --short --branch` output

```text
## feat/howto
```

## Working Memory (Stable)
<!-- Curated, long-lived context. Survives context compression and session boundaries.
If something becomes obsolete, mark it as obsolete with a timestamp instead of deleting silently. -->

### Key Files
- `src/sspec/templates/AGENTS.md` — template to update; ground truth for managed block in root AGENTS.md
- `src/sspec/howto/` — builtin HOWTO directory; new files go here
- `src/sspec/templates/skills/sspec-research/SKILL.md` — add howto refs
- `src/sspec/templates/skills/sspec-implement/SKILL.md` — add howto ref
- `src/sspec/templates/skills/sspec-handover/SKILL.md` — add howto refs
- `.sspec/changes/26-03-10T14-16_howto-integration-optimize/reference/analysis.md` — full research analysis with gap table and anti-patterns

### Decisions (Timestamped)
- [2026-03-10T14:17] **Decision** - Track A (AGENTS.md) + Track B (new HOWTOs) + Track C (SKILL refs) as three parallel phases
  **Why**: Each track is independently verifiable and has zero intra-track dependencies.
- [2026-03-10T14:17] **Decision** - Only two new HOWTOs: `resume-change` and `write-handover` (not full list from gap analysis)
  **Why**: These are the highest-value gaps; others (`do-align`, `scale-assessment`) are lower priority and can follow in a later micro-change.

### Notes (Timestamped)
- [2026-03-10T14:17] AGENTS.md changes must go through `src/sspec/templates/AGENTS.md` only — never edit root AGENTS.md or `.github/` copies.
- [2026-03-10T14:17] After template edits: `uv pip install -e .` first, then `uv run sspec project update` to sync in-project copies.
- [2026-03-10T14:17] New HOWTO files go in `src/sspec/howto/` (builtin package location) — they become available via `sspec howto list` after reinstall.
- [2026-03-10T14:17] In SKILL files: add HOWTO references as brief one-liners (e.g., `→ sspec howto <name>`) without disrupting existing text or removing existing content.

## Session Log (Append-Only)
<!-- Newest entry first. Each entry is an atomic batch (one cohesive work record).

Header format:
### 2026-03-06T20:39 [work-log] <short title>

Tags are freeform but must be readable. Examples: work-log, user-feedback, argue, risk.
Any user interaction (feedback, @align, @argue) MUST start a new log entry. -->

### 2026-03-10T14:17 [work-log] Research, design, change creation

**Accomplished**
- Read add-howto-cli change (spec, handover, all 8 builtin HOWTOs)
- Read AGENTS.md template + CLI Quick Reference and SKILL System sections
- Read sspec-research, sspec-handover SKILL files for integration point analysis
- Read project.md for context and conventions
- Created change `26-03-10T14-16_howto-integration-optimize`
- Wrote `reference/analysis.md` with full gap analysis + anti-patterns
- Filled spec.md (problem statement, three-track approach, scope table)
- Filled tasks.md (four phases, 12 tasks, per-phase verification)

**Next**
- Await user alignment on design (spec.md) — mandatory @align gate before implementing
- If approved: implement Phase 1 (two new HOWTOs) → Phase 2 (AGENTS.md) → Phase 3 (SKILLs) → Phase 4 (sync/validate)
- ...
