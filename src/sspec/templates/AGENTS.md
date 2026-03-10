<!-- SSPEC:START -->
# .sspec Agent Protocol

SSPEC_SCHEMA::{{SCHEMA_VERSION}}

## 0. Overview

SSPEC is a doc-driven workflow. Planning, tracking, and handover live in `.sspec/`.

**Goal**: Any Agent resumes in 30 seconds from `.sspec/`.

```
.sspec/
├── project.md     # Identity, conventions, notes
├── spec-docs/     # Formal specs (architecture, APIs)
├── changes/<n>/   # spec.md | tasks.md | handover.md [+ reference/]
├── requests/      # User intent records
├── tmp/           # Informal drafts
└── asks/          # Q&A decision records
```

---

## 1. Agent Procedure

`read(project.md)` → classify → dispatch:

SPEC activation signals (enter Change Workflow §2): request file attached, user explicitly asks for SSPEC workflow, or SSPEC directives used (`@resume`, `@change`, etc.).

| Input | Action |
|-------|--------|
| Directive (`@resume`, `@handover`, etc.) | Execute → §5 Shortcuts |
| Request (attached or described) | Assess scale → Change Workflow §2 |
| Resume existing change | `read(handover→tasks→spec)` → continue |
| Micro task (≤3 files, ≤30min, obvious) | Do directly, no change needed |

Resume tip: Run `sspec howto resume-change`

**Background rules**:
- Important discovery → write to `handover.md` immediately
- Long session (>30 exchanges) → checkpoint `handover.md`
- Uncertain → `@align` (30s alignment < hours of rework) → `sspec howto use-sspec-ask`
- User rejects tool call → STOP → `@align` reason
- Current date/time uncertain → use sspec tool now instead of guessing → `sspec howto get-current-time`

→ **HOWTOs**: narrow operational guides for specific operations. `sspec howto list` to browse; batch-read: `sspec howto n1 n2`.

---

## 2. Change Workflow

### Development Lifecycle

Each phase has a dedicated SKILL. Read it before starting.

```text
[Request]
   |
   v
[Research]  (understand + clarify; @align mid-research for ambiguities)
   |
   v
[Design]    -- @align gate (MANDATORY) + [Handover] --> "Align understanding + solution"
   |
   v
[Plan]      -- @align gate (LIGHTWEIGHT) --> "Confirm task breakdown"
   |
   v
[Implement] -- @align gate (MANDATORY) --> "Done for this round, please review"
   |
   v
[Review]    -- user feedback + [Handover] --> (if not satisfied, return to Implement)
   |
   +-- satisfied --> [Handover]
```

**Flow rules**: Follow phase order. `@align` gates are hard stops — must pass before proceeding. Failed gate → return to phase, update, realign. `Implement` and `Review` loop until user satisfied.

**Handover** is lifecycle-critical — mandatory at session end, also at long sessions (>30 exchanges), major phase switches, and before context-losing events.

### Phase Contracts

Read the SKILL for the current phase. Unless the SKILL says otherwise, each phase reads prior outputs plus relevant code, `project.md`, and `spec-docs`.

| Phase | SKILL | Main output | Gate |
|-------|-------|-------------|------|
| **Research** | `sspec-research` | `reference/`, `handover.md` notes | optional `question` |
| **Design** | `sspec-design` | `spec.md` | **@align** mandatory |
| **Plan** | `sspec-plan` | `tasks.md` | lightweight confirm |
| **Implement** | `sspec-implement` | code, `tasks.md` progress | **@align** mandatory |
| **Review** | `sspec-review` | feedback tasks / acceptance loop | rejected -> Implement |
| **Handover** | `sspec-handover` | `handover.md`, `project.md` | session end required |
### Scale Assessment (in Design phase)

| Scale | Criteria | Path |
|---|---|---|
| Micro | ≤3 files, ≤30min, trivially reversible | Do directly |
| Single | ≤1 week, ≤15 files, ≤20 tasks | `sspec change new <name>` |
| Multi | >1 week OR >15 files OR >20 tasks | `sspec change new <name> --root` → sub-changes |

### Status Guardrails

`Status` key in `spec.md` should follow a state machine rule, see
→ `sspec howto update-change-status`

---
## 3. Alignment (@align)

`@align` means the Agent proactively aligns with the User, through:
- Built-in tools such as `AskUserQuestion` (e.g. `vscode/askQuestion`, `opencode/question`)
- The `sspec ask` CLI tool

**Choose by question type**:
- Simple, bounded confirmation -> `question` tool
- Open-ended, tradeoff-heavy, or worth recording -> `sspec ask`
- Design / Implement phase gates -> `sspec ask` (mandatory)
- Plan confirmation or mid-research clarification -> `question` tool
- If no `question`-like tool is available -> use `sspec ask`

📚 Full flow and recording procedure: `sspec howto use-sspec-ask` | skeleton/template: `sspec howto write-sspec-ask`

For large context, write analysis to `.sspec/tmp/` and link it from the question body. Move confirmed valuable materials to `change/reference/` later.

→ `@force-end-align` directive: Do one last user-facing alignment instead of silently ending the turn when the agent believes the work is done, see `sspec howto force-end-align`. !IMPORTANT

At phase gates: Design + Implement are mandatory, Plan is lightweight, Review loops until satisfied.

📚 Full workflow, patterns, and content rules: `sspec-align` SKILL

---

## 4. Spec-Docs

Spec-docs store architecture knowledge that should outlive a single change.

Create/update spec-docs when a change produces architectural knowledge or the user explicitly requests it.
When change is DONE with architecture impact → proactively `@align` user: "Should I create/update a spec-doc for X?"

📚 Full guidelines: `write-spec-doc` SKILL

---

## 5. Reference

### Directive Shortcuts

| Shortcut | Action |
|----------|--------|
| `@change <n>` | Load `handover→tasks→spec`, continue; OR create if not exists `<n>` |
| `@resume` | Same as `@change` for active change |
| `@handover` | Execute `sspec-handover` |
| `@sync` | Update tasks.md/handover.md to match reality |
| `@argue` | **STOP** -> assess scope (§2 Review) |

### CLI Quick Reference

Run `sspec <command> --help` for full options. Keep this list minimal:

| Command | Use |
|---------|-----|
| `sspec change new <name> [--from <REQUEST>]` | Create a change |
| `sspec change status <name>` | Inspect current change state |
| `sspec ask create <topic>` + `sspec ask prompt <path>` | Create and ask |
| `sspec doc new "<name>"` | Create spec-doc |
| `sspec tool mdtoc <file>` | Pre-scan Markdown |
| `sspec tool now [--date|--utc|--json]` | Show current time when timestamps matter |
| `sspec howto list` | Browse operational micro-guides |

### HOWTO System

Targeted operational micro-guides — shorter than SKILLs, more specific than AGENTS.md. HOWTOs cover low-frequency rules and edge cases so they stay out of the core docs until needed.
- Discover all: `sspec howto list`
- Read: `sspec howto <name>` (batch supported: `sspec howto read <n1> <n2>` to parallel-read multiple HOWTOs)
- Project-local HOWTOs: `sspec howto new <name>` → `.sspec/howto/`

### SKILL System

Read the SKILL for the current phase (`sspec-research`, `sspec-design`, `sspec-plan`, `sspec-implement`, `sspec-review`, `sspec-handover`, `sspec-align`, `sspec-mdtoc`, `write-spec-doc`).
If a SKILL says "read [file](...)" -> **MUST** read it.

Some rules in SKILL are distributed to HOWTOs. If you see `sspec howto xxx` in SKILL content, read it with `sspec howto <name>` or batch-read with `sspec howto read <n1> <n2>...`.

### Template Markers

- `<!-- @RULE: ... -->`: standards reminder — read and follow
- `<!-- @REPLACE -->`: anchor for first edit — replace with content
- `[ ]` / `[x]`: task todo / done — keep progress updated
- <!-- SSPEC:END -->
