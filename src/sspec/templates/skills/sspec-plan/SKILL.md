---
name: sspec-plan
description: "Break design into concrete tasks. Fill tasks.md with file-level execution plan. Use after design alignment."
metadata:
  author: frostime
  version: 2.2.1
---

# SSPEC Plan

Turn the approved design (spec.md B) into a concrete, file-level execution plan in tasks.md.

---

## Workflow

```
1. Read spec.md frontmatter + B (approved design)
2. Choose planning mode: single/sub vs root
3. Fill tasks.md (phases + tasks OR milestones)
4. Update Progress section
5. @align with a report, then continue to implementation
```

## Step 1: Choose Planning Mode

Determine mode from `spec.md` frontmatter `change-type`:

| change-type | tasks.md form | Example |
|------------|---------------|---------|
| `single` / `sub` | Phase-based, file-level tasks (<2h each) | See [examples.md - Medium tasks.md](./examples.md#medium-tasksmd) |
| `root` | Milestone-based, one entry per sub-change (no file-level detail) | See [examples.md - Root tasks.md](./examples.md#root-tasksmd) |

Start by mimicking the closest example, then edit.

| Situation | Copy from |
|----------|-----------|
| Single phase, few files | [examples.md - Simple tasks.md](./examples.md#simple-tasksmd) |
| Multi-phase / cross-module | [examples.md - Medium tasks.md](./examples.md#medium-tasksmd) |
| Root change | [examples.md - Root tasks.md](./examples.md#root-tasksmd) |
| Unsure about B vs tasks boundary | [examples.md - Complete Flow: B -> tasks.md](./examples.md#complete-flow-b--tasksmd) |

If your Markdown viewer doesn't jump to `#...` anchors, treat them as search keys:
open `examples.md` and search for the heading text in the link label, or use `rg` to search for the `#...` fragment.

## Step 2A: Single/Sub Planning (Phases + File-Level Tasks)

Keep the generated `tasks.md` frontmatter as-is. `change` MUST match `spec.md` `name`.

### Standards

Each task SHOULD be:
- **Specific**: names exact file path + action
- **Small**: <2 hours
- **Independently testable**: has an obvious check

### Phase Structure

Follow the `tasks.md` template (`@RULE` block) and/or copy from [examples.md](./examples.md).
Use: ⏳ pending | 🚧 in progress | ✅ done

### Verification

Each phase MUST have explicit verification criteria:
- What to check (test commands, expected output, manual verification)
- How to know it's done (not "it works" but specific criteria)

### Reference Section B, Don't Repeat

tasks.md references spec.md B's design. Don't re-describe interfaces or algorithms.

| spec.md B (design) | tasks.md (plan) |
|---|---|
| Defines interfaces, data model, logic | Lists file-level actions + verification |
| Explains *how it should work* | Tells agent *what to do next* |
| `get_cached_user(user_id) -> Optional[User]` | `Create cache.py — implement interface per spec.md B` |

- ✅ "Implement Tool Interface per spec.md B"
- ✅ "Create handler following the data flow in spec.md B"
- ❌ Re-listing all function signatures
- ❌ Re-describing the algorithm

📚 Complete B → tasks.md flow example: [examples.md](./examples.md#complete-flow-b--tasksmd)

## Step 2B: Root Planning (Milestones)

Root tasks.md is milestone-level. Each phase maps to a sub-change.
Use [examples.md](./examples.md#root-tasksmd) as the reference format.

Rules of thumb:
- No file-level tasks in root tasks.md
- Each phase MUST include **Deliverable** + **Sub-change** link placeholder
- Root stays active until all sub-changes complete

## Step 3: Progress Tracking

After filling tasks, update the Progress section (overall + per-phase).
Start at 0% unless work already began.

## Exit: @align Report

Present the task breakdown:
- Number of phases and total tasks
- Key verification criteria
- Estimated scope

This is a `report`, not a hard gate. After summarizing the plan, continue to `sspec-implement` unless the user interrupts or the plan itself reveals a real decision that needs a `gate`.

---

## References

| When | Load |
|------|------|
| Need concrete tasks.md examples (Simple / Medium / Root) | [examples.md](./examples.md) |
| Need B → tasks.md complete flow example | [examples.md → Complete Flow](./examples.md#complete-flow-b--tasksmd) |
