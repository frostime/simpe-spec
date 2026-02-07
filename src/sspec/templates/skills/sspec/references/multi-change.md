# Multi-Change Management Reference

Patterns for coordinating complex projects that span multiple changes. Load when creating or managing root/sub-change structures.

---

## Root vs Sub-Change

| Aspect | Root Change | Sub-Change |
|--------|------------|------------|
| Template | `--root` flag → phase-level | Default → file-level |
| spec.md Section C | Phase/sub-change breakdown | File-level task breakdown |
| tasks.md | Milestones (one per sub-change) | Atomic tasks (<2h each) |
| handover.md | Sub-change status tracking | File-level next steps |
| Lifecycle | Active until all subs complete | Normal: PLANNING→DONE |

## Structure

```
Root change (coordinator):
  - changes/<root-name>/
    ├── spec.md         # Overall vision, phase overview (change-type: root)
    ├── tasks.md        # Milestones per sub-change
    ├── handover.md     # Sub-change status tracking
    ├── reference/      # Shared design docs
    └── script/         # Shared scripts

Sub-changes (execution):
  - changes/<sub-name>/
    ├── spec.md         # Focused scope (change-type: sub)
    ├── tasks.md        # File-level tasks
    └── handover.md
```

## Workflow

1. **Create root**: `sspec change new <n> --root` → design phases
2. **Create sub-change**: `sspec change new <sub-n>` → link to root via `reference`
3. **Execute sub-change**: Normal PLANNING→DOING→REVIEW→DONE cycle
4. **Archive sub-change → create next**: Repeat for each phase
5. **Archive root**: When all sub-changes complete

## Reference Linking

Sub-change spec.md frontmatter:
```yaml
reference:
  - source: "changes/<root-name>"
    type: "root-change"
    note: "Phase 1 of auth overhaul"
```

Root spec.md can back-link:
```yaml
reference:
  - source: "changes/<sub-name>"
    type: "sub-change"
```

## Anti-Patterns (Multi-Change Specific)

| Bad Practice | Correct Approach |
|--------------|------------------|
| File-level tasks in root change | Root is coordinator — use milestone-level tasks |
| Skip root, jump to sub-changes | Root provides vision and coordination |
| Forget to back-link root ↔ sub | Use reference field in both directions |
| Archive root before all subs done | Root stays active until all subs complete |
