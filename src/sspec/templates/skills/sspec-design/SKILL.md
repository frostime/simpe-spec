---
name: sspec-design
description: "Assess scale, create change, fill spec.md, align with user. Use after research when ready to define the solution."
metadata:
  author: frostime
  version: 3.2.0
---

# SSPEC Design

Define the problem and design the solution. Create the change. **Align with user before planning.**

This is a **user-in-the-loop** phase — like review, the user must confirm your design before you proceed. Never auto-advance to planning.

---

## Workflow

```
1. Assess scale → micro / single / multi
2. Create change (CLI)
3. Fill spec.md (choose one)
   Type A: Single/Sub change spec.md
   Type B: Root change spec.md
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

## Step 3A: Fill Single/Sub Change spec.md (Type A)

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
| Medium (5-15 files) | Sub-sections: `### Interface Design`, `### Data Flow`, `### Key Logic` (add `### Data Model` if introducing new schemas) |
| Complex (>15 files) | Detailed design in `reference/design.md`, link from B |

**What MUST appear in B** (by priority):
1. **Interfaces** — function signatures, API contracts, class interfaces
2. **Data types** — models, schemas, type definitions
3. **Data flow** — how data moves through the system (input → transform → output)
4. **Logic flow** — key algorithms, decision trees, state machines
5. **Design rationale** — why this approach over alternatives

### Presentation Rules

These rules govern *how* content in Section B must be expressed, not just what to include.
A spec that names the right elements but describes them in prose fails the standard.

**Rule 1 — Code blocks for interfaces**

Any interface, signature, or type definition MUST appear in a fenced typed code block.
Prose is supplementary only.

```python
# ✅ Good — concrete, typed, annotatable
@dataclass
class ChangeRef:
    source: str             # workspace-relative path, no leading ./
    type: RefType           # 'request' | 'root-change' | 'sub-change' | 'doc'
    note: str | None = None  # NEW: optional annotation
```

```
# ❌ Bad — reader must mentally reconstruct the shape
Add an optional `note` field to ChangeRef. It's a string for annotation purposes.
```

**Rule 2 — ASCII diagrams with text explain for data flow**

Any data-flow or call-path description MUST include an ASCII tree or flowchart
using `│ ├── └──` notation. A diagram + short explanatory text is the target form.

```
# ✅ Good — tree + companion text
sspec change new --from <req>
  │
  ├── parse_request(req_path)    → reads frontmatter, validates status
  ├── create_change_dir(name)    → mkdir .sspec/changes/<ts>_<name>/
  ├── copy_templates()           → spec.md, tasks.md, handover.md from templates/
  └── link_request(req, change)  → writes reference in BOTH directions

`link_request` is bidirectional: request frontmatter gets `attach-change` updated;
spec.md `reference` array gets a `type: request` entry appended.
```

```
# ❌ Bad — text-only narration
When creating a change from a request, the system reads the request, creates a
directory, copies templates, then links them bidirectionally.
```

**Rule 3 — Scope Summary Table**

For changes affecting ≥3 files, Key Design MUST end with a `File | Change` table.
This provides reviewers and implementers a fast orientation map.

```markdown
### Scope Summary
| File | Change |
|------|--------|
| `src/sspec/services/change_service.py` | Add `--from-request` linking logic |
| `src/sspec/templates/change/spec.md`   | Update Key Design comment |
| `src/sspec/commands/change.py`         | Wire `--from` option to service |
```

**Rule 4 — Change Item Labeling**

For changes with ≥3 independent items (fixes, features, or refactors), label each
item in Section B (Label A / B / C, or descriptive slug). This creates stable
cross-references for tasks.md.

```markdown
# ✅ Good — labeled, addressable in tasks.md
**Fix A: Request linking** — `link_request()` must write bidirectional references.
**Feat B: Dry-run mode** — Add `--dry-run` to `change new`, print plan without writing.
**Refactor C: Name normalization** — Extract slug sanitization to `core.normalize_name()`.

# In tasks.md:
- [ ] Implement Fix A per spec §B
- [ ] Implement Feat B per spec §B
```

```markdown
# ❌ Bad — unlabeled, tasks.md must re-describe the design
### Changes
Add bidirectional linking to change creation. Add dry-run flag. Refactor name normalization.
```

**What does NOT belong in B**: Execution order (tasks.md), file-level task lists (tasks.md).

**B vs tasks.md boundary**: B defines *how it should work* (interfaces, data model, logic). tasks.md defines *what to do* (file-level steps, verification). Tasks reference B — e.g. "implement interface per spec.md B" — never copy.

### Section B Skeleton (Key Design Sub-sections)

```markdown
### Key Design

#### Interface Design
...typed code block per Rule 1...

#### Data Flow
...ASCII tree per Rule 2...

#### Key Logic
...decision rules / algorithm...

#### Scope Summary
| File | Change |
|------|--------|
| ... | ... |
```

📚 Full examples with all four rules applied: [examples-single.md](./examples-single.md)

## Step 3B: Fill Root Change spec.md (Type B)

Root spec.md describes the **overall problem scope and phase decomposition**.
It does NOT contain file-level interface or data-model details — those belong in sub-change specs.

**Section A**: Overall problem — full scope across all phases, not a single module.

**Section B**:
- `### Overall Approach`: High-level strategy, delivery order, key constraints.
- `### Phase Overview`: Each phase as a named deliverable with scope and dependencies.

### Phase Overview Format

Use a dependency-annotated list. For complex dependency graphs, follow with an ASCII tree:

```markdown
### Phase Overview

- **Phase 1: Auth Backend** — JWT + Redis cache. Goal: <1s auth latency. Scope: `src/auth/`, `src/services/`.
- **Phase 2: Auth Frontend** — Login/signup UI. Depends on Phase 1.
- **Phase 3: RBAC** — Role-permission matrix, tenant-scoped. Depends on Phase 1 (independent of Phase 2).

Dependency tree:
Phase 1: Auth Backend
  ├── Phase 2: Auth Frontend
  └── Phase 3: RBAC
```

For ≥4 phases, use a dependency table:

```markdown
| Phase | Depends On | Scope |
|-------|-----------|-------|
| Phase 1: Auth Backend | — | `src/auth/`, `src/services/` |
| Phase 2: Auth Frontend | Phase 1 | `src/frontend/auth/` |
| Phase 3: RBAC | Phase 1 | `src/models/`, `src/middleware/` |
```

### Creating Sub-Changes

After defining phases → create sub-changes:
```bash
sspec change new <phase-name>    # for each phase, link to root via reference
```

For each sub-change, ensure two-way references:
- Sub `spec.md` has a `reference` item with `type: root-change` pointing to root
- Root `spec.md` appends a `type: sub-change` entry pointing to that sub-change

Each sub-change then goes through its own design → plan → implement → review cycle.

### Presentation Rules for Root Change

Rules 1–4 from Step 3A apply when relevant, adapted to phase scope:

| Rule | Single Change | Root Change |
|------|--------------|-------------|
| Rule 1 (code blocks) | Interfaces in sub-sections | Shared interfaces that span phases (if any) |
| Rule 2 (ASCII diagrams) | Data-flow within a module | Phase dependency tree |
| Rule 3 (Scope Summary) | ≥3 files → File\|Change table | Phase\|Depends On\|Scope table |
| Rule 4 (item labeling) | ≥3 independent fixes/feats | ≥3 phases with independent scope |

Root spec does NOT include file-level Scope Summary — that belongs in each sub-change's spec.

### Pitfalls

| Mistake | Fix |
|---------|-----|
| File-level tasks in root tasks.md | Root tracks milestones only — file tasks go in sub-change |
| Skip root, jump straight to sub-changes | Root provides phase vision and coordination |
| Forget bidirectional references | Always link root ↔ sub in both `spec.md` reference fields |
| Archive root before all subs done | Root stays active until every sub-change is archived |

📚 Root change examples: [examples-root.md](./examples-root.md)

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
| Single-change examples (Simple / Medium / Complex) + B→tasks boundary | [examples-single.md](./examples-single.md) |
| Root-change examples (phase overview, dependency tree, sub-change B) | [examples-root.md](./examples-root.md) |
