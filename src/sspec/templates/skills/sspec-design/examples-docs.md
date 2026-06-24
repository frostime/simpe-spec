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

### Behavior Contract

**BC-1: @align has two decision levels**

Surface: generated protocol and skill instructions.

After:
- Agents use `report` when work can continue and `gate` when user confirmation is required.
- `@force-end-align` is no longer part of the generated workflow.
- `sspec tool ask` remains only as a fallback interaction tool.

### Implementation Changes

**refactor(protocol): Split @align into report and gate** - Replace single mandatory-stop with report/gate split.

**refactor(protocol): Remove @force-end-align** - Delete from AGENTS.md, SKILL, and HOWTO.

**refactor(protocol): Move sspec ask out of main flow** - Remove from recommended workflow; restore as
`sspec tool ask` fallback only.

**docs(protocol): Strengthen micro path** - Explicit skip permission for <=3 files, <=30min tasks.

**docs(protocol): Remove Copilot-specific HOWTOs** - Delete `force-end-align`, `use-sspec-ask`,
`write-sspec-ask`.

Serves: BC-1.

### Scope Summary

| File | Change | Effort |
|------|--------|--------|
| `src/sspec/templates/AGENTS.md` | refactor(protocol): rewrite section 3; remove @force-end-align; strengthen micro path | M |
| `src/sspec/templates/skills/sspec-align/SKILL.md` | refactor(protocol): rewrite two-level system; remove channel matrix | M |
| `src/sspec/templates/skills/sspec-design/SKILL.md` | refactor(protocol): keep gate at exit; remove sspec ask references | S |
| `src/sspec/templates/skills/sspec-plan/SKILL.md` | refactor(protocol): change exit from gate to report | S |
| `src/sspec/templates/skills/sspec-implement/SKILL.md` | refactor(protocol): keep gate at exit; remove sspec ask references | S |
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

### Behavior Contract

**BC-1: Project docs match current repository behavior**

Surface: project context and spec-docs read by future agents.

After:
- Project context reflects the actual stack, commands, and platform behavior.
- Existing spec-docs no longer contain stale facts.
- New spec-docs cover stable contracts that previously lived only in code.

### Implementation Changes

**docs(project): Refresh project context** - Update `.sspec/project.md` so the stable identity
layer matches the actual stack, command surface, and platform behavior.

**docs(spec-docs): Repair existing drift** - Correct stale facts in `skill-installation.md`,
`builtin-tools.md`, and `testing-standards.md`.

**docs(change): Add change lifecycle contract** - New spec-doc for `.sspec/changes/<dir>/` structure,
status parsing, archive moves, and reference rewrite behavior.

**docs(records): Add interaction record contracts** - New spec-doc for request and ask artifacts:
creation format, linking, answer persistence, archive rewrite.

**docs(commands): Add command registry contract** - New spec-doc for `.sspec/commands/registry.yaml`
and script strategy semantics.

**docs(agents): Add root AGENTS sync contract** - New spec-doc for the managed `SSPEC:START/END`
block ownership and update behavior.

Serves: BC-1.

### Scope Summary

| File | Change | Effort |
|------|--------|--------|
| `.sspec/project.md` | docs(project): refresh stack, key paths, conventions | S |
| `.sspec/spec-docs/skill-installation.md` | docs(spec-docs): correct workspace locations and link behavior | S |
| `.sspec/spec-docs/builtin-tools.md` | docs(spec-docs): document current tool inventory | S |
| `.sspec/spec-docs/testing-standards.md` | Remove dead modules, align expectations |
| `.sspec/spec-docs/change-lifecycle.md` | New: change directory and status contract |
| `.sspec/spec-docs/interaction-records.md` | New: request/ask file format contract |
| `.sspec/spec-docs/cmd-registry.md` | New: command registry contract |
| `.sspec/spec-docs/agents-sync.md` | New: root AGENTS.md managed block contract |
```

For a pure docs change like this, design.md is typically not needed — the Behavior Contract,
Implementation Changes, and Scope Summary already give the user full predictability. Create design.md only if the
new doc content itself has structural complexity worth showing upfront (e.g. a new spec-doc
with a non-obvious schema).
