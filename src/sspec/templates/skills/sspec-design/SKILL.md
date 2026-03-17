---
name: sspec-design
description: "Assess scale, create change, fill spec.md, align with user. Use after research when ready to define the solution."
metadata:
  author: frostime
  version: 4.0.2
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
4. @align user for alignment (MANDATORY)
```

## Step 1: Assess Scale

Use the Scale Assessment rules in `AGENTS.md` (search: `Scale Assessment`) to split micro / single / multi.
Fallback heuristic (only if `AGENTS.md` isn't available): Micro (≤3 files, ≤30min) | Multi/Root (>15 files OR >20 tasks OR >1 week) | else Single.
If uncertain, default to **Single** and `@align` whether to split.

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

### Section A — Problem Statement

- Quantify impact: "[metric] causing [impact]"
- Simple changes: single paragraph
- Complex changes: split "Current Situation" + "User Requirement"

| Bad | Good |
|-----|------|
| "Need to refactor" | "Auth takes 5s → 12% conversion drop" |
| "Improve the UI" | "Form completion rate 23% → target 60%" |

### Section B — Proposed Solution

`### Approach`: Core idea (1-3 paragraphs) + why this over alternatives.

`### Key Design`: Apply the scale-aware pattern below.

| Complexity | Design Depth |
|------------|-------------|
| Simple (≤3 files) | Keep Key Design inline in Approach unless a dedicated sub-section materially improves clarity |
| Medium (4-15 files) | Choose 1-4 dedicated dimension sub-sections |
| Complex (>15 files) | Keep B as a predictive summary; move full design to `reference/design.md` and link from B |

### Choosing Dimensions

A spec is a **prediction contract** — the user reads it and forms an expectation of what the change will produce. Different changes need different kinds of prediction.

Before writing Key Design sub-sections, ask yourself:

1. What kind of change is this? (feature / fix / refactor / docs / ...)
2. What does the user need to predict to feel in control?
3. Which 1-4 dimensions best serve that prediction?

Your choice is reflected in the sub-section headings you use. No need to write a "dimension selection rationale" - the structure speaks for itself.
If the change is simple enough to stay inline, treat the dimensions as a mental checklist rather than mandatory headings.

If you need a safe starting point, use one of these default combinations, then adjust:

| Change shape | Safe default |
|--------------|--------------|
| Feature / bugfix | Interface Contract + Behavioral Spec |
| Refactor | Structural Blueprint + Behavioral Spec |
| Docs / template / protocol | Content Outline |
| Migration / compatibility | Migration Path + Interface Contract |

These are starter combinations, not a substitute for thinking.

### Predictability Dimensions

| Dimension | User's Question | When to Use |
|-----------|----------------|-------------|
| Outcome Preview | "What will it look like when done?" | Result is visually demonstrable (CLI output, UI, before/after) |
| Interface Contract | "What are the boundaries and contracts?" | Involves function signatures, APIs, type definitions |
| Structural Blueprint | "How are things organized?" | Involves module splits, file trees, component hierarchy |
| Behavioral Spec | "How does the system behave?" | Involves call chains, state machines, algorithm flows |
| Data Architecture | "What does the data look like and how does it flow?" | Involves schemas, storage structures, data pipelines |
| Content Outline | "What will the content structure be?" | Changes target documents, templates, or specs |
| Migration Path | "How do we get from here to there?" | Needs migration, compatibility, or rollback strategy |

The menu is open — custom dimensions are allowed if none of the above fit. Briefly note the rationale in Approach.

Each dimension has a detailed writing spec and snippet examples available as a howto:

```
sspec howto list --type design-dimension    # browse all dimension cards
sspec howto write-dim-<name>                # read a specific dimension
sspec howto read write-dim-<n1> write-dim-<n2>  # read in batch
```

Two old hard constraints still matter:
- Interface Contract / Data Architecture -> show interfaces and types in fenced typed code blocks.
- Behavioral Spec / Structural Blueprint -> show behavior or structure as an ASCII diagram, not prose-only narration.

For complex changes (>15 files), do not expand every detail inline in Section B.
Keep B as the prediction summary:
- `### Approach` -> strategy and rationale
- `### Key Design` -> core interfaces, flows, or boundaries only
- `reference/design.md` -> full design detail

### Universal Rules

These rules apply to **every** spec regardless of which dimensions are chosen.

**Read the dimension howto before writing** — Each dimension's howto defines its writing norms (e.g. code blocks for interfaces, ASCII diagrams for behavior). Read it before writing that sub-section: `sspec howto write-dim-<name>`.

**Scope Summary Table** — For changes affecting ≥3 files, Key Design MUST end with a `File | Change` table. This gives reviewers and implementers a fast orientation map.

```markdown
### Scope Summary
| File | Change |
|------|--------|
| `src/api/users.py` | Add new handler `GET /users/{id}` |
| `src/services/cache.py` | Add `get_cached_user()` + TTL jitter |
| `tests/test_users_api.py` | Add tests for cache hit/miss |
```

**Boundary Note** — If scope boundaries are non-obvious or user anxiety is high, add a short `### What Stays Unchanged` block after the scope table. Use it to name nearby surfaces that are intentionally untouched.

```markdown
### What Stays Unchanged
- Existing auth token format
- Public `GET /users/{id}` response shape
- Cache TTL defaults outside the new user lookup path
```

**Item Labeling** — For changes with ≥3 independent items (fixes, features, or refactors), label each item in Section B. This creates stable cross-references for tasks.md.

```markdown
**Fix A: Request linking** — `link_request()` must write bidirectional references.
**Feat B: Cache TTL jitter** — Add ±10% jitter to reduce stampede risk.
**Refactor C: Extract cache interface** — isolate I/O behind `CacheClient`.

# In tasks.md:
- [ ] Implement Fix A per spec §B
- [ ] Implement Feat B per spec §B
```

### B vs tasks.md Boundary

B defines *how it should work* (design). tasks.md defines *what to do* (execution). Tasks reference B — e.g. "implement interface per spec.md B" — never copy.

**What does NOT belong in B**: Execution order, file-level task lists.

📚 Scenario examples: [examples-feature.md](./examples-feature.md) | [examples-docs.md](./examples-docs.md) | [examples-refactor.md](./examples-refactor.md)

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

Universal rules from Step 3A apply, adapted to phase scope:

| Rule | Single Change | Root Change |
|------|--------------|-------------|
| Scope Summary | ≥3 files → File\|Change table | Phase\|Depends On\|Scope table |
| Item Labeling | ≥3 independent fixes/feats | ≥3 phases with independent scope |

Phase dependency trees use ASCII diagrams (see `sspec howto write-dim-behavioral-spec` for notation).

Root spec does NOT include file-level Scope Summary — that belongs in each sub-change's spec.

### Pitfalls

| Mistake | Fix |
|---------|-----|
| File-level tasks in root tasks.md | Root tracks milestones only — file tasks go in sub-change |
| Skip root, jump straight to sub-changes | Root provides phase vision and coordination |
| Forget bidirectional references | Always link root ↔ sub in both `spec.md` reference fields |
| Archive root before all subs done | Root stays active until every sub-change is archived |

📚 Root change examples: [examples-root.md](./examples-root.md)

## Step 4: @align for Alignment (MANDATORY)

**Never skip this step.** This is a hard gate — the user must confirm the design before planning can be considered complete.

Present the design to user for confirmation:
- Problem statement summary
- Proposed approach and rationale
- Key design dimensions chosen and their core decisions
- (Root) Phase breakdown

If a `question`-like tool is available, use it for the gate. Otherwise present the design clearly in normal output and stop.

After user confirms design, proceed to `sspec-plan`.

---

## References

| When | Load |
|------|------|
| Feature/Bugfix scenario examples | [examples-feature.md](./examples-feature.md) |
| Protocol/Template/Docs scenario examples | [examples-docs.md](./examples-docs.md) |
| Refactor/Migration scenario examples | [examples-refactor.md](./examples-refactor.md) |
| Root-change examples (phase overview, dependency tree, sub-change B) | [examples-root.md](./examples-root.md) |
| Dimension writing specs (per-dimension howto cards) | `sspec howto list --type design-dimension` |
