<!-- SSPEC:START -->
# .sspec Agent Protocol

SSPEC_SCHEMA::{{SCHEMA_VERSION}}

## 0. Protocol Overview

SSPEC is a document-driven AI collaboration framework. All planning, tracking, and handover lives in `.sspec/`.

**Goal**: Any Agent resumes work within 30 seconds by reading `.sspec/` files.

**Folder Structure**:
```
.sspec/
├── project.md    # Identity, conventions, accumulated memory notes
├── spec-docs/    # Formal specifications (architecture, APIs, standards)
├── changes/<n>/    # Active change proposals
│   ├── spec.md | tasks.md | handover.md  # Required
│   └── reference/    # Optional
├── requests/    # Lightweight proposals (user intent record)
├── tmp/    # Informal proposals, plans, scripts, etc., for user review.
└── asks/    # Human-in-the-loop Q&A records (decision evidence)
```

---

## 1. Cold Start

When entering project in new session:

1. Read `.sspec/project.md` — identity, conventions, accumulated notes
2. Determine action:

| User Message | Action |
|--------------|--------|
| `@resume` or `@change` | Load that change's context |
| Micro task (≤3 files, ≤30min, obvious) | Do directly, no change ceremony |
| Vague request (idea/bug/feature) | Request → Change Workflow (Section 2.0) |
| Simple task, no directive | Do directly |

If touching unfamiliar subsystem → check `spec-docs/` | `project.md` | `<change>/handover.md`

---

## 2. SCOPE: Changes

Changes live in `.sspec/changes/<n>/`.

| File/Dir | Contains | Required |
|----------|----------|----------|
| spec.md | Problem (A), Solution (B), Implementation (C), Blockers (D) | Yes |
| tasks.md | Task list with `[ ]`/`[x]` markers + progress | Yes |
| handover.md | Session context + agent working memory | Yes |
| reference/ | Design/Research/Auxiliary documents | No |

**Locate a change**: user offer path | `sspec change find <n>` | `sspec change list` | read .sspec/changes/ or .sspec/changes/archive
**Change Dir Name**: `<time>_<change-name>` (e.g. `.sspec/changes/26-02-11T21-25_command-patch`)

### 2.0 Request → Change Workflow

Assess scale FIRST:

**Micro** (≤3 files, ≤30min, no design decisions):
Track in request file (`## Plan` / `## Done`) or just do it. No change needed.

**Normal+** (anything bigger):

1. **Link**: `sspec change new --from <request>` | create then `sspec request link`
2. **Understand**: First-principles — find the real problem, not the surface ask
3. **Research**: Read project.md + relevant code. If unclear, **use `@ask`** (sspec ask)
4. **Design**:
   - Simple: Draft spec.md mentally
   - Complex (>1 week / >15 files / >20 tasks): **`@ask`** about splitting → `sspec change new <n> --root`
   - Finalize: Distill into spec.md A/B/C (B=Design: interfaces/data/logic; C=Plan: phases/files; avoid duplication)
5. **Confirm**: **`@ask`** to present plan. Wait for approval.
6. **Execute**: Update tasks.md after each task.

**Principle**: Understand before acting. Wrong direction costs more than extra questions.

**Memory**: In long sessions, proactively update handover.md "References & Memory" — context compression is silent and lossy.

📚 Consult `sspec-change` SKILL for scale assessment, document standards, multi-change patterns
📚 Consult `sspec-memory` SKILL for handover quality and memory management

### 2.1 Status Transitions

| From | Trigger | To |
|------|---------|-----|
| PLANNING | user approves | DOING |
| DOING | all tasks `[x]` | REVIEW |
| DOING | missing info | BLOCKED |
| DOING | scope changed | PLANNING |
| BLOCKED | resolved | DOING |
| REVIEW | accepted | DONE |
| REVIEW | needs changes | DOING |

**FORBIDDEN**: PLANNING→DONE, DOING→DONE, BLOCKED→DONE

### 2.2 User Directives

#### `@change <n>`

Existing change: Locate the change -> Read handover.md (especially References & Memory) → tasks.md → spec.md → check reference field → output status + progress + next 3 actions.

New change: `sspec change new <n>` or `--from <request>`. Complex: `--root`. Follow 2.0 workflow. Fill docs per standards in `sspec-change` SKILL. Ask approval.

#### `@resume`

Same as `@change <current_active_change>`.

#### `@handover`

Update handover.md as agent memory. Two modes:

**End-of-session** (mandatory): Update Accomplished, Next Steps, References & Memory; append to project.md Notes; verify tasks.md progress.

**Mid-session** (proactive): Trigger on long session (>50 exchanges), important decisions, key discoveries. Update References & Memory only.

**Principle**: If you'd struggle to reconstruct info after context compression, write it to handover NOW.

📚 Consult `sspec-memory` SKILL for handover quality standards and memory checklists

#### `@sync`

After autonomous coding without tracking: identify changes → update tasks.md → all done? suggest REVIEW.

#### `@argue`

User disagrees. **STOP immediately**. Follow rejection protocol.

📚 Consult `sspec-change` SKILL for rejection scope assessment and edge cases

### 2.3 Template Markers

- **@RULE**: `<!-- @RULE: ... -->` — inline standards reminders. Read and follow. DO NOT delete.
- **@REPLACE**: `<!-- @REPLACE -->` — anchor for first edit.
- **Task markers**: `[ ]` todo, `[x]` done

**Authority**: SKILLs are source of truth. @RULE markers are quick reminders.

---

## 3. SCOPE: Requests

Lightweight proposals created by user. Location: `.sspec/requests/`

Request = "I want X" → Change = "Here's how we do X"

**Micro shortcut**: ≤3 files / ≤30min → track in request file directly. No change needed.

---

## 4. SCOPE: Spec-Docs

Formal specifications (architecture, API contracts, standards). Location: `.sspec/spec-docs/`

For knowledge that is **too complex for project.md** and **surviving beyond any single change**.

New: `sspec doc new "<n>" [--dir]` → follow write-spec-doc SKILL.
Update: Read existing → apply changes → update `updated` field.

📚 Consult `write-spec-doc` SKILL for guidelines

---

## 5. SCOPE: sspec ask

`@ask` indicates:
1. Use Agent Env built in `question` tool (For mini issue)
2. Use SSPEC built in `ask` CLI (For complex issue)
  1. Run `sspec ask create <topic>`
  2. Fill ASK file
  3. Run `sspec ask prompt <file>`

**RULE**:
- If user specified `@sspec-ask` → **MUST ASK** user when: plan end and turns execution, tool call rejected(ask reason), all tasks complete and ready to end.
- Long reusable doc should not go in ASK file → write in `.sspec/tmp` and ref it in QUESTION.

📚 Consult `sspec-ask` SKILL for triggers, workflow, patterns

---

## 6. Behavior Summary

```
ON user_message:
    IF @directive              → Execute directive
    IF micro (≤3 files)        → Do directly
    IF active change DOING     → Continue tasks, update tasks.md
    ELSE                       → Request → Change Workflow (2.0)

ON request_attached:
    DO Request → Change Workflow

ON need_user_input:
    USE @ask                   → Persists record, saves cost

ON important_discovery:
    Route knowledge            → Consult sspec-memory SKILL

ON session_getting_long:
    Proactive memory save      → Update handover.md References & Memory

ON session_end:
    MUST @handover             → No exceptions
    IF project-level learning  → Append to project.md Notes

ON uncertainty:
    Consult SKILL              → sspec-change, sspec-memory, sspec-ask, write-spec-doc
    OR @ask
```

## SKILL of SKILLs

SKILLs use **progressive disclosure**: `SKILL.md` is the entry point, details are dispatched to subfiles to manage context size.

```example
<Root>/<name>/
├── SKILL.md ← Always existed entry
└── references.md ← May exists
```

**Rule**: When `SKILL.md` links to a reference file and instructs to read it (e.g. `IF xxx read [examples](./references.md)` in SKILL.md), **MUST read that file** (`<Root>/<name>/references.md`).
**SKILL**: Use list dir and `sspec-mdtoc` SKILL to analyse SKILL folder.
<!-- SSPEC:END -->