<!-- SSPEC:START -->
# .sspec Agent Protocol

SSPEC_SCHEMA::{{SCHEMA_VERSION}}

## 0. Overview

SSPEC is a document-driven AI collaboration framework. All planning, tracking, and handover lives in `.sspec/`.

**Goal**: Any Agent resumes work within 30 seconds by reading `.sspec/` files.

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

| Input | Action |
|-------|--------|
| Directive (`@resume`, `@handover`, etc.) | Execute → §4 Shortcuts |
| Request (attached or described) | Assess scale → Change Workflow §2 |
| Resume existing change | `read(handover→tasks→spec)` → continue from where left off |
| Micro task (≤3 files, ≤30min, obvious) | Do directly, no change needed |

**Background rules** (always active):
- Important discovery → write to `handover.md` immediately
- Long session (>20 exchanges) → checkpoint `handover.md`
- Uncertain → `@ask` (30s question < hours of rework)
- Session ending → `sspec-handover` MANDATORY
- User rejects tool call → STOP → `@ask` reason

---

## 2. Change Workflow

### Development Lifecycle

Each phase has a dedicated SKILL. Read the SKILL before starting the phase.

```
Request ─→ research ─→ design ──→ plan ──→ implement ──→ review ──→ done
              │           │          │          │            │
           understand   @ask       @ask      execute      @ask
           problem      align      approve   tasks       feedback
           space        design     tasks                  loop
```

### Phase → SKILL → Files

| Phase | SKILL | Reads | Writes | Checkpoint |
|-------|-------|-------|--------|------------|
| **Research** | `sspec-research` | code, project.md, spec-docs | reference/, handover.md | @ask "ready to design?" |
| **Design** | `sspec-design` | research findings, code | spec.md (A+B) | **@ask align** (MANDATORY) |
| **Plan** | `sspec-plan` | spec.md B | tasks.md | **@ask approve** (MANDATORY) |
| **Implement** | `sspec-implement` | spec.md B, tasks.md | code, tasks.md progress | **@ask "done, please review"** |
| **Review** | `sspec-review` | user feedback | tasks.md (feedback tasks) | @ask "satisfied?" |
| **Handover** | `sspec-handover` | everything | handover.md, project.md | — |

**MANDATORY checkpoints**: Design and Plan phases MUST @ask user before proceeding. Never skip.

### Scale Assessment (in Design phase)

| Scale | Criteria | Path |
|-------|----------|------|
| Micro | ≤3 files, ≤30min, trivially reversible | Do directly |
| Single | ≤1 week, ≤15 files, ≤20 tasks | `sspec change new <name>` |
| Multi | >1 week OR >15 files OR >20 tasks | `sspec change new <name> --root` → sub-changes |

### Status Transitions

| From | Trigger | To |
|------|---------|-----|
| PLANNING | user approves design+plan | DOING |
| DOING | all tasks `[x]` | REVIEW |
| DOING | missing info | BLOCKED |
| DOING | scope changed | PLANNING |
| REVIEW | accepted | DONE |
| REVIEW | needs changes | DOING |

**FORBIDDEN**: PLANNING→DONE, DOING→DONE — never skip REVIEW.

---

## 3. Consultation (@ask)

| Need persistent record? | Tool | Use when |
|--------------------------|------|----------|
| Yes | `sspec ask create` → fill → `sspec ask prompt` | Plan approval, architecture choice, direction decision |
| No | Agent env question tool | Quick yes/no, session-end check |

Default to `sspec ask` when uncertain — a record beats no record.

📚 Full workflow and patterns: `sspec-ask` SKILL

---

## 4. Reference

### Directive Shortcuts

| Shortcut | Equivalent | Procedure |
|----------|-----------|-----------|
| `@change <n>` | "Work on change N" | Load: `read(handover→tasks→spec)` → continue |
| `@resume` | "Continue last work" | Same as `@change` for active change |
| `@handover` | "Save and end" | Execute `sspec-handover` procedure |
| `@sync` | "I coded without tracking" | Update tasks.md/handover.md to match reality |
| `@argue` | "I disagree" | **STOP** → assess scope (§2 Review) |

### Scope Quick Reference

| Scope | Location | CLI |
|-------|----------|-----|
| Changes | `.sspec/changes/<n>/` | `sspec change new/find/list/archive` |
| Requests | `.sspec/requests/` | `sspec request new/find/link` |
| Spec-Docs | `.sspec/spec-docs/` | `sspec doc new "<name>"` |
| Asks | `.sspec/asks/` | `sspec ask create/prompt/list` |

### SKILL System

| SKILL | When to Read |
|-------|-------------|
| `sspec-research` | Starting investigation of a problem |
| `sspec-design` | Creating a change, filling spec.md |
| `sspec-plan` | Breaking design into tasks |
| `sspec-implement` | Executing tasks |
| `sspec-review` | Handling user feedback |
| `sspec-handover` | Saving session state |
| `sspec-ask` | Consulting user mid-work |
| `sspec-mdtoc` | Pre-scanning large Markdown files |
| `write-spec-doc` | Creating spec-docs |
| `write-patch` | Patch-based code modifications |

SKILLs are self-contained. Read the one you need for the current phase — no chaining required.

### Template Markers

| Marker | Meaning | Action |
|--------|---------|--------|
| `<!-- @RULE: ... -->` | Standards reminder | Read and follow. DO NOT delete |
| `<!-- @REPLACE -->` | Anchor for first edit | Replace with content |
| `[ ]` / `[x]` | Task todo / done | Update as work progresses |
<!-- SSPEC:END -->
