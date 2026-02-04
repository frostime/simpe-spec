# sspec

**S**spec **S**ynthesizes **P**rograms from **E**xplicit **C**ontext

A simple spec-driven Vibe Coding framework, designed for solo developers.

---

## Why sspec?

You're coding with AI. It starts great—AI understands your intent, code quality is solid.

Then the project grows. AI starts to:
- Forget design decisions you made last week
- Lose track of what's done and what's in progress
- Need the same project context explained every new session
- Get lost on complex tasks, making inconsistent changes

**The root problem**: AI has no cross-session memory. Every conversation starts from zero.

**sspec's solution**: Write project state to files. AI reads these files on startup and "remembers" everything.

---

## What does sspec do?

After running `sspec project init`, your project gets:

```
your-project/
├── AGENTS.md                    # AI protocol: tells AI how to use sspec
├── .sspec/
│   ├── project.md               # Project background, tech stack, conventions
│   ├── spec-docs/               # Project-level design docs
│   ├── changes/                 # Active changes
│   ├── requests/                # Idea drafts
│   └── asks/                    # Human-AI Q&A records
└── .claude/skills/              # AI skill references (or .github/skills/)
    ├── sspec/SKILL.md
    ├── sspec-ask/SKILL.md
    └── write-spec-doc/SKILL.md
```

**AGENTS.md** is the key—it defines how AI should interact with the `.sspec/` directory. Place it at the project root, and AI tools (Claude Code, Cursor, Copilot) will read it automatically.

---

## Core Concepts

### Change

Change is sspec's core unit of work. A feature, a bug fix, a refactor—each is a change.

Every change has three files:

```
.sspec/changes/add-auth/
├── spec.md      # What's the problem? What's the solution?
├── tasks.md     # What exactly needs to be done? Each task <2 hours
└── handover.md  # Session handover: what's done, what's next
```

**spec.md** answers WHY and WHAT:
- Section A: Problem statement (quantified pain point)
- Section B: Solution (why this approach)
- Section C: Implementation plan (which files to modify)
- Section D: Blockers and feedback

**tasks.md** answers HOW:
- Executable task checklist
- Mark `[x]` as each completes
- AI always sees current progress

**handover.md** bridges sessions:
- Background: What this change is about
- Accomplished: What got done this session
- Next Steps: What to do next time

AI reads handover.md and gets back to work in 30 seconds.

### Request

Request is an idea draft before it becomes a change.

When you have a vague idea ("auth seems slow") but haven't figured out the solution, write it as a request first:

```bash
sspec request new slow-auth
```

Requests only need the problem and initial thoughts. When ready, convert to a change:

```bash
sspec request link slow-auth auth-optimization
```

### Spec-doc

Spec-docs are project-level design documents, not tied to specific changes.

API design standards, database schemas, architecture decisions—these should persist long-term for all changes to reference:

```bash
sspec doc new "API Design Standards"
sspec doc new "Payment System" --dir  # Use directory for complex topics
```

Stored in `.sspec/spec-docs/`, AI references them when working on related changes.

### sspec ask (Human-in-the-loop)

When AI needs your input mid-execution, it uses a two-step workflow:

```bash
# Step 1: AI creates ask template
sspec ask create --name api_style

# Step 2: AI edits the .py file with REASON + QUESTION
# (OR you can pre-fill USER_ANSWER in the file)

# Step 3: Execute and collect answer
sspec ask prompt .sspec/asks/<timestamp>_api_style.py
```

AI pauses for your answer. Q&A records saved in `.sspec/asks/` for future reference.

**Benefits**:
- No shell escaping/encoding issues (edit Python file directly)
- You can pre-fill answers in the file (skip terminal prompt)
- Reduces AI guessing when uncertain
- Q&A records are traceable
- Reduces billing consumption in AI coding environments billed by credits (e.g., Copilot)
  - Traditional: Turn 1 (5 tool calls) → Stop → 1 Credit + Turn 2 (5 tool calls) → 1 Credit = **2 Credits**
  - Sspec ask: Turn 1 (5 tool calls → ask user → 5 tool calls) = **1 Credit**

---

## Workflow

### Starting a new task

```bash
# 1. Create a change
sspec change new add-user-auth

# 2. AI helps fill spec.md and tasks.md
#    Uses sspec ask to clarify uncertainties

# 3. After confirming the plan, AI starts executing tasks
```

### Ending a session

Tell AI: `@handover`

AI updates handover.md with current progress and next steps.

### Resuming work

Next time: `@resume`

AI reads handover.md and continues where you left off.

### Completing a task

When all tasks are done, change enters REVIEW status. After you confirm:

```bash
sspec change archive add-user-auth
```

Change is archived to `.sspec/changes/.archive/`.

---

## Status Flow

Each change has a status:

```
PLANNING ──→ DOING ──→ REVIEW ──→ DONE
    ↑          │
    │          ↓
    └─────── BLOCKED
```

- **PLANNING**: Still designing, spec.md not finalized
- **DOING**: Implementing, tasks.md being updated
- **BLOCKED**: Stuck, waiting on external dependency
- **REVIEW**: Done, awaiting your verification
- **DONE**: Archived

AI decides what to do based on status.

---

## Installation

```bash
pip install sspec
```

## Initialize a project

```bash
cd your-project
sspec project init
```

Interactively choose skill installation locations (.claude, .github, .agent).

## CLI Quick Reference

```bash
# Project
sspec project init          # Initialize
sspec project status        # View status
sspec project update        # Update templates

# Changes
sspec change new <n>     # Create
sspec change list           # List
sspec change archive <n> # Archive

# Requests
sspec request new <n>    # Create idea draft
sspec request link <req> <change>  # Link to change

# Spec-docs
sspec doc new <n>        # Create
sspec doc list              # List

# Human-in-the-loop
sspec ask create [--name <n>]  # Create ask template
sspec ask prompt <path>        # Execute ask prompt
```

---

## AI Directives

Use these directives in conversation to control AI:

| Directive | Action |
|-----------|--------|
| `@change <n>` | Switch to a change (or create new) |
| `@resume` | Resume previous work |
| `@handover` | End session, write handover |
| `@sync` | Sync code changes to tasks.md |
| `@argue` | Stop, I disagree |

---

## Compatibility

sspec generates Markdown files. Any AI tool that reads project files works:

- Claude Code
- Cursor
- Windsurf
- GitHub Copilot
- VS Code Copilot

Just tell AI: "Read AGENTS.md first".

---

## When you don't need sspec

- Fixing a typo
- Quick bug fix
- Config tweaks

Simple stuff, just do it. No ceremony needed. sspec is for tasks that span multiple sessions and need context preserved.

---

## License

AGPL-V3.0

