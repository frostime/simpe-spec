# Memory: pareto-cleanup

**Updated**: 2026-04-09T21:19

## Git Baseline (Immutable)
<!-- Captured during `sspec change new` before any change files are written.
This section records the change starting point in git and MUST NOT be edited or refreshed later. -->

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `refactor/sspec-vnext`
- HEAD: `2b143b54ea11fb94a397912aea3dd426cf12669f`
- Worktree: `clean`
- Status Snapshot: raw `git status --short --branch` output

```text
## refactor/sspec-vnext
```

## State
Implementation and self-host verification are complete.
Next: user review the cutover behavior; if accepted, this change can move to DONE.

## Key Files
- `.sspec/changes/26-04-09T19-28_pareto-cleanup/spec.md` — updated scope and no-compatibility boundary
- `.sspec/changes/26-04-09T19-28_pareto-cleanup/design.md` — cutover model, parsing rules, and status output contract
- `.sspec/changes/26-04-09T19-28_pareto-cleanup/tasks.md` — 4 execution phases with verification checkpoints
- `src/sspec/services/change_service.py` — parser/summarize logic to simplify to memory-only
- `src/sspec/commands/change.py` — `change status` rendering path to cut over

## Knowledge
- [2026-04-09T19:29] [Decision] Treat this work as a focused follow-up to `sspec-vnext`, not a rollback; keep `memory.md` and `Clarify` as the canonical vNext direction.
- [2026-04-09T19:48] [Decision] Backward compatibility is intentionally dropped: old `handover.md` changes are historical raw files, not a supported runtime contract.
- [2026-04-09T19:48] [Constraint] Ground truth is the markdown files themselves; CLI summaries are convenience output and do not need to preserve old parsed projections.
- [2026-04-09T19:48] [Gotcha] The current repo still contains many old-format changes, so `change status` degradation on them is an accepted consequence of the cutover.

## Milestones
- [2026-04-09T19:29] Created `pareto-cleanup` and drafted the initial compatibility-preserving repair plan.
- [2026-04-09T19:48] User chose a full cutover: revised spec/design/tasks to remove backward compatibility and standardize on `memory.md` only.
- [2026-04-09T20:06] Implemented memory-only parser/status/doc changes and verified focused tests pass (46 passed).
- [2026-04-09T21:19] Reinstalled package, ran `sspec project update`, and sandbox-verified new single/root status plus legacy unsupported output.
