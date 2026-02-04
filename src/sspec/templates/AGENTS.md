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

When entering project or after context reset, execute in order:

```
1. Read .sspec/project.md
2. Run: sspec change list
3. IF active change exists (status != DONE):
     Read: .sspec/changes/<name>/handover.md
     Then: tasks.md → spec.md
     Output: "Resuming <name>: <status>, <progress>, next: <action>"
4. ELSE:
     Output: "No active changes. What would you like to work on?"
```

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

### 2.0 Request Processing Workflow

When user provides vague request (idea, bug, feature), process BEFORE creating change:

```
Step 1: UNDERSTAND
├─ Read user request, identify UNDERLYING NEED (not surface ask)
├─ Apply first-principles thinking
└─ Request may be confused; find the REAL PROBLEM

Step 2: RESEARCH
├─ IF unclear terms or missing info:
│    USE sspec ask → Clarify (saves cost, persists record)
├─ IF existing related change:
│    Consider attaching instead of new change
└─ Gather context from .sspec/project.md and code

Step 3: DESIGN
├─ Simple changes: Draft spec.md mentally
├─ Complex changes: Write exploration to reference/
│    - reference/design-draft.md — Architecture options
│    - reference/api-comparison.md — API alternatives
│    - reference/research-notes.md — External findings
├─ Finalize: Distill into spec.md Section A/B/C
└─ reference/ drafts: Keep for context or discard after finalization

Step 4: CONFIRM
├─ USE sspec ask → Present understanding and plan:
│    "Problem: [quantified problem]
│     Solution: [approach]
│     Files: [list]─ WAIT for explicit confirmation

Step 5: EXECUTE (on confirmation)
├─ Run: sspec change new <name>
├─ Fill spec.md and tasks.md per confirmed plan
└─ Proceed per SSPEC protocol
```

**Key principle**: Understand before acting. Wrong change costs more than extra questions.

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

```
IF .sspec/changes/<name>/ exists:
    Read handover.md → tasks.md → spec.md
    IF reference/ exists: Scan for context
    Output: status, progress percentage, next 3 actions
ELSE:
    Run: sspec change new <name>
    Follow Request Processing Workflow (Section 2.0)
    Fill spec.md Sections A/B/C
    Generate tasks.md from Section C
    Output: "Plan ready. Approve to start? (y/n)"
    WAIT for explicit "y" before status → DOING
```

#### `@resume`

Same as `@change <current_active_change>`.

#### `@handover`

Execute at session end. No exceptions.

```
1. Update handover.md with:
   - Background: 1-sentence change description
   - Accomplished: List of completed tasks this session
   - Status: Current status (PLANNING/DOING/BLOCKED/REVIEW)
   - Next: 1-3 specific file-level actions
   - Conventions: Patterns/naming discovered (if any)

2. Update tasks.md:
   - Mark completed tasks [x]
   - Update progress percentage

3. IF status changed: Update spec.md frontmatter
```

**Quality check**: Would a new Agent know exactly what to do in <30 seconds?

#### `@sync`

After autonomous coding without tracking:

```
1. Identify changes: git diff or ask user
2. Update tasks.md:
   - Mark completed [x]
   - Add tasks for undocumented work done
3. Check: All tasks done? → Suggest REVIEW
```

#### `@argue`

User disagrees mid-implementation. STOP immediately.

```
1. STOP current work
2. Clarify what's wrong:
   - Implementation detail → Revise task in tasks.md
   - Design decision → Revise spec.md Section B
   - Requirement itself → Revise spec.md Section A, add PIVOT marker
3. Output revised plan
4. WAIT for explicit confirmation before continuing
```

### 2.3 Edit Rules

Templates use `@AGENT:` markers:

| Marker | Meaning | Action |
|--------|---------|--------|
| `@AGENT: RULE/<topic>` | Constraint for this section | Follow the rule when filling |
| `@AGENT: REPLACE-FOR-EDIT/<section>` | Replace entirely | Do NOT append; replace whole section |

**Task markers**: `[ ]` todo, `[x]` done, `[-]` blocked, `[~]` needs rework

📚 For quality standards and edge cases → Consult `sspec` SKILL

---

## 3. SCOPE: Requests

Lightweight proposals before becoming changes. Location: `.sspec/requests/`

```
Create:  sspec request new <name>
Link:    sspec request link <request> <change>  # When ready to implement
Archive: sspec request archive <name>
```

Request = "I want X" (idea)
Change = "Here's how we do X" (plan + execution)

---

## 4. SCOPE: Spec-Docs

Project-level specifications (architecture, API contracts, standards). Location: `.sspec/spec-docs/`

#### `@doc <name>`

```
IF creating new:
    Run: sspec doc new "<name>" [--dir]
    Consult: write-spec-doc SKILL
    Write specification following SKILL guidelines
ELSE IF updating:
    Read existing spec-doc
    Apply changes per write-spec-doc SKILL
    Update frontmatter `updated` field
```

📚 For writing guidelines → Consult `write-spec-doc` SKILL

---

## 5. SCOPE: sspec ask

Use when needing user input mid-execution. Saves cost (1 turn instead of 2), reduces hallucination/directional errors, and persists Q&A record.

**When to use**:
1. Information missing → Cannot proceed reliably
2. Directional choice → Multiple valid approaches
3. Completion check → Confirm task is done
4. Repeated failures → Need user insight

**Syntax**:
```bash
sspec ask --name "<topic>" --why "<reason>" --question "<question>"
```

📚 For multi-line syntax and examples → Consult `sspec-ask` SKILL

---

## 6. Behavior Summary

```
ON user_message:
    IF contains @directive     → Execute directive
    IF active change is DOING  → Continue tasks, update tasks.md after each
    ELSE                       → Follow Request Processing Workflow (2.0)

ON need_user_input:
    USE sspec ask              → Persists record, saves cost

ON session_end:
    MUST @handover             → No exceptions

ON uncertainty:
    Consult SKILL              → sspec, sspec-ask, write-spec-doc
    OR use sspec ask for guidance
```

<!-- SSPEC:END -->

