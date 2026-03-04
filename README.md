# sspec

[简体中文](README_zh-CN.md)

**S**spec **S**ynthesizes **P**rograms from **E**xplicit **C**ontext.

sspec is a file-based workflow for AI-assisted development. It keeps planning, decisions, and handover in your repository, so an agent can resume work across sessions instead of restarting from zero.

## Why sspec

AI coding sessions usually fail at continuity:

- in long sessions (and especially across sessions), context and decisions get lost,
- agents can drift and keep changing things while the developer loses visibility,
- humans repeat the same project background and constraints.

sspec solves this by storing working state in `.sspec/` and defining the workflow in
`AGENTS.md` plus step-specific instructions (skills) under `.sspec/skills/`.

## What sspec is (and isn't)

sspec is a lightweight, file-based workflow for controlling coding agents.

It is for independent developers (or small teams) who:

- want the agent to assist, not take over,
- care about resumability and "what changed / why" across long sessions,
- can write a decent request (context, constraints, success criteria).

It is not for:

- one-line "build me an app" style prompting,
- people who don't want to write/maintain requests, tasks, or handovers.

sspec is designed to be added to existing projects (from 1-N). You can introduce it
incrementally and use it only where it helps.

sspec does not depend on platform-specific "slash commands". The core contract is
file-based: `AGENTS.md` + `.sspec/` files that an agent can read and update.

## Core concepts and folder layout

Minimal structure (created by `sspec project init`):

```text
project/
├── AGENTS.md
└── .sspec/
    ├── project.md
    ├── requests/
    ├── changes/
    ├── asks/
    ├── skills/
    ├── spec-docs/
    └── tmp/
```

Core concepts:

- `request`: the entry point you write (context, constraints, success criteria).
  Stored under `.sspec/requests/`.
- `change`: a tracked unit of work under `.sspec/changes/<id>/`.
- `spec.md`: problem statement + proposed solution for a change.
- `tasks.md`: executable checklist + progress (updated as work completes).
- `handover.md`: session memory and next steps, so work can resume later.
- Q&A record (`ask`): used when the agent needs a decision or missing information.
  Stored under `.sspec/asks/` (created via `sspec ask`).

Note: `sspec ask` is for persisting important questions/answers instead of leaving
them only in chat history.

Skills:

- `.sspec/skills/` is the canonical (hub) copy of skills.
- sspec can sync/link skills into tool-specific locations (spokes) like `.claude/`,
  `.github/`, or `.agents/` so the same skill set works across different agent
  hosts.

## Design principles

- **Request-first**: start from a written request, not a chat log.
- **Explicit context**: link relevant files and constraints early.
- **Tracked execution**: tasks are updated as work completes.
- **Human checkpoints**: the agent must stop and confirm important decisions.
- **Resumability**: `handover.md` is required, not optional.
- **Developer-led**: the developer stays in control of direction and scope.

## Minimal example

1) Create a request:

```bash
sspec request new add-password-reset
```

2) Fill the request with context and constraints (example structure):

```markdown
# Request: add-password-reset

## Background
We currently support email+password login.

## Problem
Users cannot reset a forgotten password.

## Initial Direction
- Use email-based reset tokens (time-limited)
- Do not add new external services

## Success Criteria
- User can request a reset email
- Token expires and is single-use
- Flow is covered by tests

## Relational Context
- Related code: `src/auth/*`
- Existing emails: `src/notifications/email/*`
```

3) Hand it to your agent:

```text
Please implement this request:
.sspec/requests/<your-request-file>.md

Follow the sspec workflow described in `AGENTS.md` and the installed skills.
Keep the change docs (`spec.md`, `tasks.md`, `handover.md`) up to date.
Stop and ask me to confirm key decisions before proceeding.
```

The agent reads the request, produces `spec.md` + `tasks.md`, and keeps `handover.md` current so you can resume later.

## Quick Start

If you are working with a coding agent, the commands you typically run yourself are:

```bash
sspec project init
sspec request new <name>
sspec change archive --with-request [name]
```

### 1) Install

```bash
pip install sspec
# or
uv tool install sspec
```

### 2) Initialize in your project

```bash
cd your-project
sspec project init
```

Then fill `.sspec/project.md` with your stack, conventions, and key paths.

### 3) Create a request

```bash
sspec request new add-password-reset
```

Write the request in `.sspec/requests/...` (context, constraints, success criteria).

Then, in chat, paste the request file path (printed by `sspec request new`) and tell
your agent to follow `AGENTS.md`.

When you're done, archive the change (and its linked request) with:

```bash
sspec change archive --with-request
```

Tip: `sspec request new` can auto-open the file in your editor (see below).

## Editor integration

When creating a request, sspec will try to open the file in your editor.

Resolution order:

1) `.env` in your project working directory: `SSPEC_EDITOR`
2) environment variable: `SSPEC_EDITOR`
3) environment variable: `EDITOR`

The editor command can include `{file}` (it will be replaced with the new file path).

Example for VS Code:

```bash
SSPEC_EDITOR='code {file}'
```

## Lifecycle

Each phase has a dedicated SKILL in `.sspec/skills/`.

```text
[Request] -> [Research] -> [Design] -> [Plan] -> [Implement] -> [Review] -> [Handover]
                (decision checkpoints)   (feedback loop)
```

Core rules:

- `Research` focuses on understanding problem space and code context.
- `Design` and `Implement` include mandatory decision checkpoints.
- `Plan` uses a lightweight confirmation.
- `Implement` and `Review` form a feedback loop until user acceptance.
- `Handover` is not optional cleanup; it is a lifecycle phase.

## Human vs Agent

**Human responsibilities**

- create requests,
- answer decision questions (and record Q&A when needed),
- approve design and review outcomes.

**Agent responsibilities**

- assess scope (micro/single/multi-change),
- create and maintain change files,
- keep tasks and handover current,
- drive a feedback loop until accepted, recording questions/decisions when needed.

## CLI Reference

### Project

```bash
sspec project init
sspec project status
sspec project update --dry-run
```

### Requests

```bash
sspec request new <name>
sspec request list
sspec request show <name>
sspec request find <query>
sspec request link <request> <change>
sspec request archive [name] --with-change
```

### Changes

```bash
sspec change new <name>
sspec change new --from <request>
sspec change new <name> --root
sspec change list --all
sspec change find <query>
sspec change validate <name>
sspec change archive [name] --with-request
```

### Q&A records (`ask`)

```bash
sspec ask create <topic>
sspec ask prompt <ask-file>
sspec ask list --all
sspec ask archive [name]
```

### Spec docs

```bash
sspec doc list
sspec doc new "<name>"
sspec doc new "<name>" --dir
```

### Optional utilities

```bash
sspec skill list
sspec skill new <name>
sspec cmd add
sspec cmd list
sspec cmd run <name>
sspec tmp new <name>
sspec tool mdtoc <file>
sspec tool view-tree
sspec tool pack-zip --dry-run
sspec tool patch --prompt
```

## Compatibility

sspec works best with coding agents that can:

- read and write repository files,
- follow instructions from `AGENTS.md`,
- execute local CLI commands.
- load and follow skill instructions.

## License

AGPL-V3.0
