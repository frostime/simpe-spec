---
skill: sspec
version: 4.1.0
description: Quality standards and edge cases for SSPEC workflow. Consult when writing change documents or handling complex scenarios.
---

# SSPEC Skill

**When to consult**:
- Writing spec.md / tasks.md / handover.md for the first time
- Using reference/ or script/ directories
- Handling edge cases (partial blockers, multi-change, mid-flight rejection)
- Unsure about quality standards

**Note**: Basic rules (status transitions, directives, edit markers) are in AGENTS.md. This SKILL covers quality depth.

---

## Document Quality Standards

### spec.md

| Section | Quality Bar | ❌ Fail | ✅ Pass |
|---------|-------------|---------|---------|
| A. Problem | Quantified pain point | "Need to refactor" | "Auth takes 5s, 12% conversion drop" |
| B. Solution | Approach + rationale | "Use caching" | "JWT + Redis: DB→memory lookup" |
| C. Implementation | File-level breakdown | "Modify auth files" | "`src/auth/jwt.py` — add refresh_token()" |
| D. Blockers | Dated, actionable | "Waiting on DevOps" | "Blocker (01-27): Need Redis host:port from DevOps" |

**Section C format**:
```markdown
### Phase 1: Infrastructure
- `src/cache/redis.py` — create, connection pool
- `requirements.txt` — modify, add redis>=4.0

### Phase 2: Core Logic
- `src/auth/jwt.py` — modify, add refresh_token()
- `src/auth/middleware.py` — modify, cache-first lookup
```

### tasks.md

| Criterion | Requirement |
|-----------|-------------|
| Granularity | Each task <2h, independently executable |
| Verification | Each phase has explicit verification criteria |
| Progress | Updated after EACH task, not batched |

**Task format**:
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

| Field | Bad | Good |
|-------|-----|------|
| Background | "Doing auth" | "JWT+Redis cache, target <1s auth" |
| Accomplished | "Made progress" | "Phase 1 done: redis pool + middleware" |
| Next steps | "Continue" | "1. Implement jwt.py:refresh_token() 2. Add tests" |
| Conventions | (empty) | "Key format: `auth:{user_id}`, TTL: 900s" |

**Quality test**: Can a new Agent start coding in <30 seconds?

---

## Change Auxiliary Files

Beyond the core trio (spec.md, tasks.md, handover.md), changes can include optional directories:

```
.sspec/changes/<n>/
├── spec.md, tasks.md, handover.md  # Required
├── reference/                       # Optional: design workspace
└── script/                         # Optional: tooling
```

### reference/ — Design Workspace

**Purpose**: Pre-finalization exploration space. Use for complex changes where design needs iteration before committing to spec.md.

| Use Case | Example File | Content |
|----------|--------------|---------|
| Architecture exploration | `design-draft.md` | Multiple approaches with pros/cons |
| API design | `api-options.md` | Endpoint alternatives, request/response shapes |
| Research notes | `research.md` | External docs, library comparisons |
| Diagrams | `architecture.mmd` | Mermaid/PlantUML source |
| User feedback | `feedback-log.md` | Accumulated clarifications from sspec ask |

**Workflow**:
```
1. PLANNING phase: Write drafts in reference/
2. Iterate with user via sspec ask
3. Finalize: Distill into spec.md Sections A/B/C
4. Keep or discard: reference/ can stay for context or be cleaned up
```

**When to use reference/**:
- Change involves architectural decisions
- Multiple valid approaches need comparison
- User feedback needs accumulation before finalizing
- Design is too verbose for spec.md

**When NOT to use**:
- Simple bug fixes
- Well-understood features
- Changes with clear requirements from start

### script/ — Change-Specific Tooling

**Purpose**: One-off scripts and data specific to this change.

| Use Case | Example File | Content |
|----------|--------------|---------|
| Data migration | `migrate-v2.py` | Schema migration script |
| Test data | `fixtures.json` | Mock data for testing |
| Environment setup | `setup-local.sh` | Dev environment bootstrap |
| Analysis | `analyze-perf.py` | Performance measurement |

**Lifecycle**:
- Created during DOING phase as needed
- May be promoted to project-level if reusable
- Archived with change via `sspec change archive`

**Difference from project scripts**:
- `scripts/` in change = temporary, change-specific
- Project-level scripts = permanent, shared tooling

---

## Edge Cases

### Partial Blockers

Some tasks blocked, others can continue.

**Decision tree**:
```
IF blocked tasks are dependencies for remaining tasks:
    → Status = BLOCKED, document in spec.md Section D
ELSE IF blocked tasks are non-critical:
    → Continue with other tasks, document blocker
    → Move blocked tasks to end of task list
ELSE:
    → Split into two changes: one blocked, one active
```

### REVIEW Spanning Multiple Sessions

```
- Keep status = REVIEW
- Update handover: "Awaiting user verification since <date>"
- Can work on other changes meanwhile
- On next session: Prompt user for review result
```

### Mid-Flight Rejection

User says "this isn't what I wanted" during DOING.

```
1. STOP immediately
2. Trigger @argue directive
3. Determine rejection scope:
   - Detail level → Revise tasks.md only
   - Design level → Revise spec.md Section B + tasks.md
   - Requirement level → Revise spec.md Section A, add PIVOT marker
4. Status: Consider DOING → PLANNING if scope changed
5. WAIT for explicit approval before resuming
```

### Multiple Changes DOING Simultaneously

**Rule**: Avoid >2 changes in DOING status.

```
Before switching changes:
1. Run @handover on current change
2. Run @change <other> to switch context
3. Read other change's handover.md before any action
```

### Design Iteration in reference/

When spec.md keeps getting revised:

```
1. Move current spec.md content to reference/spec-v1.md
2. Create reference/design-exploration.md for new ideas
3. Iterate with user via sspec ask
4. Once stable: Write final version to spec.md
5. Optional: Keep reference/ versions for decision history
```

---

## Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Skip handover | Next session wastes 30min | ALWAYS run @handover at session end |
| Mark `[x]` without testing | False progress | "Done" = implemented + verified |
| No file-level breakdown | Agent guesses what to modify | spec.md Section C MUST list files |
| Stay DOING when blocked | Waste time on workarounds | Change to BLOCKED immediately |
| DOING → DONE | Skip user validation | MUST go through REVIEW |
| Batch progress updates | Lose track | Update tasks.md after EACH task |
| Append to REPLACE-FOR-EDIT | Creates duplication | Replace entire section |
| Over-engineering reference/ | Wastes time on simple changes | Only use for complex designs |

---

## Checklist

### New Change
- [ ] Section A: Problem quantified with metrics
- [ ] Section B: Solution approach + why this over alternatives
- [ ] Section C: Every task maps to specific file
- [ ] tasks.md: Each task <2h with verification
- [ ] handover.md: Initial context set
- [ ] Complex design? Consider using reference/

### Before REVIEW
- [ ] All tasks `[x]`
- [ ] All verification criteria met
- [ ] handover.md reflects completion
- [ ] No undocumented blockers
- [ ] scripts/ cleaned up or documented if kept

