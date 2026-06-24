---
name: sspec-plan
description: "Break design into concrete tasks. Fill tasks.md with file-level execution plan. Use after design alignment."
metadata:
  author: frostime
  version: 3.0.0
---

# SSPEC Plan

---

## Output Contract

When this phase ends, tasks.md MUST contain:
- Phases with file-level tasks (single/sub) OR milestones (root)
- Verification criteria for each phase
- User Check steps for phases that implement user-visible `BC-*` behavior
- Progress section initialized

## Task Quality Standards

Each task SHOULD be:
- **Specific**: names exact file path + action
- **Small**: <2 hours
- **Independently testable**: has an obvious check

## Reference Spec, Don't Repeat

tasks.md references spec.md / design.md — never re-describe design.

| spec.md / design.md | tasks.md |
|---|---|
| Defines behavior contracts, interfaces, data model, logic | Lists file-level actions + verification |
| Explains *how it should work* | Tells agent *what to do next* and how to verify |
| `BC-1: cache hit behavior` | `User Check: BC-1: sign in twice -> second request uses cache` |
| `feat(cache): Add user cache module` | `Create cache.py — implement interface per spec` |

- ✅ "Implement `feat(cache): Add user cache module` per spec"
- ✅ "Create handler following the data flow in design.md"
- ✅ "User Check: BC-1: run command X -> observe output Y"
- ❌ Re-listing all function signatures
- ❌ Re-describing the algorithm
- ❌ Defining new behavior that is not in spec.md Behavior Contract

## Single/Sub vs Root

| change-type | tasks.md form |
|------------|---------------|
| `single` / `sub` | Phase-based, file-level tasks (<2h each) |
| `root` | Milestone-based, one entry per sub-change (no file-level detail) |

Root rules: no file-level tasks; each phase has Deliverable + Sub-change link; root stays active until all sub-changes complete.

## Verification

Each phase MUST have explicit verification criteria.

Use this split:
- **Verification**: agent-run checks such as test commands, build/lint, sandbox CLI runs, and expected output.
- **User Check**: black-box review steps for user-visible `BC-*` behavior. State user action + expected observable result.

Rules:
- Behavior boundary/default/error/compatibility changes SHOULD include `User Check` unless impractical.
- Pure internal/refactor-only changes MAY omit `User Check` when spec.md states no user-visible behavior change.
- Do not write "it works"; name the specific passing condition.

## Exit: @align Report

Present the task breakdown (phases, total tasks, key Verification/User Check criteria). This is a `report`, not a hard gate — continue to `sspec-implement` unless the user interrupts.

📚 Examples: [examples.md](./examples.md)
