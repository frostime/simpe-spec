---
name: sspec-design
description: "Assess scale, create change, fill spec.md + design.md, align with user. Use after research when ready to define the solution."
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

## Step 2: Explore Solutions

Before writing formal design, ensure the technical direction is aligned.

- If user has already specified a clear approach (in request, conversation, or prior alignment) → adopt it directly, proceed to Step 3.
- If approach is open → present 1-2 candidate approaches with core tradeoffs. Let user express preference before drafting formal design.
- If user describes a solution but the underlying goal is unclear → probe the goal first (Research should have caught this, but double-check).

This is a lightweight discussion, not a document. The goal is to avoid writing a full spec.md only to discover the user wanted a different direction.

## Step 3: Create Change

```bash
sspec change new <name>                         # minimal: spec.md + handover.md
sspec change new <name> --scaffold tasks         # also create tasks.md
sspec change new <name> --scaffold tasks,design  # also create design.md
sspec change new --from <request>                # create + link request
sspec change new <name> --root                   # root coordinator
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

The design.md template contains the Quality Bar and reference organization patterns. Key principle: **use semi-structured, formal expression over flat prose — increase information density, reduce ambiguity, improve comprehension efficiency.**

For writing guidance on specific design aspects: `sspec howto list --type design-dimension`

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
