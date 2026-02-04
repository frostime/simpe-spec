<!-- SSPEC:START -->
# .sspec Agent Protocol

SSPEC_SCHEMA::{{SCHEMA_VERSION}}

## What is SSPEC?

SSPEC is a document-driven AI collaboration framework. All planning, tracking, and handover lives in `.sspec/`.

**Core Design**:
- **spec.md** = WHY/WHAT (problem, solution, decisions)
- **tasks.md** = HOW (executable tasks <2h each)
- **handover.md** = CONTINUITY (session bridge—update EVERY session end)

**Goal**: Any Agent resumes work within 30 seconds by reading `.sspec/` files.

---

## Glossary

| Term | Definition |
|------|------------|
| **Change** | Unit of work (feature/bugfix/refactor) with its own spec/tasks/handover |
| **Spec-doc** | Project-level specification document (persistent design docs, not tied to changes) |
| **Directive** | User command via `@xxx` syntax—Agent MUST NOT auto-trigger |
| **Status** | Lifecycle: PLANNING → DOING → REVIEW → DONE (or BLOCKED) |
| **SKILL** | Deep reference for status rules, quality standards, edge cases |
| **Request** | User write the reqeust of proposal draft, can be the origin of a new change |
| **Ask** | Agent use "SSPEC Ask" to inquire user, very important, see sspec-ask skill |

---

## Hard Rules

1. **`.sspec/` is authoritative**: Read from and update `.sspec/` files, not external notes
2. **Directives require user input**: Never auto-execute `@xxx` commands
3. **Handover every session**: Update `handover.md` before ending work—no exceptions
4. **Respect status transitions**: See Quick Reference; consult SKILL for edge cases

## Workflow Decision Tree

```
WHEN Agent::receive_user_message:
    IF message CONTAINS "@directive":
        EXECUTE directive
    ELSE:
        IF active_change.status == "DOING":
            CONTINUE tasks
            UPDATE tasks.md
        ELSE:
            PROMPT "What to work on?" (suggest @resume or @change)

WHEN Agent::need-to-launch-new-change:
    User 'sspec' skill, read and learn
    Deep think and research to learn the context
    Fill the spec.md and tasks.md
    Ask user if ok
    IF User say ok
        Turn into execution

WHEN Agent::is_executing_tool_call:
    IF lack information, needs clarification:
        USE "sspec-ask" skill
        Execute `sspec ask` command
        Get information from user

IF session_ending:
    REMIND "Run @handover to save progress"
```

---

## RULE | User Directives

### `@change <name>`

Switch to existing change or create new one.
```
IF .sspec/changes/<name>/ exists:
    Read: handover.md → tasks.md → spec.md
    Output: context summary (status, progress, next actions)
ELSE:
    Run: sspec change new <name>
    Help user fill spec.md (problem + solution)
    Generate tasks.md
    Wait for user approval
```

---

### `@doc <name>`

Create or edit project specification documents (architecture, API contracts, standards)
```
IF user wants to create new spec-doc:
    User request the concet needs
    Run if need: sspec doc new "<name>" [--dir]
    Consult: SKILL "write-spec-doc"
    Write spec document
ELSE IF updating existing spec-doc:
    Find spec-doc, by "sspec doc list" or user specified.
    Apply write-spec-doc SKILL guidelines -> Update.
```

---

### `@resume`

Resume work after session break.
```
Read: handover.md → tasks.md → spec.md
Research the code and think, learn the context
Recorver the working status
```

---

### `@handover`

End session and write handover for next Agent.
```
1. Update handover.md with:
   - Background: What is this change about?
   - Accomplished: What got done this session?
   - Current Status: PLANNING/DOING/BLOCKED/REVIEW
   - Next Steps: Immediately actionable items
   - Conventions: Project-specific patterns to follow
2. Update tasks.md: Mark completed [x], update progress
3. Update spec.md status if transitioning

Quality bar: Next session starts coding in <30 seconds, not 30 minutes.
```

---

### `@sync`

Reconcile `.sspec/` with code changes after autonomous coding.
```
1. Identify changes (ask user, git diff, or file timestamps)
2. Update tasks.md:
   - Mark completed tasks [x]
   - Add new tasks for undocumented work
3. Check status:
   - All tasks done? → Suggest REVIEW
   - Hit blocker? → Suggest BLOCKED
```

---

### `@argue`

User disagrees with approach during implementation.

```
1. STOP implementation immediately
2. Clarify scope:
   - Detail (how to code) → Revise task in tasks.md
   - Design (architecture) → Revise spec.md section B
   - Requirement (what to build) → Revise spec.md section A + PIVOT marker
3. Seek user confirmation before continuing
```

---

## RULE | Files Under .sspec/changes

### Use: Template Markers

Change documents (spec.md, tasks.md, handover.md) use `@AGENT:` markers to guide editing:

#### `@AGENT: RULE/<topic>`

Constraints for filling in sections. Example:
```markdown
<!-- @AGENT: RULE/quantify-pain
Describe current pain points with metrics.
-->
```

#### `@AGENT: REPLACE-FOR-EDIT/<section>`

Indicates section should be **replaced**, not appended to:
```markdown
<!-- @AGENT: REPLACE-FOR-EDIT/problem-statement -->
```

📚 **For detailed editing patterns**: Consult sspec SKILL section "Core Editing Patterns"

### Edit Files Rule

| File | Update When | Edit Pattern |
|------|-------------|-------------|
| **spec.md** | Status change, strategy pivot, design decision, blocker | Use REPLACE-FOR-EDIT markers; append to Section D for blockers |
| **tasks.md** | Task completion (immediately!), task discovery, replanning | Replace task checkboxes, replace Progress Tracking section |
| **handover.md** | **Every session end**—this is the **memory** between sessions | Replace entire content after markers |

### Edit spec.md: Status

- **PLANNING** (scope/tasks) → DOING (user approves)
- **DOING** (implementing) → BLOCKED (dependency) | REVIEW (done) | PLANNING (pivot)
- **BLOCKED** (waiting) → DOING (resolved) | PLANNING (pivot)
- **REVIEW** (verify) → DONE (accepted) | DOING (changes)
- **DONE** (complete) → archive via `sspec change archive <name>`

**Forbidden:** PLANNING→DONE | DOING→DONE | BLOCKED→DONE

📚 **For detailed definitions, edge cases, quality standards**: Consult the **sspec SKILL**.

### Edit tasks.md: Task Markers

| Marker | Meaning |
|--------|---------|
| `[ ]` | Todo |
| `[x]` | Done (complete AND tested) |
| `[-]` | Blocked |
| `[~]` | Needs rework |

---

## SSPEC Quick Reference

### Folder Structure

```
.sspec/
├── project.md              # Project overview, tech stack, conventions
├── spec-docs/              # Project-level specification documents (persistent)
│   ├── README.md           # Spec usage guide
│   └── <name>.md           # Individual specs (or <name>/index.md for multi-file)
├── skills/sspec/SKILL.md   # Status rules, quality standards, edge cases
├── changes/<name>/
│   ├── spec.md             # Problem, solution, decisions
│   ├── tasks.md            # Tasks (<2h each) + progress
│   ├── handover.md         # Session continuity
│   ├── reference/          # Optional: detailed design, research notes
│   └── scripts/            # Optional: migration scripts, test data
└── requests/               # Ad-hoc requests (optional)
```

---

### CLI Commands

```shell
# Project
sspec project init           # Initialize .sspec/
sspec project status         # Show overview

# Changes
sspec change new <name>      # Create change
sspec change list            # List all changes
sspec change archive <name>  # Archive completed change

# Specification Documents
sspec doc list               # List project specification documents
sspec doc new <name>         # Create single-file spec-doc
sspec doc new <name> --dir   # Create directory-based spec-doc (complex subsystems)

# See SSPEC ASK SKILL
sspec ask --name <name> --why <reason>  --question <question>
```


## SKILL | Prefer using `sspec ask` (alias "ask prompt")

When you need user input mid-execution and want it persisted, run `sspec ask`.

- PowerShell (multi-line): `sspec ask --name "<topic>" --why "<reason>" --question @'...multi-line...'@`
- Bash/Zsh (stdin): `sspec ask --name "<topic>" --why "<reason>" --question -` (then provide question via stdin)

The exchange is recorded under `.sspec/asks/` and the command prints the record path.

> [!IMPORTANT] If the user explicitly specifies or when specific conditions are met, the "sspec ask" (or "Ask Prompt" as an alias) must be used to consult the user.
> Refer to the "sspec-ask" skill for details.
>
> MUST use under the following conditions:
> - Information is missing and requires user input
> - A decision is needed for the next step
> - To confirm understanding or intent with the user
> - Encountering errors that are difficult to interpret

---

## Best Practices

1. **Read before acting**: Load `.sspec/` context first
2. **Update as you go**: Mark tasks `[x]` immediately, don't batch
3. **Handover is sacred**: Never skip; it's the only cross-session memory
4. **Consult SKILL when uncertain**: Status edge cases, quality standards
5. **Preserve history**: Append to handover.md, don't overwrite
6. **Actively Use SSPEC ASK**

**Your goal**: Make the next Agent's life easy. Write handovers for your future self.

<!-- SSPEC:END -->
