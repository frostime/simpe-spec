---
name: sspec-design
description: "Assess scale, create change, fill spec.md, align with user. Use after research when ready to define the solution."
metadata:
  author: frostime
  version: 3.3.1
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

Use the Scale Assessment rules in `AGENTS.md` (search: `Scale Assessment`) to split micro / single / multi.
Fallback heuristic (only if `AGENTS.md` isn't available): Micro (≤3 files, ≤30min) | Multi/Root (>15 files OR >20 tasks OR >1 week) | else Single.
If uncertain, default to **Single** and `@ask` whether to split.

## Step 2: Create Change

Create the change directory first, then fill the generated `spec.md`.

```bash
sspec change new <name>            # standard single/sub change
sspec change new --from <request>  # create + link request file
sspec change new <name> --root     # root coordinator for multi-change
```

Full CLI quick reference lives in `AGENTS.md` under "CLI Quick Reference".

If you can't jump to sections, open `AGENTS.md` and search for that heading.

Sanity check: confirm the generated `spec.md` frontmatter (especially `change-type` and `reference`) follows the template `@RULE` (don't invent new keys).

Quick checks:
- `status` starts as `PLANNING`
- `change-type` is one of: `single` | `sub` | `root`
- `reference` entries use workspace-relative `source` paths (no leading `./`) and a `type` listed in the `spec.md` template `@RULE` (for example: `request`, `root-change`, `sub-change`, `prev-change`, `doc`)

## Step 3A: Fill Single/Sub Change spec.md (Type A)

Follow the guidance below and the `@RULE` blocks in the generated `spec.md` template.

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
HTTP Request
  │
  ├── validate_input()  → reject malformed data early
  ├── load_user()       → fetch from DB/cache
  ├── apply_change()    → pure business logic
  └── persist_result()  → write side effects

**Note**: Keep `apply_change()` pure so it can be unit-tested without I/O.
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
| `src/api/users.py` | Add new handler `GET /users/{id}` |
| `src/services/cache.py` | Add `get_cached_user()` + TTL jitter |
| `tests/test_users_api.py` | Add tests for cache hit/miss |
```

**Rule 4 — Change Item Labeling**

For changes with ≥3 independent items (fixes, features, or refactors), label each
item in Section B (Label A / B / C, or descriptive slug). This creates stable
cross-references for tasks.md.

```markdown
# ✅ Good — labeled, addressable in tasks.md
**Fix A: Request linking** — `link_request()` must write bidirectional references.
**Feat B: Cache TTL jitter** — Add ±10% jitter to reduce stampede risk.
**Refactor C: Extract cache interface** — isolate I/O behind `CacheClient`.

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

### Key Design Sub-sections (Recommended)

Prefer explicit sub-sections: `Interface Design` / `Data Flow` / `Key Logic` / `Scope Summary`.
If in doubt, mimic the structure from [examples-single.md](./examples-single.md).

📚 Full examples with all four rules applied: [examples-single.md](./examples-single.md)

## Step 3B: Fill Root Change spec.md (Type B)

Root spec.md describes the **overall problem scope and phase decomposition**.
It does NOT contain file-level interface or data-model details — those belong in sub-change specs.

Follow the guidance below and the `@RULE` blocks in the generated root `spec.md` template.

**Section A**: Overall problem — full scope across all phases, not a single module.

**Section B**:
- `### Overall Approach`: High-level strategy, delivery order, key constraints.
- `### Phase Overview`: Each phase as a named deliverable with scope and dependencies.

### Phase Overview Format

Follow the root `spec.md` template `@RULE` block and/or [examples-root.md](./examples-root.md).

### Creating Sub-Changes

After defining phases → create sub-changes:
```bash
sspec change new <phase-name>
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
