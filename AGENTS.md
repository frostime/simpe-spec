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

SSPEC_SCHEMA::6.0

## 0. Structure

A spec-driven workflow, via `sspec` CLI and `.sspec/`.

```
.sspec/
├── project.md     # Identity, conventions, notes
├── spec-docs/     # Knowledge: in-code-but-scattered or outside-code
├── changes/<n>/   # spec.md | tasks.md | memory.md [+ design.md | revisions/ | reference/]
├── requests/      # User intent records
└── tmp/           # Informal drafts
```

## 1. Dispatch

`read(project.md)` → classify → act:

| Input | Action |
|-------|--------|
| Directive (`@resume`, `@memory`, etc.) | Execute → §4 |
| Request under `.sspec/requests` | Assess scale → §2 |
| Resume existing change | `read(memory)` → infer phase from State → load phase SKILL → continue |
| Micro (≤3 files, ≤30min, obvious) | Do directly |
| Mini (user opts out of formal change) | Clarify+Design thinking → `.sspec/tmp/` → §2.0 |

**Trigger-word → SKILL**:

| User says | Load |
|-----------|------|
| clarify, 搞清楚, 理解一下 | `sspec-clarify` |
| design, 设计, 出方案 | `sspec-design` |
| align, 对齐, 确认一下 | §3 protocol |
| plan, 拆任务 | `sspec-plan` |
| implement, 动手, 开始做 | `sspec-implement` |
| review, 检查, 看看 | `sspec-review` |
| mini change, 不要 change, 直接推进 | §2.0 |

**Standing rules**:
- The user MUST be able to predict what the code will look like before implementation begins. When uncertain, @align.
- Important discovery → `memory.md` Knowledge immediately
- Session end → MUST update memory.md (State + Milestones) · `sspec howto write-memory`
- @align gate decisions → SHOULD update memory.md Knowledge
- Time uncertain → `sspec tool now`
- Template HTML comments with BCP 14 keywords (MUST, SHOULD, MAY per RFC 2119) are persistent constraints — never delete them.

## 2. Change Lifecycle

Each phase has a SKILL. MUST read it before starting.

```
Clarify  (sspec-clarify)    posture, reusable       exit: ready for spec
Design   (sspec-design)     spec.md [+design.md]    exit: @align gate ■
Plan     (sspec-plan)       tasks.md                exit: @align report →
Implement(sspec-implement)  code + tasks progress   exit: @align gate ■
Review   (sspec-review)     DONE | fix→Implement | amend→revision | follow-up→new change
```

`■` = hard stop, MUST align. `→` = output summary, keep going. Failed gate → return, update, realign.
Post-Design gate: spec.md/design.md baselines immutable. Changes → `revisions/NNN-*.md`.
memory.md: maintained throughout, not a phase. → `sspec howto write-memory`

→ `sspec howto handle-review-scope-change`

### 2.0 Mini Change Protocol

Clarify/Design thinking without change entity. Output → `.sspec/tmp/`.

Trigger: user explicitly opts out of formal change.
Flow: clarify → design-level output → `sspec tmp new <topic>` → no gates, no tasks, no memory.
Boundary: no code changes. If implementation needed → upgrade to change or confirm Micro.
Agent MUST NOT self-downgrade to mini — only responds to user intent.

### Scale

| Scale | Criteria | Path |
|---|---|---|
| Micro | ≤3 files, ≤30min, trivially reversible | Do directly |
| Single | ≤1 week, ≤15 files, ≤20 tasks | `sspec change new <name>` |
| Multi | >1 week OR >15 files OR >20 tasks | `sspec change new <name> --root` → sub-changes |

Status in spec.md MUST follow state machine. → `sspec howto update-change-status`

## 3. @align

Structured sync at decision points. **Formalized exchange, not prose.**

| Level | Behavior | When |
|---|---|---|
| `report` | Summary, **keep going** | Plan done, progress |
| `gate` | Summary, **stop and wait** | Design done, implement done, blockers, scope change |

Decisions → natural home: design → spec.md, direction → memory.md Knowledge.
📚 Full mechanics: `sspec-align` SKILL

## 4. Reference

**Directives**: `@change <n>` | `@resume` | `@memory` | `@sync` | `@argue` | `@subagent-audits`

**Spec-Docs**: Knowledge that code alone cannot adequately convey — either in code but scattered or hard to reconstruct (cross-module architecture, UX requirements, design norms, deliberate trade-offs), or entirely outside code (platform rules, API quirks, business constraints). Registered in `project.md` Spec-Docs Index. → `write-spec-doc` SKILL

**CLI**:

| Command | Use |
|---------|-----|
| `sspec change new <name> [--from REQ] [--root] [--scaffold design]` | Create change |
| `sspec change scaffold <type> <change>` | Add file: tasks, design, revision |
| `sspec change find/status <name>` | Inspect change |
| `sspec doc new "<name>"` | Create spec-doc |
| `sspec howto [name...]` | Read HOWTOs (batch) |
| `sspec tool <name> [opts]` | CLI tools (`--prompt` for usage) |

**Tools** (`sspec tool <name>`): `now` · `ask` · `mdtoc` · `view-tree` · `fileinfo` · `patch/write` · `treesitter`
  Frequent: `now`, `mdtoc`, `view-tree`; See `sspec tool <name> --prompt` for usage.

**HOWTO**: `sspec howto list` to browse; batch-read with `sspec howto read <n1> <n2>`.
**SKILL**: Read before starting phase. Referenced file → MUST read. `sspec-*` not loaded → find under `.sspec/skills/`.

**Fence nesting**: When showing content that contains ` ``` `, outer fence MUST use more backticks (e.g. `````). Always outer > inner.
<!-- SSPEC:END -->
