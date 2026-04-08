<!-- SSPEC:START -->
# .sspec Agent Protocol

SSPEC_SCHEMA::{{SCHEMA_VERSION}}

## 0. Overview

SSPEC is a doc-driven workflow. Planning, tracking, and handover live in `.sspec/`.

**Goal**: Any Agent resumes in 30 seconds from `.sspec/`.

**Normative language**: MUST, SHOULD, MAY etc. follow BCP 14 (RFC 2119 / RFC 8174).

```
.sspec/
├── project.md     # Identity, conventions, notes
├── spec-docs/     # Formal specs (architecture, APIs)
├── changes/<n>/   # spec.md | handover.md [+ design.md | tasks.md | revisions/ | reference/]
├── requests/      # User intent records
└── tmp/           # Informal drafts
```

---

## 1. Core Principle

**Human-led, agent-accelerated.** The user MUST be able to predict what the code will look like before implementation begins. When uncertain, align — 30 seconds of alignment saves hours of rework.

---

## 2. Agent Procedure

`read(project.md)` → classify → dispatch:

| Input | Action |
|-------|--------|
| Directive (`@resume`, `@handover`, etc.) | Execute → §5 |
| Request (attached or described) | Assess scale → §3 |
| Resume existing change | `read(handover→tasks→spec)` → continue |
| Micro task (≤3 files, ≤30min, obvious) | Do directly — no change, no @align gates |

**Background rules**:
- Important discovery → write to `handover.md` immediately
- Long session (>30 exchanges) → checkpoint `handover.md`
- Current date/time uncertain → `sspec tool now`

---

## 3. Change Workflow

### Lifecycle

Each phase has a dedicated SKILL. Read it before starting.

```
Research → sspec-research
  output: aligned understanding, reference/ notes
  exit: alignment checkpoint

Design → sspec-design
  output: spec.md [+ design.md]
  exit: @align gate (MUST wait)
  rule: after gate, spec.md/design.md baselines are immutable;
        subsequent changes go through revisions/NNN-*.md

Plan → sspec-plan
  output: tasks.md
  exit: @align report (continue)

Implement → sspec-implement
  output: code, tasks.md progress
  exit: @align gate (MUST wait)

Review → sspec-review
  satisfied    → Handover (DONE)
  minor-fix    → Implement → Review
  amend        → revisions/NNN-*.md + tasks.md update → Implement
  follow-up    → @align user → current DONE → new change (prev-change ref)
  supersede    → @align user → current BLOCKED → new change

Handover → sspec-handover
  output: handover.md, project.md
  trigger: MUST at session end; SHOULD mid-session (>30 exchanges, phase switches)
```

**Flow rules**: Follow phase order. `gate` = hard stop, MUST pass. `report` = output summary, keep going. Failed gate → return to phase, update, realign.

→ `sspec howto handle-review-scope-change`

### Scale Assessment

| Scale | Criteria | Path |
|---|---|---|
| Micro | ≤3 files, ≤30min, trivially reversible | Do directly |
| Single | ≤1 week, ≤15 files, ≤20 tasks | `sspec change new <name>` |
| Multi | >1 week OR >15 files OR >20 tasks | `sspec change new <name> --root` → sub-changes |

### Status Guardrails

`Status` in `spec.md` MUST follow the state machine. → `sspec howto update-change-status`

---

## 4. Alignment (@align)

| Level | Agent behavior | When to use |
|-------|---------------|-------------|
| `report` | Output summary, **keep going** | Plan done, progress updates |
| `gate` | Output summary, **stop and wait** | Design done, Implement done, scope changes, blockers, ambiguity |

Decisions go in their natural home: design → `spec.md`, direction changes → `handover.md` Durable Memory, user feedback → `handover.md` Session Log.

📚 Gate mechanics and patterns: `sspec-align` SKILL

---

## 5. Reference

### Directives

`@change <n>` load or create | `@resume` active change | `@handover` save state | `@sync` reconcile files | `@argue` stop + reassess scope | `@subagent-audits` independent review

### Spec-Docs

Architecture knowledge that outlives a single change. When change is DONE with architecture impact → `@align` user about creating/updating a spec-doc. → `write-spec-doc` SKILL

### CLI

| Command | Use |
|---------|-----|
| `sspec change new <name> [--from <REQ>]` | Create change (add `--root` for multi) |
| `sspec change find/status <name>` | Inspect change state |
| `sspec doc new "<name>"` | Create spec-doc |
| `sspec howto [name...]` | Read HOWTOs (batch supported) |
| `sspec tool <name> [opts]` | CLI tool complement (see below) |

**sspec tool** — `sspec tool <name> --prompt` for detailed usage:

- `now`: current time (MUST use for handover)
- `ask`: question user (fallback when no built-in question tool)
- `mdtoc`: markdown outline / structure
- `view-tree`: directory tree
- `fileinfo`: file size / encoding / newline style
- `patch/write`: edit / write files (only if lacking built-in capability)
- `treesitter`: analyze py/ts/js code

### HOWTO & SKILL

**HOWTO**: Micro-guides for specific operations. `sspec howto list` to browse; batch-read with `sspec howto read <n1> <n2>`.

**SKILL**: Read the SKILL for the current phase before starting. If a SKILL references a file → **MUST** read it. If a SKILL mentions `sspec howto xxx` → load on-demand.

### Template Markers

`<!-- @RULE -->` standards reminder | `<!-- @REPLACE -->` first edit anchor | `[ ]`/`[x]` task progress
<!-- SSPEC:END -->
