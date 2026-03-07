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

SSPEC activation signals (enter Change Workflow §2 if any is true):
- User provides/references a request file (for example `.sspec/requests/...`)
- User explicitly asks to start SSPEC/change workflow
- User uses SSPEC directives (for example `@resume`, `@change`, `@handover`)

| Input | Action |
|-------|--------|
| Directive (`@resume`, `@handover`, etc.) | Execute → §5 Shortcuts |
| Request (attached or described) | Assess scale → Change Workflow §2 |
| Resume existing change | `read(handover→tasks→spec)` → continue |
| Micro task (≤3 files, ≤30min, obvious) | Do directly, no change needed |

Resume tip: in `handover.md`, start from the newest entry in `Session Log`.

**Background rules**:
- Important discovery → write to `handover.md` immediately
- Project-wide discovery → also append to `project.md` Notes
- Long session (>30 exchanges) → checkpoint `handover.md`
- Uncertain → `@align` (30s alignment < hours of rework)
- User rejects tool call → STOP → `@align` reason
- Current date/time uncertain → use sspec tool now instead of guessing

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

Flow rules:
- Follow phase order from `Request` to `Handover`.
- Any `@align` gate is a hard checkpoint: align with user first (`question` if available, else `sspec ask`).
- `@align` is a closed loop: if not approved, return to the required phase, update, and align again.
- `Implement` and `Review` are coupled: deliver -> align -> feedback -> implement -> align again, until satisfied.

**Handover** is lifecycle-critical. Trigger it:
- At session end (MANDATORY)
- Mid-session when context is long (>30 exchanges)
- When switching between major phases
- Before context-losing events (compression, interruption)

### Phase → SKILL → Files

| Phase | SKILL | Reads | Writes | Checkpoint |
|-------|-------|-------|--------|------------|
| **Research** | `sspec-research` | code, project.md, spec-docs | reference/, handover.md | `question` for mid-research clarifications (no formal gate) |
| **Design** | `sspec-design` | research findings, code | spec.md (A+B) | **@align** (MANDATORY) |
| **Plan** | `sspec-plan` | spec.md B | tasks.md | @align confirm breakdown (LIGHTWEIGHT) |
| **Implement** | `sspec-implement` | spec.md B, tasks.md | code, tasks.md progress | **@align "done for this round, please review"** (MANDATORY) |
| **Review** | `sspec-review` | user feedback | tasks.md (feedback tasks) | feedback loop: not satisfied -> Implement; satisfied -> Handover |
| **Handover** | `sspec-handover` | everything | handover.md, project.md | — |

### Scale Assessment (in Design phase)

| Scale | Criteria | Path |
|---|---|---|
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

## 3. Alignment (@align)

`@align` means the Agent proactively aligns with the User, through:
- Built-in tools such as `AskUserQuestion` (e.g. `vscode/askQuestion`, `opencode/question`)
- The `sspec ask` CLI tool

**Choose by question type**:

| Question type | Tool |
|---|---|
| Simple, bounded — yes/no, quick confirm | `question` tool |
| Complex/open-ended — context, tradeoffs, or worth recording | `sspec ask` |
| Phase gates (Design, Implement review) | `sspec ask` (mandatory) |
| Straightforward plan confirmation | `question` tool |
| Mid-research in-flight clarification | `question` tool |

If no `question`-like tool is available → use `sspec ask`.

**For large context**: Write design/research analysis to `.sspec/tmp/` and link it from the question body. Move confirmed valuable materials to `change/reference/` later.

**Directive: `@force-end-align`**: If a task explicitly requests it, and you believe the work is done, do one last user-facing alignment instead of silently ending the turn. Prefer `question`; use `sspec ask` only if the final check also needs durable record or sign-off.

At phase gates: Design + Implement are mandatory, Plan is lightweight, Review loops until satisfied.

📚 Full workflow, patterns, and content rules: `sspec-align` SKILL

---

## 4. Spec-Docs

Spec-docs store architecture knowledge that should outlive a single change.

Create/update spec-docs when:
- A change produces architectural knowledge (interfaces, data models, patterns)
- When the agent discovers knowledge too complex for `project.md` Notes
- When user explicitly requests documentation

Scenarios:

| Scenario | Trigger | Action |
|----------|---------|--------|
| Post-change update | Change is DONE, with architecture impact | Agent proactively `@align`: "Should I update/create spec-doc for X?" |
| User-initiated | User requests spec-doc creation | If small → do directly; if large → may need its own change |

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

Run `sspec <command> --help` for full options.

| Command | Use |
|---------|-----|
| `sspec change new <name>` | Create a change |
| `sspec change new <name> --root` | Create a root change |
| `sspec change new --from <path>` | Create change from request file |
| `sspec change status <name>` | Quick local dashboard; open linked source files for detail |
| `sspec change list` / `find <name>` | Locate active changes |
| `sspec change archive <path>` | Archive completed change |
| `sspec ask create <topic>` + `sspec ask prompt <path>` | Create and ask |
| `sspec request list` / `sspec ask list` | List requests/asks |
| `sspec doc new "<name>"` | Create spec-doc |
| `sspec tool mdtoc <file>` | Pre-scan Markdown |
| `sspec tool now [--date|--utc|--json]` | Show current time when timestamps matter |

### SKILL System

Read the SKILL for the current phase (`sspec-research`, `sspec-design`, `sspec-plan`, `sspec-implement`, `sspec-review`, `sspec-handover`, `sspec-align`, `sspec-mdtoc`, `write-spec-doc`).
If a SKILL says "read [file](...)" -> **MUST** read it.

### Template Markers

| Marker | Meaning | Action |
|--------|---------|--------|
| `<!-- @RULE: ... -->` | Standards reminder | Read and follow. |
| `<!-- @REPLACE -->` | Anchor for first edit | Replace with content |
| `[ ]` / `[x]` | Task todo / done | Update as work progresses |
<!-- SSPEC:END -->
