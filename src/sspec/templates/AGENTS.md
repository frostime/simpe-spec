<!-- SSPEC:START -->
# .sspec Agent Protocol

SSPEC_SCHEMA::{{SCHEMA_VERSION}}

## What is SSPEC?

SSPEC is a document-driven AI collaboration framework that manages the complete lifecycle of project changes through the `.sspec/` directory.

**Core Philosophy**:
- **Single Source of Truth**: All planning, tracking, and handover information lives in `.sspec/`
- **Cross-Session Continuity**: `handover.md` enables context transfer between sessions
- **Structured Collaboration**: spec.md (WHY/WHAT) + tasks.md (HOW) + handover.md (CONTINUITY)

**Goal**: Enable any Agent to resume work within 30 seconds by reading `.sspec/` files.

------

## Glossary

| Term | Definition |
|------|------------|
| **Change** | An independent unit of work (feature/bugfix/refactor) with spec/tasks/handover files |
| **Directive** | User-triggered command via `@xxx` syntax (NOT auto-executable) |
| **Status** | Lifecycle state: PLANNING → DOING → REVIEW → DONE (or BLOCKED) |
| **Handover** | Session-end context document enabling next session to start immediately |
| **SKILL** | Extended reference material for status definitions, rules, quality standards |

------

## Hard Rules

1. **`.sspec/` is authoritative**: Always read from and update `.sspec/` files, not external notes
2. **Directives are explicit**: All `@xxx` commands require user input; never auto-trigger
3. **Handover every session**: Update `handover.md` before ending any work session
4. **Status drives workflow**: Respect status transitions (see Quick Reference)

------

## User Directives

### `@change <name>`

**Purpose**: Switch to existing change or create new one.

**Execution Logic**:
```
Step 1: Check existence
  IF `.sspec/changes/<name>/` exists:
    → GO TO Step 3 (Load)
  ELSE:
    → GO TO Step 2 (Create)

Step 2: Create new change
  a. Run shell command: sspec change new <name>
  b. Help user fill spec.md:
     - Ask: "What problem are you solving?"
     - Ask: "What's your proposed solution?"
  c. Generate initial tasks in tasks.md based on spec
  d. Wait for user approval of plan

Step 3: Load existing change
  Read files in order (newer to older context):
    1. handover.md  → Latest session state
    2. tasks.md     → Current progress
    3. spec.md      → Overall context

Step 4: Output context summary (use this format)
  ═══════════════════════════════════════
  Change: <name>
  Status: <status> | Type: <type>
  ───────────────────────────────────────
  Context:
  <1-2 sentences from spec.md problem statement>

  Current Progress: <X/Y tasks completed>
  In Progress:
  <List tasks marked [~] or recently worked on>

  Next Actions:
  <From handover.md "Next Steps" or first pending task>
  ═══════════════════════════════════════
```

**Common Cases**:
- First time working on change → Expect to fill spec.md and approve tasks
- Resuming after break → Context summary shows where to continue

---

### `@resume`

**Purpose**: Resume work after session break (new chat, new terminal, etc.).

**Execution Logic**:
```
Step 1: Find candidate changes
  candidates = [c for c in changes if c.status in {DOING, BLOCKED, REVIEW}]

Step 2: Select change
  IF len(candidates) == 1:
    selected = candidates[0]
    → GO TO Step 3

  IF len(candidates) > 1:
    Output: "Multiple active changes found. Use @change <name> to specify:"
    <List candidates with status and last updated time>
    → STOP (wait for user)

  IF len(candidates) == 0:
    Output: "No active changes. Run 'sspec change list' to see all changes."
    → STOP

Step 3: Load selected change
  Same as @change Step 3-4 (read files → output context)
```

**Priority Order** when multiple candidates:
1. Status = DOING (should only be 1)
2. Status = BLOCKED, most recently updated
3. Status = REVIEW, oldest (awaiting user feedback longest)

---

### `@handover`

**Purpose**: End session and write handover document for next Agent.

**Execution Logic**:
```
Step 1: Update handover.md
  Required sections (use template structure):

  ## Session <N> - <YYYY-MM-DD HH:MM>

  ### Background
  <What is this change about? Why does it exist?>

  ### What Was Accomplished
  <Concrete achievements this session:>
  - Completed: <list finished tasks>
  - Modified files: <key files changed>
  - Decisions made: <any design choices>

  ### Current Status
  Status: <PLANNING|DOING|BLOCKED|REVIEW>
  <If BLOCKED: what's blocking and what's needed>

  ### Next Steps
  <Immediately actionable items for next session>
  1. <First thing to do>
  2. <Second thing to do>

  ### Conventions to Follow
  <Any project-specific patterns, naming, or constraints>

Step 2: Update tasks.md progress
  - Mark completed tasks [x]
  - Update progress percentage
  - Add "Recent Updates" entry with timestamp

Step 3: Update spec.md status (if changed)
  Update YAML front matter if transitioning status

Step 4: Remind user
  Output: "Handover saved. Session context preserved for next Agent."
```

**Quality Standard**: Good handover = next session starts coding in <30 seconds, not 30 minutes.

---

### `@sync`

**Purpose**: Reconcile `.sspec/` with actual code changes after autonomous coding sessions.

**Execution Logic**:
```
Step 1: Identify what changed (use first available method)
  Priority order:
  1. Ask user: "Which files/features did you work on?"
  2. If git repo: git diff --name-only HEAD
  3. Check file timestamps (last 2 hours)

Step 2: Update tasks.md
  FOR each modified file/feature:
    IF related task exists in tasks.md AND work is complete:
      → Mark task [x]
    IF new work not in tasks.md:
      → Add new task entry + mark [x] (document what was done)

Step 3: Update handover.md "Recent Updates"
  Add entry: "- <timestamp>: <brief change description>"

Step 4: Check status transition
  IF all tasks done:
    → Suggest: "All tasks complete. Ready to change status to REVIEW?"
  IF encountered blocker:
    → Suggest: "Blocker detected. Change status to BLOCKED?"
```

**Use Case**: After working in Claude Code, Copilot Edits, or other autonomous sessions where `.sspec/` wasn't actively updated.

---

### `@argue`

**Purpose**: Handle user disagreement during implementation (approach, design, requirements).

**Execution Logic**:
```
Step 1: STOP current implementation immediately

Step 2: Analyze disagreement scope
  Ask: "Is this about:
    a) Implementation detail (how to code something)
    b) Design approach (architecture, pattern)
    c) Requirement (what we're building)"

Step 3: Update relevant files
  IF scope = (a) detail:
    → Update tasks.md (revise task description)

  IF scope = (b) design:
    → Update spec.md section B (Proposed Solution)
    → Regenerate tasks.md if needed

  IF scope = (c) requirement:
    → Update spec.md section A (Problem Statement)
    → Add PIVOT marker: <!-- PIVOT: YYYY-MM-DD - <reason> -->
    → Regenerate tasks.md completely

Step 4: Seek user confirmation
  Output revised plan and ask: "Does this address your concern?"
  → Wait for approval before continuing
```

------

## Quick Reference

### Status System

| Status | Meaning | Can Transition To | Trigger |
|--------|---------|-------------------|---------|
| **PLANNING** | Defining scope, creating task plan | DOING | User approves plan |
| **DOING** | Implementation in progress | BLOCKED, REVIEW, PLANNING | Hit blocker / All tasks done / Major pivot |
| **BLOCKED** | Waiting on external dependency | DOING, PLANNING | Blocker resolved / Pivot needed |
| **REVIEW** | Implementation done, awaiting verification | DONE, DOING | User accepts / Changes requested |
| **DONE** | Completed and archived | - | User runs `sspec change archive <name>` |

**Forbidden Transitions**:
- PLANNING → REVIEW/DONE (can't skip implementation)
- DOING → DONE (must go through REVIEW)
- BLOCKED → DONE (can't finish with unresolved blocker)

💡 **For full definitions, transition rules, and edge cases**: Consult the **sspec** skill (Agent systems with SKILL support will auto-load from `.claude/skills/sspec/` or `.github/skills/sspec/`)

---

### File Formats Cheatsheet

#### spec.md Front Matter (Required)
```yaml
---
status: PLANNING        # See status table above
type: feature          # feature | bugfix | refactor | docs
created: 2026-01-27
---
```

#### tasks.md Task Markers
- `[ ]` Todo
- `[x]` Done (fully complete AND tested)
- `[-]` Blocked
- `[~]` Rework needed

#### handover.md Session Structure
See templates generated in `.sspec/changes/<name>/handover.md` for detailed format with inline comments.

**Key Principle**: Each session appends a new section; don't overwrite history.

---

### Folder Structure

```text
.sspec/
├── project.md              # Project overview, conventions, tech stack
├── skills/sspec/SKILL.md   # Extended reference (status rules, quality standards)
├── changes/<name>/
│   ├── spec.md             # WHY/WHAT: problem, decisions, solution
│   ├── tasks.md            # HOW: executable tasks (<2h each) + progress
│   └── handover.md         # CONTINUITY: session-to-session context bridge
└── requests/*.md           # Incoming ad-hoc requests (optional)
```

---

### CLI Commands

```shell
# Change management
sspec change new <name>         # Create new change
sspec change list               # List all changes with status
sspec change archive <name>     # Archive completed change

# Project operations
sspec project init              # Initialize .sspec in current directory
sspec project status            # Show project overview

# Requests (optional workflow)
sspec request new <name>        # Create ad-hoc request
```

------

## Workflow Decision Tree

```
User sends message
    │
    ├─ Contains @directive? ──YES──> Execute that directive (see above)
    │
    └─ NO ──> Check active change context
              │
              ├─ Has active change (status=DOING)?
              │   └─ YES ──> Continue working on current tasks
              │              Update tasks.md as you complete items
              │
              └─ NO ──> Ask: "What would you like to work on?"
                        Suggest: Use @resume or @change <name>

Mid-session reminders:
  - Task completed ──> Update tasks.md immediately, mark [x]
  - Hit blocker ──> Update spec.md section D + consider status → BLOCKED
  - Session >20 min ──> Remind user about @sync if working autonomously

Before ending conversation:
  - IF made progress ──> Remind: "Run @handover to save session progress"
```

------

## File Update Responsibilities

| File | Content | When to Update |
|------|---------|----------------|
| **spec.md** | Problem statement, solution design, decisions, blockers | Strategy change, status transition, major pivot |
| **tasks.md** | Executable tasks (<2h each), progress tracking | Task planning, task completion, task discovery |
| **handover.md** | Session summaries (Done/Now/Next) | **Every session end** (critical!) |
| **project.md** | Project-wide conventions, tech stack, constraints | Project setup, global rule changes |

------

## Best Practices

1. **Read before acting**: Always load context from `.sspec/` before starting work
2. **Update as you go**: Mark tasks `[x]` immediately when done, don't batch
3. **Handover is sacred**: Never skip handover; it's the only memory between sessions
4. **Ask when uncertain**: If status rules or edge cases are unclear, refer to the sspec SKILL
5. **Preserve history**: In handover.md, append sessions; don't overwrite

**Remember**: Your goal is to make the next Agent's life easy. Write handovers for your future self.

<!-- SSPEC:END -->