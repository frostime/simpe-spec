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
| Directive (`@resume`, `@handover`, etc.) | Execute → §5 Shortcuts |
| Request (attached or described) | Assess scale → Change Workflow §2 |
| Resume existing change | `read(handover→tasks→spec)` → continue from where left off |
| Micro task (≤3 files, ≤30min, obvious) | Do directly, no change needed |

**Background rules** (always active):
- Important discovery → write to `handover.md` immediately
- Long session (>20 exchanges) → checkpoint `handover.md`
- Uncertain → `@ask` (30s question < hours of rework)
- User rejects tool call → STOP → `@ask` reason

---

## 2. Change Workflow

### Development Lifecycle

Each phase has a dedicated SKILL. Read the SKILL before starting the phase.

```
Request ─→ research ─→ design ──→ plan ──→ implement ──→ review ──→ handover
              │           │          │          │            │          │
           understand   @ask       @ask      execute      @ask      persist
           problem      align      approve   tasks       feedback   session
           space        design     tasks                  loop      state
```

**Handover** is not just session-end cleanup — it's a lifecycle participant. Trigger it:
- At session end (MANDATORY)
- Mid-session when context is long (>30 exchanges)
- When switching between major phases
- Before any context-losing event (compression, interruption)

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
Long content → write to `.sspec/tmp/`, reference path in question body.

📚 Full workflow, patterns, and content rules: `sspec-ask` SKILL

---

## 4. Spec-Docs

Spec-docs capture architecture knowledge that survives beyond any single change.

**When to create/update spec-docs**:
- After a change produces architectural knowledge (new interfaces, data models, design patterns)
- When the agent discovers knowledge too complex for `project.md` Notes
- When user explicitly requests documentation

**Two scenarios**:

| Scenario | Trigger | Action |
|----------|---------|--------|
| Post-change update | Change is DONE, produced architectural knowledge | Agent proactively `@ask`: "Should I update/create spec-doc for X?" |
| User-initiated | User requests spec-doc creation | If small → do directly; if large → may need its own change |

📚 Full guidelines: `write-spec-doc` SKILL

---

## 5. Reference

### Directive Shortcuts

| Shortcut | Equivalent | Procedure |
|----------|-----------|-----------|
| `@change <n>` | "Work on change N" | Load: `read(handover→tasks→spec)` → continue |
| `@resume` | "Continue last work" | Same as `@change` for active change |
| `@handover` | "Save and end" | Execute `sspec-handover` procedure |
| `@sync` | "I coded without tracking" | Update tasks.md/handover.md to match reality |
| `@argue` | "I disagree" | **STOP** → assess scope (§2 Review) |

### CLI Quick Reference

Common `sspec` commands. Run `sspec <command> --help` for full options.

| Command | Purpose | Example |
|---------|---------|---------|
| `sspec change new <name>` | Create single change | `sspec change new fix-auth` |
| `sspec change new <name> --root` | Create root (multi) change | `sspec change new refactor --root` |
| `sspec change new --from <req>` | Create from request (auto-link) | `sspec change new --from .sspec/requests/...` |
| `sspec change find <name>` | Fuzzy-find change dir | `sspec change find auth` |
| `sspec change list` | List all active changes | |
| `sspec change archive <path>` | Archive completed change | |
| `sspec request list` | List requests | |
| `sspec doc new "<name>"` | Create spec-doc | `sspec doc new "auth-design"` |
| `sspec ask create <topic>` | Create ask file | `sspec ask create cache_approach` |
| `sspec ask prompt <path>` | Collect user answer | Combo: create → edit → prompt |
| `sspec ask list` | List asks | |
| `sspec tool mdtoc <file>` | Pre-scan Markdown (headings + sizes) | |

### Scope Quick Reference

| Scope | Location | Key Actions |
|-------|----------|-------------|
| Changes | `.sspec/changes/<n>/` | `new`, `find`, `list`, `archive` |
| Requests | `.sspec/requests/` | `new`, `find`, `link` |
| Spec-Docs | `.sspec/spec-docs/` | `new` |
| Asks | `.sspec/asks/` | `create` → `prompt`, `list` |

### SKILL System

Each SKILL is self-contained — read the one you need for the current phase, no chaining required.
When a SKILL.md says "read [reference](./references/file.md)" → you **MUST** follow and read it.

| SKILL | When to Read |
|-------|-------------|
| `sspec-research` | Starting investigation of a problem |
| `sspec-design` | Creating a change, filling spec.md |
| `sspec-plan` | Breaking design into tasks |
| `sspec-implement` | Executing tasks |
| `sspec-review` | Handling user feedback |
| `sspec-handover` | Saving session state (end-of-session or mid-session) |
| `sspec-ask` | Consulting user mid-work |
| `sspec-mdtoc` | Pre-scanning large Markdown files |
| `write-spec-doc` | Creating spec-docs |
| `write-patch` | Patch-based code modifications |

### Template Markers

| Marker | Meaning | Action |
|--------|---------|--------|
| `<!-- @RULE: ... -->` | Standards reminder | Read and follow. DO NOT delete |
| `<!-- @REPLACE -->` | Anchor for first edit | Replace with content |
| `[ ]` / `[x]` | Task todo / done | Update as work progresses |
<!-- SSPEC:END -->
