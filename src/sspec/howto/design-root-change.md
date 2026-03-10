---
name: design-root-change
desc: Design a root change spec.md — phase decomposition and sub-change coordination rules.
---

Root `spec.md` describes overall problem scope and phase decomposition. It does **not** contain file-level interfaces — those belong in each sub-change spec.

## Section structure

**Section A**: Overall problem — full scope across all phases, not a single module.

**Section B**:
- `### Overall Approach` — high-level strategy, delivery order, key constraints.
- `### Phase Overview` — each phase as a named deliverable with scope and dependencies.

```markdown
| Phase | Scope | Depends On |
|-------|-------|------------|
| Phase 1: <name> | <deliverable> | — |
| Phase 2: <name> | <deliverable> | Phase 1 |
```

## Creating sub-changes

After phases are defined, create each sub-change:
```bash
sspec change new <phase-name>
```

Ensure bidirectional references:
- Sub `spec.md`: `reference` entry with `type: root-change` pointing to root path
- Root `spec.md`: `reference` entry with `type: sub-change` pointing to sub path

## Pitfalls

| Mistake | Fix |
|---------|-----|
| File-level tasks in root `tasks.md` | Root = milestones only — file tasks go in sub-change |
| Skip root, jump to sub-changes | Root provides phase vision and coordination |
| Forget bidirectional references | Always link root ↔ sub in both `spec.md` reference fields |
| Archive root before all subs done | Root stays active until every sub reaches DONE |

📚 Full examples: `sspec-design` SKILL → `examples-root.md`
