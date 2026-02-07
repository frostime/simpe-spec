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

📋 For quick checklists at specific checkpoints → See [references/checklists.md](./references/checklists.md)

---

## Change Complexity Assessment

**FIRST DECISION**: Single change or multi-change?

### No Change Needed (micro)

Use when ALL of:
- **Scope**: ≤3 files
- **Time**: ≤30 minutes
- **Complexity**: No design decisions, obvious implementation

**Action**: Track in request file or do directly. No change ceremony.

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

**Pattern**: Create **root change** (`sspec change new <n> --root`) for coordination + multiple **sub-changes** for execution.

**When uncertain**: Use `sspec ask` to consult user on splitting approach.

---

## Multi-Change Management

### Root vs Sub-Change

| Aspect | Root Change | Sub-Change |
|--------|------------|------------|
| Template | `--root` flag → phase-level | Default → file-level |
| spec.md Section C | Phase/sub-change breakdown | File-level task breakdown |
| tasks.md | Milestones (one per sub-change) | Atomic tasks (<2h each) |
| handover.md | Sub-change status tracking | File-level next steps |
| Lifecycle | Active until all subs complete | Normal: PLANNING→DONE |

### Structure

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

### Workflow

1. **Create root**: `sspec change new <n> --root` → design phases
2. **Create sub-change**: `sspec change new <sub-n>` → link to root via `reference`
3. **Execute sub-change**: Normal PLANNING→DOING→REVIEW→DONE cycle
4. **Archive sub-change → create next**: Repeat for each phase
5. **Archive root**: When all sub-changes complete

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

### tasks.md

| Criterion | Standard |
|-----------|----------|
| Granularity | Each task <2h, independently testable (sub/single); milestone-level (root) |
| Verification | Each phase has explicit pass criteria |
| Progress tracking | Update after completing EACH task |

### handover.md

| Field | Purpose | Bad Example | Good Example |
|-------|---------|-------------|--------------|
| Background | One-sentence overview | "Doing auth" | "JWT+Redis cache to reduce auth from 5s to <1s" |
| Accomplished | What's done this session | "Made progress" | "Phase 1 complete: redis pool + middleware integration" |
| Next Steps | 1-3 specific actions | "Continue" | "1. Code jwt.py:refresh_token() 2. Add token expiry tests" |
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
| Use file-level tasks in root | Root is coordinator, not executor | Use milestone-level tasks |
