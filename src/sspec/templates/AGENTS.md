<!-- SSPEC:START -->
# .sspec Agent Protocol

SSPEC_SCHEMA::{{SCHEMA_VERSION}}

## 0. Structure

A spec-driven workflow, via `sspec` CLI and `.sspec/`.

```
.sspec/
├── project.md     # Identity, conventions, notes
├── spec-docs/     # Formal specs (architecture, APIs)
├── changes/<n>/   # spec.md | tasks.md | memory.md [+ design.md | revisions/ | reference/]
├── requests/      # User intent records
└── tmp/           # Informal drafts
```

**Principle**:

- The user MUST be able to predict what the code will look like before implementation begins.
- When uncertain, talk with user for clarification.

## 1. Dispatch

`read(project.md)` → classify → act:

| Input | Action |
|-------|--------|
| Directive (`@resume`, `@memory`, etc.) | Execute → §4 |
| Request under `.sspec/requests` | Assess scale → §2 |
| Resume existing change | `read(memory→tasks→spec)` → continue |
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
| revision | See `sspec-review`, run `sspec change scaffold revision` |
| mini change, 不要 change, 直接推进 | §2.0 |

**Standing rules**:
- Agent MUST NOT implement before user can predict the result — when uncertain, @align.
- Important discovery → `memory.md` Knowledge immediately
- Session end → MUST update memory.md (State + Milestones) · `sspec howto write-memory`
- @align gate decisions → SHOULD update memory.md Knowledge
- Time uncertain → `sspec tool now`

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

Format: tables / labeled items / code blocks. Prose @align = anti-pattern. 5-second scan, instant decision.
End with atomic decision question (use `question`-like tool if available).
Decisions → natural home: design → spec.md, direction → memory.md Knowledge.
📚 Full mechanics: `sspec-align` SKILL

## 4. Reference

**Directives**: `@change <n>` | `@resume` | `@memory` | `@sync` | `@argue` | `@subagent-audits`

**Spec-Docs**: Architecture knowledge outliving changes. DONE + arch impact → @align about spec-doc. → `write-spec-doc` SKILL

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
  Frequent Used: `now`, `mdtoc`, `view-tree`; See `sspec tool <name> --prompt` for usage.

**HOWTO**: `sspec howto list` to browse; batch-read with `sspec howto read <n1> <n2>`.
**SKILL**: Read before starting phase. Referenced file → MUST read. `sspec-*` not loaded → find under `.sspec/skills/`.

**Template markers**:

| Marker | Meaning | Agent action |
|--------|---------|-------------|
| `<!-- @RULE:... -->` | Structural constraint | Read, obey, keep marker |
| `<!-- @REPLACE:... -->` | First-edit anchor | Replace with content, delete marker |
| `[ ]` / `[x]` | Task progress | Mark `[x]` on completion |

**Fence nesting**: When showing content that contains ` ``` `, outer fence MUST use more backticks (e.g. `````). Always outer > inner.
<!-- SSPEC:END -->
