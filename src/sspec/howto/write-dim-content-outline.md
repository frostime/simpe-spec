---
name: write-dim-content-outline
desc: "Design dimension: Content Outline — document structure, chapter plans, template layouts."
type: design-dimension
---

# Content Outline

## What It Answers

User's question: "What will the content structure be?"

## When to Choose

- Writing or restructuring documentation, spec-docs, READMEs
- Changing SKILL files, AGENTS.md, or protocol templates
- Designing template structures (memory, spec, tasks)
- Any change where the primary deliverable is text content, not code

## How to Write

Show the target structure as a heading outline or section list. The reader
should be able to predict what each section will contain.

**Heading outline pattern** — best for document restructuring:

```markdown
# SKILL.md (revised structure)

## Workflow                    — unchanged
## Step 1: Assess Scale        — unchanged
## Step 2: Create Change       — unchanged
## Step 3A: Fill Single Change
  ### Choosing Dimensions      — NEW: meta-thinking guidance
  ### Predictability Dimensions — NEW: dimension menu table
  ### Writing Rules            — dimension howto + B vs tasks.md boundary
## Step 3B: Fill Root Change   — unchanged
## Step 4: @align              — unchanged
## References                  — updated links to new example files
```

**Change inventory pattern** — best for multi-item content changes (used in `### Implementation Changes`):

```markdown
**Change A: Refresh project.md** — Update stack description, key paths,
and spec-doc index to match current repo.

**Change B: Fix skill-installation.md** — Correct workspace location names
and Windows link behavior.

**Change C: Add change-lifecycle.md** — New spec-doc covering directory
structure, status parsing, and archive semantics.
```

**Template structure pattern** — best for template design:

```markdown
## Howto Card Structure

Each dimension howto follows this layout:
1. Frontmatter (name, desc, type)
2. What It Answers — one-line user question
3. When to Choose — bullet list of signals
4. How to Write — writing norms + snippet examples
5. Pairs Well With — dimension combinations
```

Avoid prose-heavy descriptions of what sections "will discuss". Show the
structure; let the headings speak.

## Pairs Well With

- Migration Path (when restructuring existing documents)
- Scope Summary / What Stays Unchanged blocks (when content scope needs explicit boundaries)
