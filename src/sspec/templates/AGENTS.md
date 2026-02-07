<!-- SSPEC:START -->
# .sspec Agent Protocol

SSPEC_SCHEMA::{{SCHEMA_VERSION}}

## 0. Protocol Overview

SSPEC is a document-driven AI collaboration framework. All planning, tracking, and handover lives in `.sspec/`.

**Goal**: Any Agent resumes work within 30 seconds by reading `.sspec/` files.

**Folder Structure**:
```
.sspec/
├── project.md              # Identity, conventions, accumulated notes (memory)
├── spec-docs/              # Formal specifications (architecture, APIs, standards)
├── changes/<n>/            # Active change proposals
│   ├── spec.md | tasks.md | handover.md  # Required
│   └── reference/ | script/              # Optional
├── requests/               # Lightweight proposals
└── asks/                   # Human-in-the-loop Q&A records
```

---

## 1. Cold Start

When entering project in new session:

1. Read `.sspec/project.md` — identity, conventions, and accumulated notes
2. Determine action based on user message:

| User Message | Action |
|--------------|--------|
| Contains `@resume` or `@change` | Load that change's context |
| Contains `@status` | Show project overview (see below) |
| Micro task (≤3 files, ≤30min, obvious) | Do directly, no change ceremony |
| Vague request (idea/bug/feature) | Follow Request → Change Workflow (Section 2.0) |
| Simple task, no directive | Do directly, skip sspec ceremony |

3. If touching unfamiliar subsystem → check `spec-docs/` for relevant specs

#### `@status`

Project-wide overview. Output:

1. Active changes: name, status, progress% for each
2. Pending requests (OPEN/DOING)
3. Blockers across all changes
4. Recent entries from `project.md` Notes (if any)

---

## 2. SCOPE: Changes

Changes live in `.sspec/changes/<n>/`.

| File/Dir | Contains | Required |
|----------|----------|----------|
| spec.md | Problem (A), Solution (B), Implementation (C), Blockers (D) | Yes |
| tasks.md | Task list with `[ ]`/`[x]` markers + progress | Yes |
| handover.md | Session context for next Agent | Yes |
| reference/ | Design drafts, research, diagrams (pre-finalization workspace) | No |
| script/ | Migration scripts, test data, one-off tools | No |

### 2.0 Request → Change Workflow

When user provides a request (idea, bug, feature), assess scale FIRST:

**Micro** (≤3 files, ≤30min, no design decisions):
- Track inline in request file — add `## Plan` and `## Done` sections
- Or just do it directly if user approves
- No change ceremony needed

**Normal+** (anything bigger):

1. **Link**: Invoke `sspec change new` with `--from` or invoke `link` after new, make request-change pair.
2. **Understand**: Read the request carefully. Identify the underlying need, not the surface ask. Requests are often confused—apply first-principles thinking to find the real problem.
3. **Research**: Gather context from `.sspec/project.md` and relevant code. If unclear terms or missing info, **use `@ask` actively**—it saves cost and reduces guessing.
4. **Design**: Once requirements are clear:
   - Simple changes: Draft spec.md mentally
   - Complex changes (>1 week / >15 files / >20 tasks): **Use `@ask`** to consult user on splitting into multi-change approach. If confirmed, use `sspec change new <n> --root` to create a root change.
     - For design exploration: Use `reference/` for drafts
     - For one-off scripts: Use `script/`
   - Finalize: Distill into spec.md Sections A/B/C
5. **Confirm**: Before implementation, **use `@ask`** to present your understanding and plan. Wait for explicit approval.
6. **Execute**: Proceed per SSPEC protocol. Update tasks.md after each task.

**Key principle**: Understand before acting. Wrong direction costs more than extra questions.

📚 For quality standards, complexity assessment, multi-change patterns → Consult `sspec` SKILL

### 2.1 Status Transitions

| From | Trigger | To |
|------|---------|-----|
| PLANNING | user approves plan | DOING |
| DOING | all tasks `[x]` | REVIEW |
| DOING | missing info/resource | BLOCKED |
| DOING | scope changed | PLANNING |
| BLOCKED | blocker resolved | DOING |
| REVIEW | user accepts | DONE |
| REVIEW | user requests changes | DOING |

**FORBIDDEN**: PLANNING→DONE, DOING→DONE, BLOCKED→DONE

### 2.2 Directives

#### `@change <n>`

If `.sspec/changes/<n>/` exists:
- Read handover.md → tasks.md → spec.md
- Check spec.md `reference` frontmatter field for linked requests/changes
- If reference/ exists: Scan for context
- Output: status, progress percentage, next 3 actions

If new:
- Run `sspec change new <n>` or `sspec change new --from <request>`
- For complex scope: `sspec change new <n> --root` (creates phase-level coordinator)
- Follow Request → Change Workflow (Section 2.0)
- Fill spec.md Sections A/B/C, (follow `@RULE` inside template)
- Generate tasks.md from Section C, (follow `@RULE` inside template)
- Ask for approval to execute

#### `@resume`

Same as `@change <current_active_change>`.

#### `@handover`

Execute at session end. No exceptions.

1. Update handover.md with:
   - Background: 1-sentence change description
   - Accomplished: List of completed tasks this session
   - Status: Current status (PLANNING/DOING/BLOCKED/REVIEW)
   - Next: 1-3 specific file-level actions
   - Conventions: Patterns/naming discovered (if any)

2. Update tasks.md:
   - Mark completed tasks `[x]`
   - Update progress percentage

3. If status changed: Update spec.md frontmatter

4. If project-level learnings discovered (not change-specific):
   Append to `.sspec/project.md` Notes section

**Quality check**: Would a new Agent know exactly what to do in <30 seconds?

#### `@sync`

After autonomous coding without tracking:

1. Identify changes: git diff or ask user
2. Update tasks.md:
   - Mark completed `[x]`
   - Add tasks for undocumented work done
3. Check: All tasks done? → Suggest REVIEW

#### `@argue`

User disagrees mid-implementation. **STOP immediately**, then follow the rejection protocol.

📚 For detailed rejection protocol and scope assessment → Consult `sspec` SKILL

### 2.3 Edit Rules

Templates use markers to guide editing:

| Marker | Meaning | Action |
|--------|---------|--------|
| `<!-- @RULE: ... -->` | Constraint for this section | Follow the rule when filling |
| `<!-- @REPLACE -->` | Replace entirely | Do NOT append; replace whole section |

**Task markers**: `[ ]` todo, `[x]` done

📚 For quality standards and edge cases → Consult `sspec` SKILL

---

## 3. SCOPE: Requests

Lightweight proposals before becoming changes. Location: `.sspec/requests/`

```
Create:  sspec request new <n>
Link:    sspec request link <request> <change>
Archive: sspec request archive <n>
```

Request = "I want X" (idea)
Change = "Here's how we do X" (plan + execution)

**Micro-change shortcut**: For ≤3 files / ≤30min work, track plan and result directly in the request file. No change needed.

---

## 4. SCOPE: Spec-Docs

Formal project-level specifications (architecture, API contracts, standards). Location: `.sspec/spec-docs/`

Use spec-docs for knowledge **too complex for project.md Conventions** and **needs to survive beyond any single change**.

#### `@doc <n>`

If creating new:
- Run `sspec doc new "<n>" [--dir]`
- Consult write-spec-doc SKILL
- Write specification following SKILL guidelines

If updating:
- Read existing spec-doc
- Apply changes per write-spec-doc SKILL
- Update frontmatter `updated` field

📚 For writing guidelines → Consult `write-spec-doc` SKILL

---

## 5. SCOPE: sspec ask

**USE ACTIVELY** — Don't hesitate to ask. Better to confirm than guess wrong.

```
sspec ask create <topic>     # Create ask template
sspec ask prompt <file>      # Execute and collect answer
sspec ask list               # View pending/completed asks
```

📚 For triggers, workflow, syntax and examples → Consult `sspec-ask` SKILL

User directive `@ask` → Consult `sspec-ask` SKILL, and trigger ask when {confused, before session end, tool call rejected}.

---

## 6. Behavior Summary

```
ON user_message:
    IF contains @directive     → Execute directive
    IF micro task (≤3 files)   → Do directly, skip ceremony
    IF active change is DOING  → Continue tasks, update tasks.md after each
    ELSE                       → Follow Request → Change Workflow (2.0)

ON need_user_input:
    USE @ask                   → Persists record, saves cost

ON session_end:
    MUST @handover             → No exceptions
    IF project-level learning  → Append to project.md Notes

ON uncertainty:
    Consult SKILL              → sspec, sspec-ask, write-spec-doc
    OR use @ask for guidance
```

### Directive Quick Reference

| Directive | Scope | What it does |
|-----------|-------|--------------|
| `@change <n>` | Changes | Load or create change context |
| `@resume` | Changes | Continue active change |
| `@handover` | Changes | Save context + notes for next session |
| `@sync` | Changes | Reconcile tasks with actual work |
| `@argue` | Changes | Stop, clarify, re-plan |
| `@status` | Project | Active changes, requests, blockers overview |
| `@doc <n>` | Spec-Docs | Create or update specification |
| `@ask` | Ask | Consult user, by using `sspec ask` |

<!-- SSPEC:END -->
