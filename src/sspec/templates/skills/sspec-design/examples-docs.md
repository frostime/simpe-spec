# Design Examples — Protocol / Template / Docs

Scenario examples for changes that target documentation, SKILL files, templates, or protocol definitions.
These are **references, not prescriptions** — adapt to your specific change.

Path note: when a sample includes `reference.source`, it is workspace-relative and normally starts with `.sspec/`.

---

## Protocol Example: Simplify @align to two levels

```markdown
---
name: simplify-align
status: PLANNING
change-type: single
created: 2026-03-17T01:00:00
reference: null
---

# simplify-align

## Problem Statement

The @align interaction layer was designed for Copilot Agent Mode's per-turn billing model.
In non-Copilot systems (Claude Code, OpenCode, Cursor), the complex channel selection matrix
and `@force-end-align` create unnecessary cognitive load for agents without adding value.

## Proposed Solution

### Approach

Keep the change lifecycle skeleton (Clarify → Design → Plan → Implement → Review)
intact. Only rewrite the interaction layer: how agents communicate with users during the workflow.

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

- Change lifecycle (Clarify → Design → Plan → Implement → Review)
- spec.md / tasks.md / memory.md structure and templates
- Scale assessment logic (micro/single/multi)
- Design and Implement hard gate nature

### Design Reference

→ 详细技术设计见 [design.md](./design.md)
```

**design.md** — for a protocol/docs change, the "design" is the new content structure itself.
Show the before/after document outline, not prose description:

```markdown
---
change: "simplify-align"
created: 2026-03-17T01:00:00
---

# Design: simplify-align

## AGENTS.md §3 — Revised Structure

```text
# Before: §3 Alignment
  - Three levels: report / gate / force-end
  - Channel selection matrix (Copilot / non-Copilot)
  - @force-end-align directive
  - sspec ask as primary channel

# After: §3 Alignment
  - Two levels: report / gate
  - Single fallback chain: question tool → sspec tool ask → plain output
  - No Copilot-specific paths
```

## sspec-align SKILL — Revised Outline

```text
## 1. Two Levels
   report: output summary, keep going
   gate:   output summary, stop and wait

## 2. How To Gate
   question tool → sspec tool ask → plain output (fallback chain)

## 3. After Align
   record decisions in natural home (spec.md / memory.md / tasks.md)
```

## Removed Directives

| Removed | Reason |
|---------|--------|
| `@force-end-align` | Copilot-specific, no value in other systems |
| `sspec ask` as primary channel | Replaced by question tool + fallback chain |
```

---

## Documentation Example: Refresh project spec-docs

```markdown
---
name: refresh-spec-docs
status: PLANNING
change-type: single
created: 2026-03-06T23:39:00
reference: null
---

# refresh-spec-docs

## Problem Statement

At least 4 existing spec-docs describe outdated paths, field names, or tool inventory.
That drift causes future agents to follow stale guidance when reading `.sspec/spec-docs/`.

## Proposed Solution

### Approach

Treat this as a bounded documentation transaction: first fix factual drift in existing docs,
then add a small set of new spec-docs for stable contracts that currently live only in code.

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

For a pure docs change like this, design.md is typically not needed — the Key Change labels
and Scope Summary already give the user full predictability. Create design.md only if the
new doc content itself has structural complexity worth showing upfront (e.g. a new spec-doc
with a non-obvious schema).
