# sspec

[简体中文](README_zh-CN.md)

> **S**spec **S**ynthesizes **P**rograms from **E**xplicit **C**ontext.

## What sspec is

sspec is a document-driven workflow for coding with agents.

It keeps project context, request entrypoints, change specs, execution plans, and scoped memory in the repository instead of leaving them only in chat. Chat moves the work forward; repository files keep the durable state.

## What problems sspec solves

If you rely on chat alone for AI coding, common problems include:

- context and key decisions disappearing across sessions;
- design and implementation checkpoints becoming implicit;
- project conventions needing to be restated repeatedly;
- complex work growing into one opaque, hard-to-review thread.

sspec writes the working state into the repository:

- `AGENTS.md` defines the collaboration protocol;
- `.sspec/project.md` records project identity, stack, key paths, and conventions;
- `.sspec/requests/` stores request entrypoints;
- `.sspec/changes/` stores per-change specs, tasks, memory, and supporting files;
- `.sspec/spec-docs/` stores architecture knowledge that should outlive one change;
- `.sspec/asks/` stores structured questions when important decisions need an explicit record.

When work resumes, the agent reads repository context instead of reconstructing state from prior chat.

## What this requires from the user

sspec assumes a human-led, agent-accelerated workflow.

The developer is expected to:

- define the request clearly enough for the agent to work from it;
- answer design and scope questions at alignment points;
- review implementation results and catch mistakes;
- decide when work should stay in one `change` and when it should be split.

If you do not plan to review the design, review the code, or judge whether the implementation is correct, sspec is usually not a good fit.

## Core concepts

Start with two core concepts: `request` and `change`.

- `request`: the task entrypoint written by the developer. It captures background, constraints, direction, and success criteria.
- `change`: a cohesive, trackable unit of work. A `change` should stay small enough to review and reason about as one unit.

The core files inside a `change` are:

- `spec.md`: the problem and the solution contract;
- `tasks.md`: the execution checklist and progress;
- `memory.md`: the current state, durable knowledge, and milestones for continuity.

Optional files inside a `change`:

- `design.md`: detailed technical design when interfaces, data models, or architecture matter;
- `revisions/`: amendments after the design gate;
- `reference/`: supporting notes, investigation material, and auxiliary files.

For work that is too large for one `change`, use a root change to coordinate multiple sub-changes.

## Folder layout

`sspec project init` creates the project scaffold:

```text
project/
├── AGENTS.md
├── .agents/               # optional synced host location
└── .sspec/
    ├── project.md
    ├── requests/
    ├── changes/
    ├── asks/
    ├── skills/
    ├── spec-docs/
    ├── howto/
    └── tmp/
```

A typical change directory looks like this:

```text
.sspec/changes/<ts>_<name>/
├── spec.md
├── tasks.md
├── memory.md
├── design.md        # optional
├── revisions/       # optional
└── reference/
```

Main directories:

- `project.md`: project identity and conventions;
- `requests/`: request files written by the developer;
- `changes/`: per-change working documents;
- `asks/`: structured questions and answers when needed;
- `skills/`: agent-facing skills synced into host-specific locations;
- `spec-docs/`: long-lived architecture and project knowledge;
- `howto/`: focused operational guides for specific jobs;
- `tmp/`: scratch space for temporary notes and drafts.

## Workflow

sspec’s default lifecycle is:

```text
Clarify → Design → Plan → Implement → Review
```

What each stage does:

- **Clarify**: build shared understanding from user intent and codebase reality;
- **Design**: create the change, write `spec.md`, add `design.md` when needed, then align with the user;
- **Plan**: turn the design into file-level tasks in `tasks.md`;
- **Implement**: execute tasks, update progress, and keep `memory.md` current;
- **Review**: collect feedback, iterate, and close the loop.

Two practical rules:

- `memory.md` is the continuity file agents resume from;
- if approved scope or design needs to change later, record it in `revisions/NNN-*.md` and update `tasks.md`.

## Quick Start

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

Then fill `.sspec/project.md` with:

- your stack;
- key paths;
- coding conventions;
- project-level notes.

### 3) Create a request

```bash
sspec request new add-password-reset
```

Write background, problem, direction, and success criteria in the generated request file. A minimal example:

```markdown
# Request: add-password-reset

## Background
We currently support email and password login only.

## Problem
Users cannot reset a forgotten password on their own.

## Initial Direction
- Use email reset tokens
- Tokens must be time-limited and single-use
- Do not add new external services

## Success Criteria
- Users can request a reset email
- Tokens expire and cannot be reused
- The core flow is covered by tests

## Relational Context
- Related code: `src/auth/*`
- Existing emails: `src/notifications/email/*`
```

### 4) Hand the request to the agent

You can paste the request file path into chat and tell the agent to follow `AGENTS.md`:

```text
Please work from this request:
.sspec/requests/<your-request-file>.md

Follow `AGENTS.md` and `.sspec/skills/`.
Start with `sspec-clarify`, then create and maintain the change docs.
Stop at design and implementation gates for review.
```

The agent will typically create the working change with:

```bash
sspec change new --from <request>
```

### 5) Track the change

Use the CLI to inspect progress and current state:

```bash
sspec change list
sspec change status <name>
```

When the design needs a dedicated technical document:

```bash
sspec change scaffold design <change>
```

### 6) Archive when done

When the work is complete, archive the change and its linked request:

```bash
sspec change archive --with-request [name]
```

## Key rules and responsibilities

**Developer responsibilities**

- write the `request`, including background, constraints, and success criteria;
- answer key design and scope questions;
- approve the design direction and implementation result;
- decide when a `change` should be split.

**Agent responsibilities**

- clarify the problem before designing;
- create and maintain the `change` docs for the work;
- propose a solution, align with the user, then implement;
- keep `tasks.md` and `memory.md` current while the change is active.

**Workflow rules**

- start from a `request`, not from chat history alone;
- design and implementation both stop at explicit review points;
- long-lived state belongs in repository files, not only in chat;
- complex work should be split into trackable changes instead of accumulating in one thread.

## Common commands

These are the commands most users need. For the full list, run `sspec --help`.

### Project

```bash
sspec project init
sspec project status
sspec project update --dry-run
```

### Request

```bash
sspec request new <name>
sspec request list
sspec request show <name>
sspec request find <query>
sspec request archive [name] --with-change
```

### Change

```bash
sspec change new <name>
sspec change new --from <request>
sspec change new <name> --root
sspec change new <name> --scaffold design
sspec change scaffold design <change>
sspec change scaffold revision <change> --title "scope-update"
sspec change status <name>
sspec change list --all
sspec change validate <name>
sspec change archive [name] --with-request
```

### Ask

```bash
sspec ask create <name>
sspec ask prompt <ask-file>
sspec ask list --all
sspec ask archive [name]
```

### Docs, HOWTOs, skills, and tools

```bash
sspec doc list
sspec doc new "<name>"
sspec howto list
sspec howto resume-change
sspec skill list
sspec tool now
sspec tool mdtoc README.md
sspec tool view-tree .
```

## Advanced

### Root changes

Use a root change when the work is too large for one trackable unit:

```bash
sspec change new <name> --root
```

A root change defines the overall problem and phase breakdown. File-level design and execution stay in the sub-changes.

### `design.md` and `revisions/`

Create `design.md` when the change introduces new interfaces, data models, or architectural behavior.

When approved design or scope changes later, create a revision file and update the plan:

```bash
sspec change scaffold revision <change> --title "<reason>"
```

### `memory.md`

`memory.md` is the continuity surface for a change. It typically carries:

- `State`: where the work is now and what happens next;
- `Key Files`: non-obvious files that matter to continuation;
- `Knowledge`: durable decisions, constraints, and gotchas;
- `Milestones`: one-line factual session records.

Root changes also use `Coordination` to summarize sub-change status.

### Skills and sync layout

`.sspec/skills/` is the source directory for skills. Host-specific locations such as `.agents/skills/` are synced from it by `sspec project init` and `sspec project update`.

### Builtin tools

`sspec tool` provides CLI complements for agent workflows, including:

- `now`
- `ask`
- `mdtoc`
- `view-tree`
- `fileinfo`
- `patch`
- `write`
- `treesitter`
- `pack-zip`

Run `sspec tool --help` for the full list.

## Compatibility

sspec assumes an agent environment that can:

- read and write local repository files;
- follow instructions from `AGENTS.md`;
- execute local CLI commands;
- load and follow skills under `.sspec/skills/`.

## License

AGPL-V3.0
