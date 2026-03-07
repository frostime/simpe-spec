# sspec

[简体中文](README_zh-CN.md)

> **S**spec **S**ynthesizes **P**rograms from **E**xplicit **C**ontext.

## What sspec is

sspec is a doc-driven collaboration workflow for coding agents.

It keeps the request entrypoint, design, task list, and handover records in the repository instead of leaving them only in chat history. Chat moves the work forward; repository files hold long-lived state. You define goals, constraints, and key decisions; the agent researches, implements, and updates the docs so work can continue across sessions.

## What problems sspec solves

If you rely on chat alone for AI coding, common problems include:

- context and key decisions getting lost in long or cross-session work;
- the agent continuing to modify code while the developer loses visibility into what changed and why;
- repeating the same project background, conventions, and constraints;
- complex work growing inside chat until it becomes one large, hard-to-track change.

sspec writes long-lived working state into the repository:

- `AGENTS.md` defines the collaboration protocol;
- `.sspec/project.md` records project identity, stack, key paths, and conventions;
- `.sspec/requests/` stores request entrypoints;
- `.sspec/changes/` stores the spec, tasks, and handover for each change;
- `.sspec/asks/` stores important questions and answers.

When work resumes, the agent reads explicit repository context instead of reconstructing state from the previous chat.

## What this requires from the user

sspec assumes that the developer defines requirements and reviews results, while the agent handles research, design, implementation, and documentation updates.

Using it usually requires:

- the ability to write a clear `request`;
- the ability to give direct feedback during design alignment and implementation review;
- enough development skill to judge whether the implementation is correct and spot agent mistakes.

If you do not plan to write `request` files, review results, or judge whether the implementation is correct, this workflow is usually not a good fit.

## Core concepts and folder layout

Start with two core concepts: `request` and `change`.

- `request`: the task entrypoint written by the developer. It describes background, constraints, direction, and success criteria.
- `change`: a cohesive, atomic, trackable change proposal. A `change` should stay small enough to review and track as one unit.

The three most important files inside a `change` are:

- `spec.md`: how the change should work, and why;
- `tasks.md`: execution steps and current progress;
- `handover.md`: current session state, key findings, and what the next session needs.

If work grows beyond the trackable scope of a single `change`, split it by:

- using `root-change` to coordinate multiple `sub-change` items;
- or creating a follow-up `change` that references `prev-change`, instead of expanding one old change into a large, untrackable container.

For more concepts and advanced usage, see `Advanced` later in this README.

`sspec project init` creates the minimal structure:

```text
project/
├── AGENTS.md
└── .sspec/
    ├── project.md
    ├── requests/
    ├── changes/
    │   └── <ts>_<name>/
    │       ├── spec.md
    │       ├── tasks.md
    │       ├── handover.md
    │       └── reference/
    ├── asks/
    ├── skills/
    ├── spec-docs/
    └── tmp/
```

Main directories:

- `project.md`: project identity. Record the stack, key paths, conventions, and project-level notes.
- `requests/`: request entry files written by the developer.
- `changes/`: per-change document directories; each change contains `spec.md`, `tasks.md`, and `handover.md`.
- `asks/`: recorded questions and answers, so decisions do not live only in chat.
- `spec-docs/`: long-lived architectural knowledge that goes beyond a single change.
- `skills/`: phase-specific skills that can be synced into different agent hosts.

## Minimal workflow

A typical flow looks like this:

1. Run `sspec project init`, then fill in `.sspec/project.md`.
2. Run `sspec request new <name>` and write the `request`.
3. Send the request file path to the agent and tell it to follow `AGENTS.md`.
4. The agent researches the background and codebase, then proposes the design and plan, and stops at key checkpoints for alignment.
5. After alignment, the agent implements the change; you review the result and provide feedback.
6. The agent iterates on that feedback until you are satisfied.
7. At session end, the agent updates `handover.md`; when the work is complete, archive the `change`.

This workflow includes document updates and user confirmation points. It does not depend on a single chat session.

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
Create and maintain the corresponding change docs for this work.
Stop and ask me before making key decisions.
```

### 5) Archive when done

When the work is complete, archive the change and its linked request:

```bash
sspec change archive --with-request [name]
```

## Key rules and responsibilities

**Developer responsibilities**

- write the `request`, including background, constraints, and success criteria;
- answer key decision questions;
- approve the design direction and implementation result;
- decide when a `change` should be split to keep scope trackable.

**Agent responsibilities**

- research the code, background, and constraints before designing;
- create and maintain the `change` docs for the work;
- propose a solution, align with the user, then implement;
- keep `tasks.md` and `handover.md` current, and keep iterating after review feedback.

**Workflow rules**

- start from a `request`, not from chat history alone;
- `Design` and `Implement` both include mandatory confirmation points;
- `Handover` is a formal lifecycle phase, not optional cleanup;
- long-lived state lives in `change` docs, not only in chat history.

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
sspec request archive [name] --with-change
```

### Change

```bash
sspec change new <name>
sspec change new --from <request>
sspec change new <name> --root
sspec change list --all
sspec change archive [name] --with-request
```

## Advanced

### `ask`: persist important Q&A

Use `ask` when the agent needs a key decision, finds ambiguity in the requirement, or needs to record an important question formally.

Common commands:

```bash
sspec ask create <topic>
sspec ask prompt <ask-file>
sspec ask list --all
sspec ask archive [name]
```

### `spec-docs/`: store long-lived knowledge across changes

`spec-docs/` stores knowledge that should outlive a single change, such as architecture interfaces, data models, design patterns, or conventions.

Common commands:

```bash
sspec doc list
sspec doc new "<name>"
```

### `skills/`: `.sspec/skills/` is the source directory

sspec installs skills with a hub-spoke layout:

- `.sspec/skills/` is the hub and the source directory for skills
- `.agents/skills/`, `.claude/skills/`, `.github/skills/`, and similar external locations are spokes
- spokes usually reference `.sspec/skills/` via symlink or junction
- `sspec project init` and `sspec project update` manage this hub-spoke sync; users do not need to update it manually

## Other

### Compatibility

sspec depends on an agent environment that can:

- read and write local repository files;
- follow instructions from `AGENTS.md`;
- execute local CLI commands;
- load and follow skills under `.sspec/skills/`.

## License

AGPL-V3.0
