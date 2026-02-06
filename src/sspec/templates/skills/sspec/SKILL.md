---
name: sspec
description: Quality standards and workflows for SSPEC changes. Covers single/multi-change assessment, document standards, reference field usage, and edge cases. Consult when starting changes, handling complex scenarios, or unsure about quality standards.
metadata:
  author: frostime
  version: 7.0.0
---

# SSPEC Skill

**When to consult**:
- Starting a new change → Complexity assessment (single vs multi-change)
- Filling spec.md / tasks.md / handover.md → Quality standards below
- Handling edge cases → Blockers, rejection (@argue), multi-change coordination
- Using reference field or reference/ directories

**Note**: Core protocol (directives, status transitions, cold start) is in AGENTS.md. This SKILL provides quality depth.

---

## Change Complexity Assessment

**FIRST DECISION**: Single change or multi-change?

### Single Change (default)

Use when ALL of:
- **Time**: Completable in ≤1 week
- **Scope**: Modifies ≤15 files, focuses on one subsystem
- **Tasks**: ≤20 actionable tasks
- **Risk**: Low, changes are reversible

**Examples**: Bug fix, add single API endpoint, refactor one module, update docs.

### Multi-Change (complex projects)

Use when ANY of:
- **Time**: >1 week estimated
- **Scope**: Touches multiple subsystems or >15 files
- **Tasks**: >20 tasks, or phases with distinct milestones
- **Risk**: High, requires staged rollout or extensive testing

**Pattern**: Create **root change** for coordination + multiple **sub-changes** for execution.

**When uncertain**: Use `sspec ask` to consult user on splitting approach.

---

## Multi-Change Management

### Structure

```
Root change (coordinator):
  - changes/<root-name>/
    ├── spec.md         # Overall vision, phases overview
    ├── tasks.md        # High-level milestones
    ├── reference/      # Shared design docs, architecture
    └── script/         # Shared migration scripts

Sub-changes (execution):
  - changes/<sub-name>/
    ├── spec.md         # Focused scope, reference links to root
    ├── tasks.md        # Specific tasks for this phase
    └── handover.md
```

### Workflow

1. **Create root change**: Design overall approach, break into phases
2. **Create first sub-change**: Link to root via `reference` field
3. **Complete → Archive → Next**: Archive sub-change, create next
4. **Root stays active**: Until all sub-changes complete
5. **Final archive**: Archive root when everything done

### Reference Linking

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

---

## Document Quality Standards

### spec.md

| Section | Requirement | ❌ Fail | ✅ Pass |
|---------|-------------|---------|---------|
| A. Problem | Quantified impact | "Need to refactor" | "Auth takes 5s → 12% conversion drop" |
| B. Solution | Approach + rationale | "Use caching" | "JWT + Redis: DB→memory, <100ms target" |
| C. Implementation | File-level tasks | "Modify auth files" | "`src/auth/jwt.py` — create refresh_token()" |
| D. Blockers | Dated, actionable | "Waiting on DevOps" | "Blocker (01-27): Need Redis host:port" |

**Section C format**:
```markdown
### Phase 1: Infrastructure
- `src/cache/redis.py` — create, connection pool setup
- `requirements.txt` — modify, add redis>=4.0

### Phase 2: Core Logic
- `src/auth/jwt.py` — create, token generation/validation
- `src/auth/middleware.py` — modify, add cache-first lookup

### Risks & Dependencies
- Redis server required (coordinate with DevOps)
```

### tasks.md

| Criterion | Standard |
|-----------|----------|
| Granularity | Each task <2h, independently testable |
| Verification | Each phase has explicit pass criteria |
| Progress tracking | Update after completing EACH task |

**Format**:
```markdown
### Phase 1: Infrastructure ✅
- [x] Add redis dependency to `requirements.txt`
- [x] Create connection pool in `src/cache/redis.py`
**Verification**: `pytest tests/test_cache.py` all pass

### Phase 2: Core Logic 🚧
- [x] Implement cache-first lookup in `src/auth/middleware.py`
- [ ] Create token refresh in `src/auth/jwt.py`
**Verification**: Auth endpoint responds in <100ms
```

### handover.md

| Field | Purpose | Bad Example | Good Example |
|-------|---------|-------------|--------------|
| Background | One-sentence overview | "Doing auth" | "JWT+Redis cache to reduce auth from 5s to <1s" |
| Accomplished | What's done this session | "Made progress" | "Phase 1 complete: redis pool + middleware integration" |
| Next Steps | 1-3 specific file actions | "Continue" | "1. Code jwt.py:refresh_token() 2. Add token expiry tests" |
| Conventions | Patterns discovered | (empty) | "Cache key format: `auth:{user_id}`, TTL: 900s" |

**Quality test**: New Agent can resume in <30 seconds?

---

## Optional Directories

### reference/ (Design Iteration)

Use for **complex changes** needing design iteration before implementation.

| Use Case | File Example |
|----------|--------------|
| Architecture exploration | `design-draft.md` |
| API alternatives comparison | `api-options.md` |
| Research notes | `research.md` |

**Workflow**: Draft in reference/ → Iterate via `sspec ask` → Finalize into spec.md A/B/C → Keep for record or discard.

**Skip for**: Simple bug fixes, well-understood features.

### script/ (One-Off Tools)

Migrations, test data generators, analysis tools for this change.

**Lifecycle**: Created in DOING, may promote to project-level if reusable, otherwise archived with change.

---

## Frontmatter Reference Field

Track relationships: request → change, sub-change ↔ root change, change → spec-doc.

```yaml
reference:
  - source: "requests/26-02-05T14-00_add-auth.md"  # Relative to .sspec/
    type: "request"       # See type list below
    note: "Original feature proposal"  # Optional
```

### Valid Reference Types

| Type | Meaning | Direction |
|------|---------|-----------|
| `request` | Originating request | change → request |
| `root-change` | Parent coordinator | sub-change → root |
| `sub-change` | Child execution unit | root → sub-change |
| `doc` | Related spec-doc | change → spec-doc |

### Auto-populated
- `sspec change new --from <req>`: Creates change with `request` reference
- `sspec request link <req> <chg>`: Updates both request and change

---

## Edge Cases

### Partial Blockers

Some tasks blocked, others can proceed.

```
IF blocked tasks are dependencies for remaining:
    → Status = BLOCKED, document in spec.md Section D
ELSE IF blocked tasks are non-critical:
    → Continue other tasks, move blocked to end, document in spec.md D
ELSE:
    → Consider splitting into two changes
```

### REVIEW Across Sessions

- Keep status = REVIEW
- Update handover.md: "Awaiting user review since <date>"
- Can start other changes meanwhile
- Next session: Prompt user for review result first

### Mid-Flight Rejection (@argue)

User says "this isn't right" during DOING.

1. **STOP** immediately — don't continue current task
2. **Clarify** rejection scope:
   - Implementation detail → Update tasks.md only
   - Design decision → Revise spec.md Section B + tasks.md
   - Requirement itself → Revise spec.md Section A, mark PIVOT in Section D
3. **Re-plan**: If scope changed significantly, transition DOING → PLANNING
4. **Wait**: Get explicit user approval before resuming

### Multiple Active Changes

Limit to ≤2 changes in DOING status simultaneously.

**Context switching**:
1. `@handover` on current change
2. `@change <other>` to switch
3. Read `<other>/handover.md` before acting

### Design Iteration Loop

When spec.md keeps getting revised in PLANNING:

1. Version current spec: `reference/spec-v1.md`
2. Brainstorm in `reference/design-exploration.md`
3. Iterate with user via `sspec ask`
4. Write final clean version to spec.md

---

## Anti-Patterns

| Bad Practice | Why It Fails | Correct Approach |
|--------------|--------------|------------------|
| Skip @handover | Next session re-discovers context | **ALWAYS** handover before ending |
| Mark `[x]` without testing | False progress, hidden bugs | Done = coded **AND** verified |
| No file paths in spec.md C | Agent guesses wrong files | List specific paths per task |
| Stay DOING when blocked | Waste time on workarounds | BLOCKED immediately + document |
| Skip REVIEW status | No user validation | DOING → REVIEW → DONE |
| Batch progress updates | Lose track of actual state | Update after **each** task |
| Over-use reference/ | Wasted effort on simple changes | Reserve for complex design |
| Forget reference field | Lost traceability | Use CLI auto-link or add manually |

---

## Checklists

### Starting New Change

- [ ] Assessed: Single vs multi-change?
- [ ] If multi-change: Created root change first?
- [ ] Spec.md Section A: Problem quantified with metrics?
- [ ] Spec.md Section B: Solution approach + rationale stated?
- [ ] Spec.md Section C: File-level task breakdown provided?
- [ ] Tasks.md: Each task <2h, has verification criteria?
- [ ] Handover.md: Initial context documented?
- [ ] Reference field: Linked to originating request (if applicable)?

### Before Transitioning to REVIEW

- [ ] All tasks marked `[x]` in tasks.md?
- [ ] All phase verification criteria met?
- [ ] Handover.md reflects completion?
- [ ] Spec.md Section D: No undocumented blockers?
- [ ] Code tested and passing?

### Before @handover (End of Session)

- [ ] Handover.md: "Accomplished" updated?
- [ ] Handover.md: "Next Steps" clear (1-3 file-level actions)?
- [ ] Handover.md: "Conventions" updated if new patterns found?
- [ ] Tasks.md: Progress percentage updated?
- [ ] Spec.md: Status accurate?
