# Memory: slim-agents-router

**Updated**: 2026-06-27T13:55+08:00

## Git Baseline (Immutable)
<!-- Captured during `sspec change new` before any change files are written.
This section records the change starting point in git and MUST NOT be edited or refreshed later. -->

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `refactor/slim-agents-router`
- HEAD: `de7e402e6bdc69d8580ae6b78b5547639bcd26e1`
- Worktree: `clean`
- Status Snapshot: raw `git status --short --branch` output

```text
## refactor/slim-agents-router
```

## State

Implementation complete; change is in REVIEW. Root `AGENTS.md` is now a router, `.sspec/SSPEC.rule.md` is the managed full workflow rule, and `sspec_schema` is `7.0`.

## Key Files

- `.sspec/changes/26-06-27T13-30_slim-agents-router/spec.md` — behavior contract and implementation scope.
- `.sspec/changes/26-06-27T13-30_slim-agents-router/design.md` — router/rule structure, CLI/update flow, hash contract, test matrix.
- `src/sspec/templates/AGENTS.md` — current full protocol source; target becomes router.
- `src/sspec/templates/SSPEC.rule.md` — planned new full protocol source.
- `src/sspec/core.py` — planned `SCHEMA_VERSION = '7.0'` and managed file list change via `UPDATABLE_FILES`.
- `src/sspec/services/project_init_service.py` — init creates managed files and hashes.
- `src/sspec/services/project_update_service.py` — update candidate state machine for managed files.
- `src/sspec/services/portable_service.py` — compatibility shim needed for `rule:sspec` source.
- `tmp/baseline-sspec-6.2/` — clean 6.2 initialized project for copy-based update migration testing.

## Knowledge

- [2026-06-27T13:30+08:00] Decision: Use `.sspec/SSPEC.rule.md`, not `.sspec/rules/`, because there is one core sspec rule and the path should stay short/top-level.
- [2026-06-27T13:30+08:00] Decision: `.sspec/project.md` remains a top-level trigger and user-managed project context; it is not replaced by the new rule file.
- [2026-06-27T13:30+08:00] Decision: `.sspec/SSPEC.rule.md` is managed by sspec update; local edits are skipped by default and only overwritten by `--force`.
- [2026-06-27T13:30+08:00] Decision: Do not redesign portable mode; only preserve compatibility by making `sspec portable read rule:sspec` read the new full-rule source.
- [2026-06-27T13:30+08:00] Constraint: Root `AGENTS.md` should be a router, not a full workflow manual; the largest removable content is the change lifecycle/workflow section.
- [2026-06-27T13:34+08:00] Decision: Bump `SCHEMA_VERSION` / `.meta.json.sspec_schema` from `6.2` to `7.0`; keep `.meta.json.meta_schema` unchanged because metadata shape is unchanged.
- [2026-06-27T13:34+08:00] Decision: Do not add a full `sspec_schema` Markov migration runner in this change; use existing managed-template update flow plus explicit `sspec_schema` drift persistence.
- [2026-06-27T13:34+08:00] Insight: Existing code has schema-chain migration for `meta_schema`, but `sspec_schema` is currently only a protocol marker overwritten during project update.
- [2026-06-27T13:36+08:00] Insight: `tmp/baseline-sspec-6.2/` was created with current code: `sspec_schema=6.2`, `meta_schema=2.1`, root `AGENTS.md` length 5557 chars, no `.sspec/SSPEC.rule.md`, 8 installed skills.
- [2026-06-27T13:55+08:00] Insight: Final fresh-init and copied-baseline migration sandboxes both produced router `AGENTS.md` length 1188 chars, full `.sspec/SSPEC.rule.md`, `sspec_schema=7.0`, and `file_hashes['SSPEC.rule.md']`.
- [2026-06-27T13:30+08:00] Rejected: A pure CLI-triggered rule with no root AGENTS router; it risks missed triggers in installed projects.

## Milestones

- [2026-06-27T13:30+08:00] Created branch `refactor/slim-agents-router`, scaffolded change, and drafted spec/design for user alignment.
- [2026-06-27T13:34+08:00] Added `sspec_schema` 7.0 migration compatibility design and deferred full protocol migration runner.
- [2026-06-27T13:36+08:00] Created `tmp/baseline-sspec-6.2/` for future copy-based update migration checks.
- [2026-06-27T13:55+08:00] Implemented all tasks, moved change to REVIEW, and verified changed-file lint, 116 targeted tests, fresh init, and 6.2 baseline migration.
