---
name: sspec-plan
description: "Break design into concrete tasks. Fill tasks.md with file-level execution plan. Use after design alignment."
metadata:
  author: frostime
  version: 3.0.0
---

# SSPEC Plan

Turn the approved design into a concrete, file-level execution plan in tasks.md.

---

## Output Contract

If tasks.md does not yet exist, scaffold it first:

```bash
sspec change scaffold tasks <change>
```

When this phase ends, tasks.md MUST contain:
- Phases with file-level tasks (single/sub) OR milestones (root)
- Verification criteria for each phase
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
| Defines interfaces, data model, logic | Lists file-level actions + verification |
| Explains *how it should work* | Tells agent *what to do next* |
| `get_cached_user(id) -> Optional[User]` | `Create cache.py — implement interface per spec` |

- ✅ "Implement Fix A per spec"
- ✅ "Create handler following the data flow in design.md"
- ❌ Re-listing all function signatures
- ❌ Re-describing the algorithm

## Single/Sub vs Root

| change-type | tasks.md form |
|------------|---------------|
| `single` / `sub` | Phase-based, file-level tasks (<2h each) |
| `root` | Milestone-based, one entry per sub-change (no file-level detail) |

Root rules: no file-level tasks; each phase has Deliverable + Sub-change link; root stays active until all sub-changes complete.

## Verification

Each phase MUST have explicit verification criteria:
- What to check (test commands, expected output, manual verification)
- How to know it's done (not "it works" but specific criteria)

## Exit: @align Report

Present the task breakdown (phases, total tasks, key verification criteria). This is a `report`, not a hard gate — continue to `sspec-implement` unless the user interrupts.

📚 Examples: [examples.md](./examples.md)
