---
skill: sspec
version: 5.0.0
description: Quality standards and edge cases for SSPEC workflow. Consult when writing change documents or handling complex scenarios.
---

# SSPEC Skill

**When to consult**:
- Writing spec.md / tasks.md / handover.md
- Handling edge cases (partial blockers, multi-change, mid-flight rejection)
- Using reference/ or script/ directories
- Unsure about quality standards

**Note**: Core protocol is in AGENTS.md. This SKILL covers depth and edge cases.

---

## Document Quality Standards

### spec.md

| Section | Quality Bar | ❌ Fail | ✅ Pass |
|---------|-------------|---------|---------|
| A. Problem | Quantified pain | "Need to refactor" | "Auth takes 5s, 12% conversion drop" |
| B. Solution | Approach + rationale | "Use caching" | "JWT + Redis: DB→memory lookup" |
| C. Implementation | File-level breakdown | "Modify auth files" | "`src/auth/jwt.py` — add refresh_token()" |
| D. Blockers | Dated, actionable | "Waiting on DevOps" | "Blocker (01-27): Need Redis host:port" |

**Section C format**:
```markdown
### Phase 1: Infrastructure
- `src/cache/redis.py` — create, connection pool
- `requirements.txt` — modify, add redis>=4.0

### Phase 2: Core Logic
- `src/auth/jwt.py` — modify, add refresh_token()
- `src/auth/middleware.py` — modify, cache-first lookup

### Risks & Dependencies
- Redis server required (DevOps)
```

### tasks.md

| Criterion | Requirement |
|-----------|-------------|
| Granularity | Each task <2h, independently verifiable |
| Verification | Each phase has explicit criteria |
| Progress | Update after EACH task, not batched |

**Format**:
```markdown
### Phase 1: Infrastructure ✅
- [x] Add redis dependency `requirements.txt`
- [x] Create connection pool `src/cache/redis.py`
**Verification**: `pytest tests/test_cache.py` passes

### Phase 2: Core Logic 🚧
- [x] Cache-first lookup `src/auth/middleware.py`
- [ ] Token refresh `src/auth/jwt.py`
**Verification**: Auth response <100ms
```

### handover.md

| Field | ❌ Bad | ✅ Good |
|-------|--------|---------|
| Background | "Doing auth" | "JWT+Redis cache, target <1s auth" |
| Accomplished | "Made progress" | "Phase 1 done: redis pool + middleware" |
| Next Steps | "Continue" | "1. Implement jwt.py:refresh_token() 2. Add tests" |
| Conventions | (empty) | "Key format: `auth:{user_id}`, TTL: 900s" |

**Quality test**: Can a new Agent start coding in <30 seconds?

---

## Auxiliary Directories

```
.sspec/changes/<n>/
├── spec.md, tasks.md, handover.md  # Required
├── reference/                       # Optional: design workspace
└── script/                         # Optional: one-off tooling
```

### reference/ — Design Workspace

Use for complex changes where design needs iteration before committing to spec.md.

| Use Case | Example File |
|----------|--------------|
| Architecture exploration | `design-draft.md` |
| API alternatives | `api-options.md` |
| Research notes | `research.md` |
| Diagrams | `architecture.mmd` |

**Workflow**:
1. PLANNING phase: Write drafts in reference/
2. Iterate with user via `sspec ask`
3. Finalize: Distill into spec.md Sections A/B/C
4. Keep or discard reference/ after finalization

**When to use**: Architectural decisions, multiple valid approaches, verbose design.

**When NOT to use**: Simple bug fixes, well-understood features.

### script/ — Change-Specific Tooling

One-off scripts and data specific to this change: migrations, test fixtures, analysis scripts.

Lifecycle: Created during DOING, may be promoted to project-level if reusable, archived with change.

---

## Edge Cases

### Partial Blockers

Some tasks blocked, others can continue.

```
IF blocked tasks are dependencies for remaining:
    → Status = BLOCKED, document in spec.md Section D
ELSE IF blocked tasks are non-critical:
    → Continue other tasks, document blocker, move blocked to end
ELSE:
    → Split into two changes: one blocked, one active
```

### REVIEW Spanning Sessions

- Keep status = REVIEW
- Update handover: "Awaiting user verification since <date>"
- Can work on other changes meanwhile
- Next session: Prompt user for review result

### Mid-Flight Rejection (@argue)

User says "this isn't what I wanted" during DOING.

1. STOP immediately
2. Determine rejection scope:
   - Detail level → Revise tasks.md only
   - Design level → Revise spec.md Section B + tasks.md
   - Requirement level → Revise spec.md Section A, add PIVOT marker
3. Consider: DOING → PLANNING if scope changed significantly
4. Wait for explicit approval before resuming

### Multiple Changes Simultaneously

**Rule**: Avoid >2 changes in DOING status.

Before switching:
1. Run `@handover` on current change
2. Run `@change <other>` to switch
3. Read other change's handover.md before any action

### Design Iteration

When spec.md keeps getting revised:

1. Move current spec.md content to reference/spec-v1.md
2. Create reference/design-exploration.md for new ideas
3. Iterate with user via `sspec ask`
4. Once stable: Write final version to spec.md

---

## Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Skip handover | Next session wastes time | ALWAYS `@handover` at session end |
| Mark `[x]` without testing | False progress | Done = implemented + verified |
| No file-level breakdown | Agent guesses what to modify | spec.md Section C MUST list files |
| Stay DOING when blocked | Waste time on workarounds | Change to BLOCKED immediately |
| DOING → DONE | Skip user validation | MUST go through REVIEW |
| Batch progress updates | Lose track | Update tasks.md after EACH task |
| Over-engineering reference/ | Wastes time on simple changes | Only use for complex designs |

---

## Checklists

### New Change
- [ ] Section A: Problem quantified with metrics
- [ ] Section B: Solution approach + why this over alternatives
- [ ] Section C: Every task maps to specific file
- [ ] tasks.md: Each task <2h with verification
- [ ] handover.md: Initial context set

### Before REVIEW
- [ ] All tasks `[x]`
- [ ] All verification criteria met
- [ ] handover.md reflects completion
- [ ] No undocumented blockers
