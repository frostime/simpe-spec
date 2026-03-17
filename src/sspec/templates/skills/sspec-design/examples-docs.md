# Design Examples — Protocol / Template / Docs

Scenario examples for changes that target documentation, SKILL files, templates, or protocol definitions.
These are **references, not prescriptions** — adapt dimensions to your specific change.

**Typical dimensions**: Content Outline

Path note: when a sample includes `reference.source`, it is workspace-relative and normally starts with `.sspec/`.

---

## Protocol Example: Simplify @align to two levels

Dimensions chosen: Content Outline (protocol structure changes).

```markdown
---
name: simplify-align
status: PLANNING
change-type: single
created: 2026-03-17T01:00:00
reference: null
---

# simplify-align

## A. Problem Statement

### Current Situation

The @align interaction layer was designed for Copilot Agent Mode's per-turn billing model.
In non-Copilot systems (Claude Code, OpenCode, Cursor), the complex channel selection matrix
and `@force-end-align` create unnecessary cognitive load for agents without adding value.

### User Requirement

Simplify @align from a single mandatory-stop level to a two-level system (report vs gate),
removing Copilot-specific mechanisms while preserving the change lifecycle structure.

## B. Proposed Solution

### Approach

Keep the change lifecycle skeleton (Research → Design → Plan → Implement → Review → Handover)
intact. Only rewrite the interaction layer: how agents communicate with users during the workflow.

### Key Design

#### Content Outline

AGENTS.md §3 Alignment — revised structure:

\`\`\`text
## 3. Alignment (@align)

Two levels:
| Level   | Agent behavior                    | When to use                    |
|---------|-----------------------------------|--------------------------------|
| report  | Output summary, keep going        | Plan done, progress updates    |
| gate    | Output question, stop and wait    | Design done, Implement done,   |
|         |                                   | irreversible actions, blockers |

How to gate:
- question tool available → use it
- otherwise → state question in output, end turn, wait
\`\`\`

sspec-align SKILL — revised structure:

\`\`\`text
# sspec-align SKILL (revised)
## Two-Level @align           — report vs gate definitions
## Gate Implementation        — question tool → sspec tool ask fallback → output
## Recording Decisions        — spec.md for design, handover.md for direction changes
\`\`\`

### Key Change

**Change A: @align two levels** — Replace single mandatory-stop with report/gate split.

**Change B: Remove @force-end-align** — Delete from AGENTS.md, SKILL, and HOWTO.

**Change C: sspec ask exits main flow** — Remove from recommended workflow; restore as
`sspec tool ask` fallback only.

**Change D: Strengthen micro path** — Explicit skip permission for ≤3 files, ≤30min tasks.

**Change E: Remove Copilot-specific HOWTOs** — Delete `force-end-align`, `use-sspec-ask`,
`write-sspec-ask`.

### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/templates/AGENTS.md` | Rewrite §3 (two-level align); remove @force-end-align; strengthen micro path |
| `src/sspec/templates/skills/sspec-align/SKILL.md` | Rewrite: two-level system, remove channel matrix |
| `src/sspec/templates/skills/sspec-design/SKILL.md` | Keep gate at exit, remove sspec ask references |
| `src/sspec/templates/skills/sspec-plan/SKILL.md` | Change exit from gate to report |
| `src/sspec/templates/skills/sspec-implement/SKILL.md` | Keep gate at exit, remove sspec ask references |
| HOWTO `force-end-align` | Delete |
| HOWTO `use-sspec-ask` | Delete |
| HOWTO `write-sspec-ask` | Delete |

### What Stays Unchanged

- Change lifecycle (Research → Design → Plan → Implement → Review → Handover)
- spec.md / tasks.md / handover.md structure and templates
- spec-docs system
- Scale assessment logic (micro/single/multi)
- Design and Implement hard gate nature (only implementation method changes)
```

---

## Documentation Example: Refresh project spec-docs

Dimensions chosen: Content Outline (what docs to fix/add).

```markdown
---
name: refresh-spec-docs
status: PLANNING
change-type: single
created: 2026-03-06T23:39:00
reference: null
---

# refresh-spec-docs

## A. Problem Statement

At least 4 existing spec-docs describe outdated paths, field names, or tool inventory.
That drift causes future agents to follow stale guidance when reading `.sspec/spec-docs/`.

## B. Proposed Solution

### Approach

Treat this as a bounded documentation transaction: first fix factual drift in existing docs,
then add a small set of new spec-docs for stable contracts that currently live only in code.

### Key Design

#### Content Outline

Six items across two categories: drift repair (Fix A–B) and new contracts (Doc C–F).
Fix items correct stale facts in existing docs. Doc items create new spec-docs for
stable contracts that currently live only in code.

### Key Change

**Fix A: Project context refresh** — Update `.sspec/project.md` so the stable identity
layer matches the actual stack, command surface, and platform behavior.

**Fix B: Existing spec-doc drift repair** — Correct stale facts in `skill-installation.md`,
`builtin-tools.md`, and `testing-standards.md`.

**Doc C: Change lifecycle contract** — New spec-doc for `.sspec/changes/<dir>/` structure,
status parsing, archive moves, and reference rewrite behavior.

**Doc D: Interaction record contracts** — New spec-doc for request and ask artifacts:
creation format, linking, answer persistence, archive rewrite.

**Doc E: Command registry contract** — New spec-doc for `.sspec/commands/registry.yaml`
and script strategy semantics.

**Doc F: Root AGENTS sync contract** — New spec-doc for the managed `SSPEC:START/END`
block ownership and update behavior.

### Scope Summary

| File | Change |
|------|--------|
| `.sspec/project.md` | Refresh stack, key paths, conventions |
| `.sspec/spec-docs/skill-installation.md` | Correct workspace locations and link behavior |
| `.sspec/spec-docs/builtin-tools.md` | Document current tool inventory |
| `.sspec/spec-docs/testing-standards.md` | Remove dead modules, align expectations |
| `.sspec/spec-docs/change-lifecycle.md` | New: change directory and status contract |
| `.sspec/spec-docs/interaction-records.md` | New: request/ask file format contract |
| `.sspec/spec-docs/cmd-registry.md` | New: command registry contract |
| `.sspec/spec-docs/agents-sync.md` | New: root AGENTS.md managed block contract |
```
