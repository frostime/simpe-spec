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
| **Directive** | User command via `@xxx` syntax—Agent MUST NOT auto-trigger |
| **Status** | Lifecycle: PLANNING → DOING → REVIEW → DONE (or BLOCKED) |
| **SKILL** | Deep reference for status rules, quality standards, edge cases |

---

## Hard Rules

1. **`.sspec/` is authoritative**: Read from and update `.sspec/` files, not external notes
2. **Directives require user input**: Never auto-execute `@xxx` commands
3. **Handover every session**: Update `handover.md` before ending work—no exceptions
4. **Respect status transitions**: See Quick Reference; consult SKILL for edge cases

---

## User Directives

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

### `@resume`

Resume work after session break.

```
candidates = changes WHERE status IN {DOING, BLOCKED, REVIEW}

IF len(candidates) == 0:
    Output: "No active changes. Use @change <name> or see 'sspec change list'"
    STOP

IF len(candidates) == 1:
    Load that change (same as @change)
ELSE:
    Output: "Multiple active changes. Specify with @change <name>:"
    List candidates with status
    STOP
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

## Quick Reference

### Status Transitions

| Status | Meaning | Next States | Trigger |
|--------|---------|-------------|---------|
| **PLANNING** | Defining scope, planning tasks | DOING | User approves plan |
| **DOING** | Implementation in progress | BLOCKED, REVIEW, PLANNING | Blocker / Done / Pivot |
| **BLOCKED** | Waiting on external dependency | DOING, PLANNING | Resolved / Pivot |
| **REVIEW** | Done, awaiting verification | DONE, DOING | Accepted / Changes needed |
| **DONE** | Completed | - | `sspec change archive <name>` |

**Forbidden**: PLANNING→DONE (skip work), DOING→DONE (skip review), BLOCKED→DONE (unresolved)

📚 **For detailed definitions, edge cases, quality standards**: Consult the **sspec SKILL** at `.claude/skills/sspec/SKILL.md` or `.sspec/skills/sspec/SKILL.md`

---

### Task Markers

| Marker | Meaning |
|--------|---------|
| `[ ]` | Todo |
| `[x]` | Done (complete AND tested) |
| `[-]` | Blocked |
| `[~]` | Needs rework |

---

### Folder Structure

```
.sspec/
├── project.md              # Project overview, tech stack, conventions
├── spec/                   # Project-level specifications (persistent)
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

# Specifications
sspec spec list              # List project specifications
sspec spec new <name>        # Create single-file spec
sspec spec new <name> --dir  # Create directory-based spec
```

---

## Workflow Decision Tree

```
User message received
    │
    ├─ Contains @directive? → Execute that directive
    │
    └─ No directive
        │
        ├─ Active change (status=DOING)?
        │   └─ Continue tasks, update tasks.md as you go
        │
        └─ No active change
            └─ Ask: "What to work on?" Suggest @resume or @change

Session ending?
    └─ Remind: "Run @handover to save progress"
```

---

## File Update Rules

| File | Update When |
|------|-------------|
| **spec.md** | Status change, strategy pivot, design decision |
| **tasks.md** | Task completion (immediately!), task discovery, replanning |
| **handover.md** | **Every session end**—this is the memory between sessions |

---

## Best Practices

1. **Read before acting**: Load `.sspec/` context first
2. **Update as you go**: Mark tasks `[x]` immediately, don't batch
3. **Handover is sacred**: Never skip; it's the only cross-session memory
4. **Consult SKILL when uncertain**: Status edge cases, quality standards
5. **Preserve history**: Append to handover.md, don't overwrite

**Your goal**: Make the next Agent's life easy. Write handovers for your future self.

<!-- SSPEC:END -->
