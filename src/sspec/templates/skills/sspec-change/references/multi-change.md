# Multi-Change Coordination

Patterns for projects that need a root change + sub-changes. Load when Assess Scale → Multi.

---

## Root vs Sub

| Aspect | Root Change | Sub-Change |
|--------|------------|------------|
| Create | `sspec change new <n> --root` | `sspec change new <n>` |
| spec.md C | Phase/sub-change breakdown | File-level task breakdown |
| tasks.md | Milestones (one per sub-change) | Atomic tasks (<2h each) |
| handover.md | Sub-change status tracking | File-level next steps |
| Lifecycle | Active until all subs complete | Normal: PLANNING→DONE |

## Structure

```
changes/<root>/
├── spec.md          # Overall vision (change-type: root)
├── tasks.md         # Milestones per sub-change
├── handover.md      # Sub-change status tracking
├── reference/       # Shared design docs
└── script/          # Shared scripts

changes/<sub>/
├── spec.md          # Focused scope (change-type: sub)
├── tasks.md         # File-level tasks
├── handover.md
└── reference/       # Design docs for complex change task
```

## Workflow

1. `sspec change new <n> --root` → design phases in spec.md C
2. `sspec change new <sub>` → link to root via reference field
3. Execute sub: normal PLANNING→DOING→REVIEW→DONE
4. Archive sub → create next sub
5. All subs done → archive root

## Reference Linking

Sub → Root:
```yaml
reference:
  - source: "changes/<root>"
    type: "root-change"
    note: "Phase 1 of auth overhaul"
```

Root → Sub:
```yaml
reference:
  - source: "changes/<sub>"
    type: "sub-change"
```

## Archiving Root

Before archiving root change:

- [ ] All sub-changes archived?
- [ ] Root tasks.md: all milestones `[x]`?
- [ ] Valuable coordination notes preserved in reference/?
- [ ] Linked spec-docs up to date?

## Pitfalls

| Mistake | Fix |
|---------|-----|
| File-level tasks in root | Root is coordinator — milestone-level only |
| Skip root, jump to subs | Root provides vision and phase coordination |
| Forget to link root ↔ sub | Use reference field in both directions |
| Archive root before subs done | Root stays active until all subs complete |
