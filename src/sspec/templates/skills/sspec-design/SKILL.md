---
name: sspec-design
description: "Assess scale, create change, fill spec.md, align with user. Use after research when ready to define the solution."
metadata:
  author: frostime
  version: 2.0.0
---

# SSPEC Design

Define the problem and design the solution. Create the change. Align with user before planning.

---

## Workflow

```
1. Assess scale → micro / single / multi
2. Create change (CLI)
3. Fill spec.md
4. @ask user for alignment
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

## Step 3: Fill spec.md

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

**What to include in B**: Interfaces, data models, key algorithms, design rationale.
**What NOT to include**: Execution order (that's tasks.md), file-level task lists (tasks.md).

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

Each sub-change then goes through its own design → plan → implement → review cycle.

## Step 4: @ask for Alignment (MANDATORY)

**Never skip this step.** Present the design to user for confirmation:

- Problem statement summary
- Proposed approach and rationale
- Key design decisions
- (Root) Phase breakdown

Wait for user approval before proceeding to `sspec-plan`.

After user confirms → transition status `PLANNING → DOING` in spec.md frontmatter.
