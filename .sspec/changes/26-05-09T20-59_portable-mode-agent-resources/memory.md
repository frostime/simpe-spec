# Memory: portable-mode-agent-resources

**Updated**: 2026-05-09T22:05+08:00

## Git Baseline (Immutable)
<!-- Captured during `sspec change new` before any change files are written.
This section records the change starting point in git and MUST NOT be edited or refreshed later. -->

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `main`
- HEAD: `9ebe4700946c8261e5f35af6b2bc47030d31b9de`
- Worktree: `clean`
- Status Snapshot: raw `git status --short --branch` output

```text
## main...origin/main
```

## State

Implementation complete; change is in REVIEW. Next: user reviews `sspec portable` behavior and either accepts or requests adjustments.

## Key Files

- `.sspec/changes/26-05-09T20-59_portable-mode-agent-resources/spec.md` — product scope and behavior contract
- `.sspec/changes/26-05-09T20-59_portable-mode-agent-resources/design.md` — CLI contract, output format, resource read semantics, safety rules
- `src/sspec/templates/AGENTS.md` — source for `rule:project`
- `src/sspec/templates/skills/` — source for builtin SKILL index and `skill:` reads
- `src/sspec/services/portable_service.py` — portable bootstrap rendering and safe resource reader
- `src/sspec/commands/portable.py` — CLI command group for portable mode
- `tests/test_portable_service.py` — service-level coverage for portable resources
- `tests/test_portable_command.py` — command-level coverage for no-project portable usage

## Knowledge

- [2026-05-09T20:59+08:00] Decision: Command name is `portable`, not `resource` or `guide`; `portable` communicates no-project/no-state use and avoids implying normal sspec workflow.
- [2026-05-09T20:59+08:00] Constraint: `sspec portable` must not output all SKILL bodies; it should expose a standard `<available_skills>` index and rely on `sspec portable read skill:<name>` for on-demand loading.
- [2026-05-09T20:59+08:00] Constraint: Portable mode overlay wins over project rule/SKILL instructions when they conflict; no implicit `project init`, `change new`, or `.sspec/` writes.
- [2026-05-09T21:09+08:00] Decision: `sspec portable` must assume zero sspec context and first explain what sspec is before stating portable constraints.
- [2026-05-09T21:09+08:00] Decision: Rename read target `rule:project` to `rule:sspec`; do not expose `rule:portable` because portable guidance is the bootstrap itself.
- [2026-05-09T21:09+08:00] Decision: Default output uses progressive disclosure; it does not inline AGENTS.md/rule body and instead instructs `sspec portable read rule:sspec`.

## Milestones

- [2026-05-09T20:59+08:00] Created change and drafted spec/design for portable Agent resource mode.
- [2026-05-09T21:09+08:00] Revised design to add zero-context explanation, behavior mapping, `rule:sspec`, HOWTO reads, and progressive disclosure.
- [2026-05-09T21:57+08:00] Implemented portable command and moved change to REVIEW; focused tests and smoke checks passed.
- [2026-05-09T22:05+08:00] Updated portable read source metadata from package-relative logical paths to absolute local paths for direct Agent reads.
