# sspec Development Protocol

## 0. Self-Hosting Notice

This project uses sspec to develop sspec. Two sets of rules coexist:

| | This file (above SSPEC block) | SSPEC block (below) |
|---|---|---|
| Purpose | How to **develop** sspec | How to **use** sspec |
| Audience | Agent working on this repo | Agent using sspec in any project |
| Authority | **This file wins** on conflicts | Provides workflow structure |

**Rule**: When developing templates, the **template source files** in `src/sspec/templates/` are ground truth.

**Hard rule**: If a change touches AGENTS, SKILLs, or any template content, edit only `src/sspec/templates/`. Do **not** hand-edit `.github/`, `.claude/`, or `.sspec/` copies; refresh them with `uv run sspec project update`.

**Auto-managed rule**: The SSPEC block below `SSPEC:START` is generated from `src/sspec/templates/AGENTS.md`. If that block needs to change, update the template source and run `uv run sspec project update` instead of editing the block directly.

---

## 1. Cold Start (Development)

1. Read `.sspec/project.md` — tech stack, conventions, project notes.
2. Classify the request:

| User Message | Action |
|--------------|--------|
| `@resume` or `@change` | Load change context (follow SSPEC block below) |
| Template/SKILL change | Follow **Template Change Protocol** (Section 2) |
| Python code change | Follow **Code Change Protocol** (Section 3) |
| Bug report / feature idea | Follow SSPEC workflow in block below |

3. If touching an unfamiliar area, check `src/sspec/` structure:

```
src/sspec/
├── cli.py              # Entry point
├── core.py             # Shared types, constants, utilities
├── commands/           # CLI commands (project/change/ask/request/doc/tool/...)
├── services/           # Business logic (CLI-agnostic)
├── libs/               # Pure utilities (hashing, etc.)
└── templates/          # Product: what users get on `sspec init`
    ├── AGENTS.md       # ⭐ The protocol template
    ├── project.md      # Project context template
    ├── change/         # spec.md, tasks.md, handover.md
    ├── change-root/    # Root change variants
    ├── requests/       # Request template
    └── skills/         # User-facing SKILL templates
```

---

## 2. Template Change Protocol

Changing templates = changing the product. Extra care required.

### What counts as a template change
- Any file under `src/sspec/templates/`
- SKILL files under `src/sspec/templates/skills/`

### Workflow

1. Edit template source in `src/sspec/templates/`
2. Reinstall: `uv pip install -e .`  ← **必须，否则模板缓存不更新**
3. Sync self-hosted copies: `uv run sspec project update`
4. Test in sandbox:

```powershell
# Create clean test environment
cd tmp
mkdir test_<feature>
cd test_<feature>

# Test init
uv run sspec project init
# Verify: check generated files match expectations

# Test update (if applicable)
uv run sspec project update --dry-run
```

5. If template structure changed → check `UPDATABLE_FILES`, `USER_FILES` in `core.py`
6. If a skill was added/renamed/removed → verify both init/install flow in `project_init_service.py` and update/orphan flow in `project_update_service.py`

### Template editing rules

Templates use `{{VARIABLE}}` placeholders. Current variables:
- `{{SCHEMA_VERSION}}` — from `core.py:SCHEMA_VERSION`
- `{{TODO}}` — user fills after init
- `{{NAME}}`, `{{TIME}}`, `{{CHANGE_NAME}}` — CLI fills at creation

**Never** put development-specific content in templates. Templates are for users.

**Never** patch installed/generated copies under `.github/`, `.claude/`, or `.sspec/` by hand. Re-sync from template source.

---

## 3. Code Change Protocol

### After editing Python files

```powershell
uv pip install -e .          # Reinstall editable
uv run ruff check src/       # Lint
uv run ruff format src/      # Format
```

Then run focused verification for the behavior you changed (for example a targeted `uv run pytest ...` module and/or a `tmp/` CLI sandbox check).

### CLI testing pattern

```powershell
# Always test in tmp/ — never pollute project root
cd tmp/test_<feature>
uv run sspec <command>       # Test the command
```

### Key architectural rules

- `commands/` = CLI layer (click decorators, user I/O, output formatting)
- `services/` = business logic (no click, no rich — pure functions)
- `core.py` = shared types and constants (no business logic)
- Keep commands thin: validate input → call service → format output

### Windows terminal encoding rule

- Treat Windows GBK/cp936 terminals as a supported environment.
- Any CLI output path must not crash on non-UTF encodings.
- Keep `configure_stdio_error_fallback()` wired in CLI startup when refactoring entrypoints.
- For new symbols/emojis in user-facing text, verify behavior in legacy encodings or provide ASCII fallback.


---

## Git Commit

When user asks Agent to commit:

- Consult: git-commit-msg SKILL
- Write suitable commit msg
- If the change is too broad for one clean commit, ask whether to split it

---

<!-- ====================================================================
     Below: SSPEC protocol block, auto-managed by `sspec project update`.
     Provides the standard workflow (changes, requests, handover, etc.).
     When in doubt: Section 0 of this file defines precedence.
     ==================================================================== -->



<!-- SSPEC:START -->
# .sspec Agent Protocol

SSPEC_SCHEMA::5.0

## 0. Overview

SSPEC is a doc-driven workflow. Planning, tracking, and memory live in `.sspec/`.

**Goal**:
- **Harness**: Human takes in control with sspec
- **Trackable**: Agent make trackable work with sspec

**Normative language**: MUST, SHOULD, MAY etc. follow BCP 14 (RFC 2119 / RFC 8174).

```
.sspec/
├── project.md     # Identity, conventions, notes
├── spec-docs/     # Formal specs (architecture, APIs)
├── changes/<n>/   # spec.md | tasks.md | memory.md [+ design.md | revisions/ | reference/]
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
| Directive (`@resume`, `@memory`, etc.) | Execute → §5 |
| Request file under `.sspec/requests` (attached or described) | Assess scale → §3 |
| Resume existing change | `read(memory→tasks→spec)` → continue |
| Micro task (≤3 files, ≤30min, obvious) | Do directly — no change, no @align gates |

**Background rules**:
- Important discovery → write to `memory.md` Knowledge immediately
- Session ending → MUST update memory.md (State + Milestones) → `sspec howto write-memory`
- @align gate with new decisions → SHOULD update memory.md Knowledge
- Current date/time uncertain → `sspec tool now`

---

## 3. Change Workflow

### Lifecycle

Each phase has a dedicated SKILL. Read it before starting.

```phase
Clarify → sspec-clarify
  posture, not phase — reusable when understanding drifts
  output: Problem Statement + direction sketch, reference/ notes
  exit: ready to formalize into spec.md

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
  satisfied    → DONE (update memory.md State + Milestones)
  minor-fix    → Implement → Review
  amend        → revisions/NNN-*.md + tasks.md update → Implement
  follow-up    → @align user → current DONE → new change (prev-change ref)
  supersede    → @align user → current BLOCKED → new change
```

memory.md is a change-scoped memory store, maintained throughout the lifecycle (not a phase).
Triggers and format: `sspec howto write-memory`

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

Structured, efficient synchronization at decision points. **Formalized exchange, not prose.**

| Level | Agent behavior | When to use |
|-------|---------------|-------------|
| `report` | Structured summary, **keep going** | Plan done, progress updates |
| `gate` | Structured summary, **stop and wait** | Design done, Implement done, scope changes, blockers, ambiguity |

**Format rule**: @align MUST use structured format (tables, labeled items, code blocks). Prose-style @align is an anti-pattern. 5-second scan, instant decision.

Decisions go in their natural home: design → `spec.md`, direction changes → `memory.md` Knowledge, user feedback → `memory.md` Knowledge.

📚 Gate mechanics and patterns: `sspec-align` SKILL

---

## 5. Reference

### Directives

`@change <n>` load or create | `@resume` active change | `@memory` save state | `@sync` reconcile files (MUST NOT split/replace without @align) | `@argue` stop + reassess scope | `@subagent-audits` independent review

### Spec-Docs

Architecture knowledge that outlives a single change. When change is DONE with architecture impact → `@align` user about creating/updating a spec-doc. → `write-spec-doc` SKILL

### CLI

| Command | Use |
|---------|-----|
| `sspec change new <name> [--from <REQ>]` | Create change (default: spec.md + tasks.md + memory.md; add `--root` for multi, `--scaffold design` for extras) |
| `sspec change scaffold <type> <change>` | Add file to change: tasks, design, revision |
| `sspec change find/status <name>` | Inspect change state |
| `sspec doc new "<name>"` | Create spec-doc |
| `sspec howto [name...]` | Read HOWTOs (batch supported) |
| `sspec tool <name> [opts]` | CLI tool complement (see below) |

**sspec tool** — `sspec tool <name> --prompt` for detailed usage:

- `now`: current time (MUST use for memory updates)
- `ask`: question user (fallback when no built-in question tool)
- `mdtoc`: markdown outline / structure
- `view-tree`: directory tree
- `fileinfo`: file size / encoding / newline style
- `patch/write`: edit / write files (only if lacking built-in capability)
- `treesitter`: analyze py/ts/js code

### HOWTO & SKILL

**HOWTO**: Micro-guides for specific operations. `sspec howto list` to browse; batch-read with `sspec howto read <n1> <n2>`.

**SKILL**: Read the SKILL for the current phase before starting. If a SKILL references a file → **MUST** read it. If a SKILL mentions `sspec howto xxx` → load on-demand.
IF `sspec-*` skill not auto-loaded → list&find under `.sspec/skills/`

### Template Markers

`<!-- @RULE -->` standards reminder | `<!-- @REPLACE -->` first edit anchor | `[ ]`/`[x]` task progress
<!-- SSPEC:END -->
