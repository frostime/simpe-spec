---
name: sspec-design
description: "Assess scale, create change, fill spec.md + design.md, align with user. Use after clarify when ready to define the solution."
metadata:
  author: frostime
  version: 5.1.0
---

# SSPEC Design

Define the problem, design the solution, create the change. **The user MUST confirm the design before planning** — never auto-advance without **align**.

---

## Workflow

```
1. Assess scale → micro / single / multi
2. Explore solutions with user (if approach not predetermined)
3. Create change (CLI)
4. Fill spec.md (+ design.md if needed)
5. @align user (gate)
```

## Step 1: Assess Scale

Use `AGENTS.md` Scale Assessment. Fallback: Micro (≤3 files, ≤30min) | Multi (>15 files OR >20 tasks OR >1 week) | else Single.
Uncertain → default **Single**, `@align` whether to split.

## Step 2: Converge Solution

Clarify phase should have produced a Problem Statement + direction sketch.

- If Clarify produced a clear direction → adopt it, proceed to Step 3.
- If multiple approaches surfaced during Clarify → present final recommendation with tradeoffs for user decision.
- If entering Design without prior Clarify (e.g. user jumped straight to "build X this way") → briefly verify the direction is sound. If the goal is unclear, step back to Clarify posture.

The goal is to converge on a single approach before formalizing into spec.md.

## Step 3: Create Change

```bash
sspec change new <name>                  # default: spec.md + tasks.md + memory.md
sspec change new <name> --scaffold design # also create design.md
sspec change new --from <request>         # create + link request
sspec change new <name> --root            # root coordinator
```

## Step 4: Fill spec.md + design.md

### spec.md

Follow the template comment constraints (BCP 14 keywords). Key sections:

- **Problem Statement**: Quantify impact. Format: "[metric] causing [impact]".
- **Approach**: Core idea (1-3 paragraphs) + why this over alternatives.
- **Behavior Contract**: REQUIRED. Define externally observable behavior boundaries: surface, before/after, unchanged boundary, compatibility/error behavior when relevant. Use `BC-*` labels when multiple contracts exist.
- **Implementation Changes**: REQUIRED. Label each independent implementation item with a unique `type(scope): title` label, such as `feat(cli): Add tag filter` or `refactor(service): Extract cache adapter`. Each item states which `BC-*` it serves.
- **Scope Summary**: REQUIRED. File | Change | Effort table. Effort uses `XS` / `S` / `M` / `L` as a rough design-stage estimate.
- **Design Reference**: If design.md exists, link it here.

### design.md — when to create

Create `design.md` when the change involves new interface definitions, data model changes, or architectural logic changes. Simple bugfixes and text changes don't need it.

```bash
sspec change scaffold design <change>  # create design.md from template
```

### Writing design.md — Prediction Contract

spec + design is a **prediction contract**: the user reads it and predicts the resulting code. Choose the dimensions that make that prediction possible for this specific change.

**Common dimensions** (examples, not checklist — pick what serves prediction):

| Dimension | User's question | Useful when | Format constraint |
|-----------|----------------|-------------|-------------------|
| Interface Contract | "What are the signatures / APIs?" | New or changed function/class/endpoint | Typed code block (MUST) |
| Behavioral Spec | "How does it behave at runtime?" | Call chains, state transitions, algorithms | ASCII diagram (MUST) |
| Structural Blueprint | "How is it organized?" | Module splits, file trees, component hierarchy | ASCII diagram (MUST) |
| Data Architecture | "What does the data look like?" | Schemas, storage, data pipelines | Typed code block (MUST) |
| Outcome Preview | "What will I see?" | CLI output, UI, before/after | Example output block |
| Content Outline | "What's the content structure?" | Documents, templates, specs | Heading tree / outline |
| Migration Path | "How do we get from here to there?" | Compatibility, rollback, versioning | Step list + constraints |

Custom dimensions are fine.

**Minimum quality bar**: design.md MUST contain at least one structured artifact (code block, diagram, table, or labeled items). Show, don't describe — `def process(x: Input) -> Output` beats "a function that accepts X and returns Y".

### spec.md vs design.md boundary

| Content | Where |
|---------|-------|
| What problem, why it matters | spec.md Problem Statement |
| Core approach + rationale | spec.md Approach |
| Externally observable behavior boundaries | spec.md Behavior Contract |
| Implementation items and changelog-style labels | spec.md Implementation Changes |
| Which files affected + rough effort | spec.md Scope Summary |
| How it works technically (interfaces, data models, algorithms) | design.md |

### spec.md vs tasks.md boundary

spec.md/design.md = *how it should work* (design). tasks.md = *what to do* (execution) and *how to verify it*.
Tasks reference `BC-*` behavior labels and `type(scope): title` implementation labels. They MUST NOT redefine behavior contracts or copy design logic.

### Root change

Root spec.md = **overall problem scope + phase decomposition**. Root Behavior Contract stays phase-level and final-outcome focused. No file-level details — those belong in sub-change specs.

After defining phases: `sspec change new <phase-name>` for each sub-change.

Ensure **bidirectional references**:
- Sub spec.md → `type: root-change` pointing to root
- Root spec.md → `type: sub-change` pointing to sub

| Pitfall | Fix |
|---------|-----|
| File-level tasks in root tasks.md | Root = milestones only; file tasks → sub-change |
| Skip root, jump to sub-changes | Root provides phase vision and coordination |
| Forget bidirectional references | Always link root ↔ sub in both spec.md |

📚 Examples: [examples-feature.md](./examples-feature.md) | [examples-refactor.md](./examples-refactor.md) | [examples-docs.md](./examples-docs.md) | [examples-root.md](./examples-root.md)

## Step 5: @align

**Hard gate** — the user MUST confirm before planning proceeds.

Present: problem summary, approach + rationale, Behavior Contract, implementation labels, scope/effort, key risks. Use `question-like` tool if available, otherwise present clearly and stop.

After confirmation → proceed to `sspec-plan`.

### Revision mechanism

During Design: user-requested changes → edit spec.md/design.md directly, no revision.

Once the change enters Plan (tasks.md created), spec.md/design.md become **immutable**. Any subsequent scope or design change MUST go through the revision protocol:
1. Create `revisions/NNN-description.md` recording what changed and why
2. Update tasks.md to reflect new work
3. The original spec.md/design.md are NOT modified

→ `sspec howto handle-review-scope-change`
