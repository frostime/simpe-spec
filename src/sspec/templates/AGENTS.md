<!-- SSPEC:START -->
# .sspec Agent Protocol

SSPEC_SCHEMA::{{SCHEMA_VERSION}}

## 0. Protocol Overview

SSPEC is a document-driven AI collaboration framework. All planning, tracking, and handover lives in `.sspec/`.

**Goal**: Any Agent resumes work within 30 seconds by reading `.sspec/` files.

**Folder Structure**:
```
.sspec/
├── project.md              # Project overview, tech stack, conventions
├── spec-docs/              # Project-level specifications (persistent)
├── changes/<name>/         # Active change proposals
│   ├── spec.md | tasks.md | handover.md  # Required
│   └── reference/ | script/             # Optional
├── requests/               # Lightweight proposals
└── asks/                   # Human-in-the-loop Q&A records
```

---

## 1. Cold Start

When entering project in new session:

1. Read `.sspec/project.md`
2. Determine action based on user message:

| User Message | Action |
|--------------|--------|
| Contains `@resume` or `@change` | Load that change's context |
| Vague request (idea/bug/feature) | Follow Request → Change Workflow (Section 2.0) |
| Simple task, no directive | Do directly, skip sspec ceremony |
| Micro change (≤3 files, ≤30 min) | Plan inline in request file, skip change ceremony |

---

## 2. SCOPE: Changes

Changes live in `.sspec/changes/<name>/`.

| File/Dir | Contains | Required |
|----------|----------|----------|
| spec.md | Problem (A), Solution (B), Implementation (C), Blockers (D) | Yes |
| tasks.md | Task list with `[ ]`/`[x]` markers + progress | Yes |
| handover.md | Session context for next Agent | Yes |
| reference/ | Design drafts, research, diagrams (pre-finalization workspace) | No |
| script/ | Migration scripts, test data, one-off tools | No |

### 2.0 Request → Change Workflow

<!-- Request → Change Pre-check -->
**First**: Assess if a change is needed at all.
- **Micro change** (≤3 files, ≤30 min, user says OK): Track in request file directly. Add a `## Plan` and `## Done` section to the request. No change ceremony needed.
- **Normal change**: Proceed with workflow below.

<!-- Request → Change Main Workflow -->
User provides a vague request (idea, bug, feature), process following BEFORE creating change:

1. **Change**: Invoke `sspec change new` with `--from` or invoke `link` after new, make request-change pair.
2. **Understand**: Read the request carefully. Identify the underlying need, not the surface ask. Requests are often confused—apply first-principles thinking to find the real problem.
3. **Research**: Gather context from `.sspec/project.md` and relevant code. If unclear terms or missing info, **use `sspec ask` actively**—it saves cost and reduces guessing.
4. **Design**: Once requirements are clear:
   - Simple changes: Draft spec.md mentally
   - Complex changes (>1 week / >15 files / >20 tasks): **Use `sspec ask`** to consult user on splitting into multi-change approach. If confirmed, use `sspec change new <n> --root` to create a root change.
     - For design exploration: Use `reference/` for drafts
     - For one-off scripts: Use `script/`
   - Finalize: Distill into spec.md Sections A/B/C
5. **Confirm**: Before implementation, **use `sspec ask`** to present your understanding and plan. Wait for explicit approval.
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

#### `@change <name>`

If `.sspec/changes/<name>/` exists:
- Read handover.md → tasks.md → spec.md
- Check spec.md `reference` frontmatter field for linked requests/changes
- If reference/ exists: Scan for context
- Output: status, progress percentage, next 3 actions

If new:
- Run `sspec change new <name>` or `sspec change new --from <request>`
- For complex scope: `sspec change new <name> --root` (creates phase-level coordinator)
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
Create:  sspec request new <name>
Link:    sspec request link <request> <change>
Archive: sspec request archive <name>
```

Request = "I want X" (idea)
Change = "Here's how we do X" (plan + execution)

---

## 4. SCOPE: Spec-Docs

Project-level specifications (architecture, API contracts, standards). Location: `.sspec/spec-docs/`

#### `@doc <name>`

If creating new:
- Run `sspec doc new "<name>" [--dir]`
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
🤖 User input directive `/sspec-ask` → Consult `sspec-ask` SKILL, and apply ask when {Confuse, Before End, Tool call rejected}.

---

## 6. Behavior Summary

```
ON user_message:
    IF contains @directive     → Execute directive
    IF active change is DOING  → Continue tasks, update tasks.md after each
    ELSE                       → Follow Request → Change Workflow (2.0)

ON need_user_input:
    USE sspec ask              → Persists record, saves cost

ON session_end:
    MUST @handover             → No exceptions

ON uncertainty:
    Consult SKILL              → sspec, sspec-ask, write-spec-doc
    OR use sspec ask for guidance
```

<!-- SSPEC:END -->
