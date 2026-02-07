---
name: sspec
description: Decision framework for SSPEC workflow. Assess work scale, route knowledge, handle edge cases. Consult when AGENTS.md says to.
metadata:
  author: frostime
  version: 7.1.0
---

# SSPEC Skill

Core protocol lives in AGENTS.md. This SKILL provides judgment for decisions AGENTS.md can't make.

## Playbook

| You need to... | Action |
|----------------|--------|
| Start single change | Assess Scale → fill docs per [doc-standards] → [checklists] |
| Start multi-change | Assess Scale → [multi-change] → fill root docs → [checklists] |
| Fill or review spec/tasks/handover | Read [doc-standards] |
| Check before status transition | Read [checklists] |
| Decide where knowledge belongs | Knowledge Routing below |
| Handle blockers, rejection, etc. | Edge Cases below |

---

## Assess Scale

How big is this work?

**Micro** — ALL of: ≤3 files, ≤30min, no design decisions, trivially reversible.
→ Do directly or track in request file (`## Plan` / `## Done`). No change.

**Single** — ALL of: ≤1 week, ≤15 files in one subsystem, ≤20 tasks, low risk.
→ Standard change workflow. Fill spec.md/tasks.md/handover.md.

**Multi** — ANY of: >1 week, >15 files across subsystems, >20 tasks, high risk.
→ Root change (`--root`) + sub-changes. Read [multi-change](./references/multi-change.md) first.

**Uncertain?** Use `@ask` to consult user on splitting.

---

## Knowledge Routing

Where does a piece of knowledge go?

| Test | → Destination |
|------|---------------|
| One-liner, applies across all work | `project.md` **Conventions** |
| Project-wide gotcha, preference, learning | `project.md` **Notes** (append with date) |
| Needs paragraphs, diagrams, or sections | `spec-docs/` |
| Only relevant to current change | `handover.md` **Conventions Discovered** |

**Notes lifecycle**: Append during `@handover` → Promote to Conventions if permanent → Prune if outdated → Graduate to spec-doc if it grows complex.

---

## Edge Cases

### Partial Blockers

- Blocked tasks are dependencies for remaining → BLOCKED, document in spec.md D
- Blocked tasks are non-critical → Continue others, note in spec.md D
- Ambiguous → Split into two changes

### REVIEW Across Sessions

Keep status REVIEW. Note "Awaiting review since \<date\>" in handover. Can start other work. Next session: prompt user for review first.

### Rejection (@argue)

AGENTS.md says STOP. Then assess scope of rejection:
- Implementation detail → update tasks.md only
- Design decision → revise spec.md B + regenerate tasks.md
- Requirement itself → revise spec.md A, mark PIVOT in D, transition DOING→PLANNING

### Multiple Active Changes

≤2 in DOING simultaneously. Switch: `@handover` current → `@change <other>` → read other's handover.

### Design Iteration Loop

spec.md keeps being revised → Archive current to `reference/spec-v1.md` → Brainstorm in `reference/` → Iterate via `@ask` → Write final to spec.md.

---

## References

| When | Load |
|------|------|
| Filling or reviewing documents | [doc-standards.md](./references/doc-standards.md) |
| Setting up or coordinating multi-change | [multi-change.md](./references/multi-change.md) |
| Checkpoint before any status transition | [checklists.md](./references/checklists.md) |
