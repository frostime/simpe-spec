---
name: plan-root-change
desc: Plan a root change tasks.md — milestone-level, one entry per sub-change.
---

Root `tasks.md` tracks milestones only. It **must not** contain file-level tasks — those belong in each sub-change's `tasks.md`.

## Structure

Each phase maps to one sub-change:

```markdown
### Phase 1: <name> ⏳
- [ ] Sub-change created and linked: `.sspec/changes/<path>`
**Deliverable**: <what this sub-change produces>
**Depends On**: —

### Phase 2: <name> ⏳
- [ ] Sub-change created and linked: `.sspec/changes/<path>`
**Deliverable**: <what this sub-change produces>
**Depends On**: Phase 1
```

## Rules

- Root stays `DOING` until all sub-changes reach `DONE`
- Track real-time sub-change progress in `handover.md` under `Sub-Change Status (Volatile Snapshot)`
- Mark a phase `[x]` only after the corresponding sub-change is archived
- Never put implementation detail in root tasks.md — keep it milestone-only

📚 Full example: `sspec-plan` SKILL → `examples.md` → Root tasks.md section
