---
name: sspec-design
description: "Assess scale, create change, fill spec.md, align with user. Use after research when ready to define the solution."
metadata:
  author: frostime
  version: 4.1.0
---

# SSPEC Design

Define the problem, design the solution, create the change. **User must confirm design before planning** — never auto-advance without **align**.

---

## Workflow

```
1. Assess scale → micro / single / multi
2. Create change (CLI)
3. Fill spec.md → Type A (single/sub) or Type B (root)
4. @align user (MANDATORY gate)
```

## Step 1: Assess Scale

Use `AGENTS.md` Scale Assessment. Fallback: Micro (≤3 files, ≤30min) | Multi (>15 files OR >20 tasks OR >1 week) | else Single.
Uncertain → default **Single**, `@align` whether to split.

## Step 2: Create Change

```bash
sspec change new <name>            # single/sub change
sspec change new --from <request>  # create + link request
sspec change new <name> --root     # root coordinator
```

Verify generated `spec.md` frontmatter follows template `@RULE`:
- `status`: `PLANNING` | `change-type`: `single` | `sub` | `root`
- `reference` entries: workspace-relative `source` (no leading `./`), valid `type` per template

## Step 3A: Fill Single/Sub spec.md (Type A)

Follow guidance below + `@RULE` blocks in the generated template.

### Section A — Problem Statement

Quantify impact: "[metric] causing [impact]". Simple → single paragraph. Complex → split "Current Situation" + "User Requirement".

| Bad | Good |
|-----|------|
| "Need to refactor" | "Auth takes 5s → 12% conversion drop" |
| "Improve the UI" | "Form completion rate 23% → target 60%" |

### Section B — Proposed Solution

Section B has three parts. Approach and Key Design are flexible; **Key Change and Scope Summary are mandatory** (but scale with complexity — a single-line each is fine for simple changes).

```
### Approach          — core idea + rationale (always)
### Key Design        — optional dimension sub-sections (scale-aware)
### Key Change        — per-item decisions and constraints (always, ≥1 item)
### Scope Summary     — File | Change table (always, ≥1 file)
```

`### Approach`: Core idea (1-3 paragraphs) + why this over alternatives.

`### Key Design`: Scale-aware depth:

| Complexity | Design Depth |
|------------|-------------|
| Simple (≤3 files) | Inline in Approach unless sub-section materially improves clarity |
| Medium (4-15 files) | 1-4 dedicated dimension sub-sections |
| Complex (>15 files) | B = predictive summary; full design in `reference/design.md` |

`### Key Change`: Label each independent change item and describe its core decision, constraints, and boundary conditions. This is what lets the user predict *exactly how the code will change*. Use `**Type Label: Title**` format:

```markdown
**Fix A: Request linking** — `link_request()` writes bidirectional references.
  Absolute paths outside workspace require confirmation; `--unsafe` bypasses.
**Feat B: Cache TTL jitter** — ±10% jitter to reduce stampede risk.
  `no_change_patch` counts as non-fatal so reruns don't fail.
```

tasks.md references these labels: "Implement Fix A per spec §B". Never copy the logic description into tasks.

`### Scope Summary`: File | Change table — every spec must end with this.

```markdown
| File | Change |
|------|--------|
| `src/api/users.py` | Add `GET /users/{id}` handler |
| `src/services/cache.py` | Add `get_cached_user()` + TTL jitter |
```

If scope boundaries are non-obvious, add `### What Stays Unchanged` after the table.

### Choosing Dimensions

A spec is a **prediction contract** — the user reads it and predicts what the change will produce. Pick 1-4 dimensions that best serve that prediction.

Think: (1) What kind of change? (2) What must the user predict to feel in control? (3) Which dimensions serve that?

Structure speaks for itself — no need for a "dimension selection rationale". Simple changes: treat dimensions as mental checklist, not mandatory headings.

Safe defaults (adjust as needed):

| Change shape | Default dimensions |
|--------------|-------------------|
| Feature / bugfix | Interface Contract + Behavioral Spec |
| Refactor | Structural Blueprint + Behavioral Spec |
| Docs / template / protocol | Content Outline |
| Migration / compatibility | Migration Path + Interface Contract |

### Predictability Dimensions

| Dimension | User's Question | When to Use |
|-----------|----------------|-------------|
| Outcome Preview | "What will it look like?" | Visually demonstrable result (CLI, UI, before/after) |
| Interface Contract | "What are the contracts?" | Function signatures, APIs, type definitions |
| Structural Blueprint | "How are things organized?" | Module splits, file trees, component hierarchy |
| Behavioral Spec | "How does it behave?" | Call chains, state machines, algorithm flows |
| Data Architecture | "What does the data look like?" | Schemas, storage structures, data pipelines |
| Content Outline | "What's the content structure?" | Documents, templates, specs |
| Migration Path | "How do we get there?" | Migration, compatibility, rollback |

Custom dimensions allowed — note rationale in Approach.

Per-dimension writing specs — two-step workflow:
1. `sspec howto list --type design-dimension` — confirm which dimensions you need
2. `sspec howto read write-dim-<a> write-dim-<b>` — batch-read chosen dimensions in one call

Hard format constraints:
- Interface Contract / Data Architecture → fenced typed code blocks
- Behavioral Spec / Structural Blueprint → ASCII diagrams, not prose-only

### Writing Rules

**Read dimension howto before writing** — `sspec howto write-dim-<name>` defines writing norms for each dimension.

**B vs tasks.md boundary** — B = *how it should work* (design). tasks.md = *what to do* (execution). Tasks reference B labels (e.g. "Implement Fix A per spec §B"), never copy. Execution order and file-level task lists do NOT belong in B.

📚 Examples: [examples-feature.md](./examples-feature.md) | [examples-docs.md](./examples-docs.md) | [examples-refactor.md](./examples-refactor.md)

## Step 3B: Fill Root spec.md (Type B)

Root spec.md = **overall problem scope + phase decomposition**. No file-level details — those belong in sub-change specs.

Follow `@RULE` blocks in the generated root template.

**Section A**: Overall problem — full scope across all phases.

**Section B**:
- `### Overall Approach`: Strategy, delivery order, constraints.
- `### Phase Overview`: Each phase as named deliverable with scope and dependencies. Format per root template `@RULE` and [examples-root.md](./examples-root.md).

### Creating Sub-Changes

After defining phases: `sspec change new <phase-name>`

Ensure bidirectional references:
- Sub spec.md → `type: root-change` pointing to root
- Root spec.md → `type: sub-change` pointing to sub

Each sub-change follows its own design → plan → implement → review cycle.

### Root Presentation Rules

Key Change and Scope Summary rules from 3A apply, adapted:

| Rule | Root adaptation |
|------|----------------|
| Scope Summary | Phase \| Depends On \| Scope table (not file-level) |
| Key Change | ≥3 phases with independent scope |
| Dependencies | ASCII diagram for phase dependency trees |

### Pitfalls

| Mistake | Fix |
|---------|-----|
| File-level tasks in root tasks.md | Root = milestones only; file tasks → sub-change |
| Skip root, jump to sub-changes | Root provides phase vision and coordination |
| Forget bidirectional references | Always link root ↔ sub in both spec.md references |
| Archive root before subs done | Root stays active until all sub-changes archived |

📚 [examples-root.md](./examples-root.md)

## Step 4: @align (MANDATORY)

**Hard gate** — user must confirm before planning proceeds.

Present: problem summary, approach + rationale, key design decisions, (root) phase breakdown. Use `question-like` tool if available, otherwise present clearly and stop.

After confirmation → proceed to `sspec-plan`.

---

## References

| When | Load |
|------|------|
| Feature/Bugfix examples | [examples-feature.md](./examples-feature.md) |
| Docs/Template examples | [examples-docs.md](./examples-docs.md) |
| Refactor/Migration examples | [examples-refactor.md](./examples-refactor.md) |
| Root-change examples | [examples-root.md](./examples-root.md) |
| Dimension writing specs | `sspec howto list --type design-dimension` |
