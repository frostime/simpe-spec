# sspec

[简体中文](README_zh-CN.md)

> Spec-driven development for AI coding. Developer controls the agent. State lives in files, not chat.

---

## The Idea

AI coding agents are powerful but unpredictable. They forget decisions across sessions, they run ahead without alignment, and the thread becomes the only record of what was decided and why.

sspec inverts this: **the repository is the source of truth, not the chat**. The agent reads files to understand context. The agent writes files to commit to decisions. At key points, the agent stops and waits for the developer to review — before code is written, not after.

Three principles:

- **Predictability**: You must be able to predict the outcome before implementation begins. No unclarified assumptions survive.
- **Durable state**: Project context, specs, tasks, and session memory live in repository files. Agents resume from files, not from reconstructing chat history.
- **Hard gates**: Design and implementation each end with a mandatory review point. The agent stops. You decide.

## Is sspec for you?

**Yes** if you:
- review design before code is written
- want specs and tasks tracked in files, not buried in chat
- work on projects where continuity across sessions matters

**Probably not** if you:
- prefer free-form conversation with the agent, no structure
- do not plan to review the agent's design or code
- work on one-shot scripts where a single chat session suffices

## How it works

### Request — intent record

A request captures what you want, something you observed, or an idea to keep. Three kinds:

| kind | when to use | agent behavior |
|------|-------------|----------------|
| `directive` | You have a clear task for the agent | Agent assesses scale, creates a change, starts working |
| `observe` | You noticed something off — a UX glitch, weird code, a smell | Agent reads and notes it. Does **not** create a change. For later human triage. |
| `idea` | A thought worth keeping, maybe for later | Agent may refer to it as context. Does **not** act unless asked. |

```bash
sspec request new add-password-reset                # directive (default)
sspec request new strange-logout-bug --kind observe
sspec request new async-refactor --kind idea
```

### Change — atomic unit of work

A change is a cohesive, reviewable piece of work. It lives in `.sspec/changes/<name>/` and contains:

| File | Purpose |
|------|---------|
| `spec.md` | Problem, approach, scope, and success criteria — **the contract** |
| `tasks.md` | File-level execution checklist with progress |
| `memory.md` | Current state, key decisions, milestones — **continuity across sessions** |
| `design.md` | (optional) Technical design for interfaces, data models, architecture |
| `revisions/` | (optional) Amendments after the design gate |

### Lifecycle with gates

```
Clarify  →  Design  →  Plan  →  Implement  →  Review
              ■                   ■
```

`■` = hard stop. The agent **must** wait for your review before proceeding.

- **Design gate**: Review `spec.md` (+ `design.md`). The solution contract is now fixed. Changes after this go into `revisions/`.
- **Implementation gate**: Review the code. Fix issues, amend scope, or approve as done.

### Memory — continuity file

`memory.md` is how the agent resumes. Next session, the agent reads `memory.md` first — it knows exactly where the work stands, what files matter, and why past decisions were made. No reconstructing from chat history.

### Spec-docs — long-lived knowledge

Architecture decisions, design patterns, platform constraints — things that outlive any single change. Live in `.sspec/spec-docs/`, referenced by the agent across all changes.

## Folder layout

```
project/
├── AGENTS.md              ← the protocol (agent reads this first)
├── .agents/skills/        ← synced from .sspec/skills/
└── .sspec/
    ├── project.md         ← your stack, conventions, key paths
    ├── requests/          ← intent records (directive / observe / idea)
    ├── changes/           ← active and archived changes
    │   └── <name>/
    │       ├── spec.md
    │       ├── tasks.md
    │       └── memory.md
    ├── spec-docs/         ← architecture and design knowledge
    ├── skills/            ← agent-facing skill definitions
    ├── asks/              ← structured Q&A records
    ├── howto/             ← operational guides
    └── tmp/               ← scratch space
```

## Quick Start

### 1. Install and initialize

```bash
pip install sspec
cd your-project
sspec project init
```

Then fill `.sspec/project.md` with your stack, key paths, and conventions.

### 2. Start work — two paths

**Path A: Describe your need to the agent.** Tell the agent what you want. A capable agent reads `AGENTS.md` and follows the sspec protocol — it clarifies, creates a change, writes the spec, and stops at the design gate for your review.

**Path B: Write a request file.** If you have clear ideas, create a request:

```bash
sspec request new add-dark-mode --kind directive
```

Fill in background, problem, direction, and success criteria. The agent picks it up from there.

### 3. Review at gates

The agent stops at two points:
- **Design gate**: read `spec.md`, confirm the approach, then tell the agent to proceed.
- **Implementation gate**: review the code, request fixes, or approve.

### 4. Archive when done

```bash
sspec change archive --with-request <name>
```

## Common commands

```bash
# Requests
sspec request new <name> [--kind directive|observe|idea]
sspec request list

# Changes
sspec change new <name> [--from <request>] [--root]
sspec change status <name>
sspec change list
sspec change archive <name> --with-request

# Project
sspec project status
sspec project update --dry-run

# Docs
sspec doc new "Architecture Overview"

# Tools
sspec tool now
sspec tool mdtoc README.md
```

Run `sspec --help` for the full command list.

## License

AGPL-3.0
