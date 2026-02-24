---
name: sspec-design
description: "Assess scale, create change, fill spec.md, align with user. Use after research when ready to define the solution."
metadata:
  author: frostime
  version: 3.1.0
---

# SSPEC Design

Define the problem and design the solution. Create the change. **Align with user before planning.**

This is a **user-in-the-loop** phase — like review, the user must confirm your design before you proceed. Never auto-advance to planning.

---

## Workflow

```
1. Assess scale → micro / single / multi
2. Create change (CLI)
3. Fill spec.md
4. @ask user for alignment (MANDATORY)
```

## Step 1: Assess Scale

| Scale | Criteria | Action |
|-------|----------|--------|
| **Micro** | ≤3 files, ≤30min, no design decisions, trivially reversible | Do directly. No change needed. Track in request if useful. |
| **Single** | ≤1 week, ≤15 files, one subsystem, ≤20 tasks | Standard change → Step 2 Single |
| **Multi** | >1 week OR >15 files across subsystems OR >20 tasks OR high risk | Root change → Step 2 Root |

**Uncertain?** → `@ask` user about scope/splitting.

## Step 2: Create Change

### Single Path

```bash
sspec change new <name>                        # standalone
sspec change new --from <request>              # from request (auto-link)
sspec change new <name> --from <request>       # explicit name + request link
```

### Root Path (Multi-Change)

```bash
sspec change new <name> --root                 # creates root coordinator
sspec change new <name> --root --from <req>    # root from request
```

Root change creates a coordinator with different templates:
- Root `spec.md`: Phase overview, not file-level detail
- Root `tasks.md`: Milestones, not individual tasks

## Step 2.5: Normalize spec.md Frontmatter (MANDATORY)

Use this schema exactly:

```yaml
---
name: <change-name>
status: PLANNING
type: ""
change-type: single|sub|root
created: <iso-timestamp>
reference: null|[]
---
```

### Sub-Change Must Link Root (Required)

```yaml
change-type: sub
reference:
  - source: "changes/<root-change-dir>"
    type: "root-change"
    note: "Phase <n>: <phase-name>"
```

### Root Should Link Request + Sub-Changes (Bidirectional Tracking)

```yaml
change-type: root
reference:
  - source: "requests/<request-file>.md"
    type: "request"
  - source: "changes/<sub-change-dir>"
    type: "sub-change"
    note: "Phase <n>: <phase-name>"
```

Use workspace-relative paths without `./` prefix.

## Step 3: Fill spec.md

### What Users Care About Most

Users review designs for: **interfaces**, **data types**, **data flow**, and **logic flow**.
Prioritize these in Section B. Abstract hand-waving ("we'll handle it later") erodes trust.

### Single Change

**Section A — Problem Statement**:
- Quantify impact: "[metric] causing [impact]"
- Simple changes: single paragraph
- Complex changes: split "Current Situation" + "User Requirement"

| ❌ Bad | ✅ Good |
|--------|---------|
| "Need to refactor" | "Auth takes 5s → 12% conversion drop" |
| "Improve the UI" | "Form completion rate 23% → target 60%" |

**Section B — Proposed Solution**:

`### Approach`: Core idea (1-3 paragraphs) + why this over alternatives.

`### Key Design`: Scale by complexity:

| Complexity | Design Depth |
|------------|-------------|
| Simple (≤5 files) | Inline in Approach, brief mention |
| Medium (5-15 files) | Sub-sections: `### Interface Design`, `### Data Model`, `### Key Logic` |
| Complex (>15 files) | Detailed design in `reference/design.md`, link from B |

**What MUST appear in B** (by priority):
1. **Interfaces** — function signatures, API contracts, class interfaces
2. **Data types** — models, schemas, type definitions
3. **Data flow** — how data moves through the system (input → transform → output)
4. **Logic flow** — key algorithms, decision trees, state machines
5. **Design rationale** — why this approach over alternatives

**What does NOT belong in B**: Execution order (tasks.md), file-level task lists (tasks.md).

**B vs tasks.md boundary**: B defines *how it should work* (interfaces, data model, logic). tasks.md defines *what to do* (file-level steps, verification). Tasks reference B — e.g. "implement interface per spec.md B" — never copy.

### Section B Example (Medium Complexity)

```markdown
## B. Proposed Solution

### Approach
Add token refresh via middleware. Background refresh prevents expired tokens from blocking requests.

Why middleware: intercepting at HTTP layer avoids modifying every API call site.

### Key Design

#### Interface
- `TokenService.refresh(token: str) -> TokenPair`
- `AuthMiddleware.intercept(request: Request) -> Request`
- `TokenPair = TypedDict('TokenPair', {'access': str, 'refresh': str, 'expires_at': int})`

#### Data Flow
```
Request → AuthMiddleware → check expiry
  → if valid: pass through
  → if expiring (<5min): background refresh + pass through
  → if expired: block, refresh, retry with new token
```

#### Key Logic
Refresh uses sliding window: if token expires within `REFRESH_WINDOW` (default 5min),
trigger background refresh. Concurrent requests share one refresh via lock.
```

### Root Change

**Section A**: Overall problem — full scope, not a single module.

**Section B**:
- `### Overall Approach`: High-level strategy, delivery order
- `### Phase Overview`: Each phase with goal, scope, dependencies

```markdown
- **Phase 1: Auth Backend** — JWT + Redis cache, goal: <1s auth response
- **Phase 2: Auth Frontend** — Login/signup UI, depends on Phase 1
- **Phase 3: Migration** — Migrate existing sessions, depends on Phase 1+2
```

After defining phases → create sub-changes:
```bash
sspec change new <phase-name>    # for each phase, link to root via reference
```

For each sub-change, ensure two-way references:
- Sub `spec.md` has a `reference` item with `type: root-change` pointing to root
- Root `spec.md` appends a `type: sub-change` entry pointing to that sub-change

Each sub-change then goes through its own design → plan → implement → review cycle.

**Multi-change pitfalls**:

| Mistake | Fix |
|---------|-----|
| File-level tasks in root tasks.md | Root tracks milestones only — file tasks go in sub-change |
| Skip root, jump straight to sub-changes | Root provides phase vision and coordination |
| Forget bidirectional references | Always link root ↔ sub in both `spec.md` reference fields |
| Archive root before all subs done | Root stays active until every sub-change is archived |

## Step 4: @ask for Alignment (MANDATORY)

**Never skip this step.** This is a user-in-the-loop confirmation — like review phase, the user must sign off.

Present the design to user for confirmation:
- Problem statement summary
- Proposed approach and rationale
- Key interfaces and data types
- (Root) Phase breakdown

After user confirms design, proceed to `sspec-plan`.
Only after user also approves the task plan, transition status `PLANNING → DOING`.

---

## References

| When | Load |
|------|------|
| Need concrete spec.md examples (Simple / Medium / Complex / Root) | [examples.md](./examples.md) |
| Need B → tasks.md boundary guidance | [examples.md → B → tasks.md Boundary](./examples.md#b--tasksmd-boundary) |
