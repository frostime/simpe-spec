---
name: sspec-design
description: "Assess scale, create change, fill spec.md + design.md, align with user. Use after clarify when ready to define the solution."
metadata:
  author: frostime
  version: 5.0.0
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

Follow the template `@RULE` blocks. Key sections:

- **Problem Statement**: Quantify impact. Format: "[metric] causing [impact]".
- **Approach**: Core idea (1-3 paragraphs) + why this over alternatives.
- **Key Change**: REQUIRED. Label each independent change item with `**Type Label: Title**` format. This is what lets the user predict *exactly what will change*.
- **Scope Summary**: REQUIRED. File | Change table.
- **Design Reference**: If design.md exists, link it here.

### design.md — when to create

Create `design.md` when the change involves new interface definitions, data model changes, or architectural logic changes. Simple bugfixes and text changes don't need it.

```bash
sspec change scaffold design <change>  # create design.md from template
```

### Writing design.md — Prediction Contract

spec + design is a **prediction contract**: the user reads it and predicts what the code will look like. Your job is to think carefully about which dimensions to cover so the user feels in control of this change.

**Guiding question**: What does the user need to predict to feel in control? Answer this for the specific change, then choose dimensions accordingly.

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

Custom dimensions are fine — use whatever makes the prediction clearer.

**Minimum quality bar**: design.md MUST contain at least one structured artifact (code block, diagram, table, or labeled items). Pure prose design is not acceptable.

**Key principle**: show, don't describe. `def process(x: Input) -> Output` beats "a function that accepts X and returns Y".

### spec.md vs design.md boundary

| Content | Where |
|---------|-------|
| What problem, why it matters | spec.md Problem Statement |
| Core approach + rationale | spec.md Approach |
| What changes, labeled items | spec.md Key Change |
| Which files affected | spec.md Scope Summary |
| How it works technically (interfaces, data models, behavior) | design.md |

### spec.md vs tasks.md boundary

spec.md/design.md = *how it should work* (design). tasks.md = *what to do* (execution).
Tasks reference spec labels (e.g. "Implement Fix A per spec") and MUST NOT copy the logic description.

### Root change

Root spec.md = **overall problem scope + phase decomposition**. No file-level details — those belong in sub-change specs.

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

Present: problem summary, approach + rationale, key design decisions, scope. Use `question-like` tool if available, otherwise present clearly and stop.

After confirmation → proceed to `sspec-plan`.

### Revision mechanism

After this gate, spec.md and design.md baselines become **immutable**. Any subsequent scope or design change MUST go through the revision protocol:
1. Create `revisions/NNN-description.md` recording what changed and why
2. Update tasks.md to reflect new work
3. The original spec.md/design.md are NOT modified

→ `sspec howto handle-review-scope-change`
