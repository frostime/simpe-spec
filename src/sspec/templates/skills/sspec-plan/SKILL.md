---
name: sspec-plan
description: "Break design into concrete tasks. Fill tasks.md with file-level execution plan. Use after design alignment."
metadata:
  author: frostime
  version: 2.1.0
---

# SSPEC Plan

Turn the approved design (spec.md B) into a concrete, file-level execution plan in tasks.md.

---

## Workflow

```
1. Read spec.md B (approved design)
2. Break into phases + file-level tasks
3. Fill tasks.md
4. @ask user for final review
```

## Task Standards

### tasks.md Frontmatter (MANDATORY)

Single/sub change:

```yaml
---
change: "<change-name>"
updated: ""
---
```

Root change:

```yaml
---
change: "<change-name>"
change-type: root
updated: ""
---
```

Keep `change` exactly aligned with `spec.md` `name`.

### Granularity

| Change Type | Task Level | Example |
|-------------|-----------|---------|
| Single / Sub | File-level, <2h each | `- [ ] Create src/auth/jwt.py — refresh_token()` |
| Root | Milestone-level (one per sub-change) | `- [ ] Phase 1 sub-change completed` |

Each task should be:
- **Independently testable** — can verify without completing other tasks
- **Specific** — mentions exact file path and what to do
- **Small** — <2 hours of work

### Phase Structure

```markdown
### Phase 1: <name> ⏳
- [ ] Task description `path/file.py`
- [ ] Task description `path/file.py`
**Verification**: <how to verify this phase>

### Phase 2: <name> ⏳
- [ ] Task description `path/file.py`
**Verification**: <how to verify>
```

### Phase Emoji

| Emoji | Meaning |
|-------|---------|
| ⏳ | Pending — not started |
| 🚧 | In progress — actively working |
| ✅ | Done — all tasks complete and verified |

### Verification

Each phase MUST have explicit verification criteria:
- What to check (test commands, expected output, manual verification)
- How to know it's done (not "it works" but specific criteria)

## Reference Section B, Don't Repeat

tasks.md references spec.md B's design. Don't re-describe interfaces or algorithms.

- ✅ "Implement Tool Interface per spec.md B"
- ✅ "Create handler following the data flow in spec.md B"
- ❌ Re-listing all function signatures
- ❌ Re-describing the algorithm

## Root Change Planning

For root changes, tasks.md contains milestones, not file-level tasks:

```markdown
### Phase 1: Auth Backend ⏳
- [ ] Sub-change created and linked
- [ ] Sub-change completed and archived
**Deliverable**: JWT auth with <1s response time
**Sub-change**: (link when created)
```

The active sub-change gets its own tasks.md with file-level detail.

## Progress Tracking

Update the Progress section after filling tasks:

```markdown
## Progress

**Overall**: 0%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 0% | ⏳ |
| Phase 2 | 0% | ⏳ |
```

## Exit: @ask User Review (MANDATORY)

Present the task breakdown to user:
- Number of phases and total tasks
- Key verification criteria
- Estimated scope

Wait for user approval before starting `sspec-implement`.
