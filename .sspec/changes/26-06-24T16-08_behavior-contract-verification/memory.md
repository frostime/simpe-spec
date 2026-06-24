# Memory: behavior-contract-verification

**Updated**: 2026-06-24T16:25+08:00

## Git Baseline (Immutable)
<!-- Captured during `sspec change new` before any change files are written.
This section records the change starting point in git and MUST NOT be edited or refreshed later. -->

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `main`
- HEAD: `b5375f90d7188b9042175e0a030861f61a401afe`
- Worktree: `clean`
- Status Snapshot: raw `git status --short --branch` output

```text
## main...origin/main
```

## State
Design drafted. Awaiting user confirmation of `spec.md` + `design.md` before entering Plan.

## Key Files
- `.sspec/changes/26-06-24T16-08_behavior-contract-verification/spec.md` — design gate summary: behavior contract, implementation changes, scope, effort.
- `.sspec/changes/26-06-24T16-08_behavior-contract-verification/design.md` — detailed section boundaries, templates, lifecycle trace, verification split.
- `src/sspec/templates/change/spec.md` — target single/sub-change spec template.
- `src/sspec/templates/change/tasks.md` — target phase verification and user-check template.
- `src/sspec/templates/skills/sspec-design/SKILL.md` — target design phase protocol.
- `src/sspec/templates/skills/sspec-plan/SKILL.md` — target planning protocol.
- `src/sspec/templates/skills/sspec-implement/SKILL.md` — target implementation completion protocol.

## Knowledge
- [2026-06-24T16:17+08:00] [Decision] Place `Behavior Contract` after `Approach` as a peer section under `Proposed Solution`; it is a result contract, not an implementation detail.
- [2026-06-24T16:17+08:00] [Decision] Rename target `Key Change` section to `Implementation Changes`; `Code Change` was rejected as too narrow for templates/docs/config/tests.
- [2026-06-24T16:25+08:00] [Decision] Implementation items use changelog-style labels, `type(scope): title`, instead of `IC-*`; examples include `feat`, `add`, `refactor`, `docs`, `test`, and `chore`.
- [2026-06-24T16:17+08:00] [Constraint] `spec.md` defines behavior boundaries; `tasks.md` defines agent verification and user black-box checks. Do not move click-by-click verification into `Behavior Contract`.
- [2026-06-24T16:17+08:00] [Constraint] Product template edits must land in `src/sspec/templates/`; after template edits run `uv pip install -e .` then `uv run sspec project update`.

## Milestones
- [2026-06-24T16:17+08:00] Created change and drafted `spec.md` + `design.md` for behavior contract, user checks, implementation-change naming, and scope effort.
- [2026-06-24T16:25+08:00] Revised implementation item labels from `IC-*` to changelog-style `type(scope): title` after user feedback.
