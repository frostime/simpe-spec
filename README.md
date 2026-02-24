# sspec

[简体中文](README_zh-CN.md)

**S**spec **S**ynthesizes **P**rograms from **E**xplicit **C**ontext.

sspec is a file-based workflow for AI-assisted development. It keeps planning, decisions, and handover in your repository, so an agent can resume work across sessions instead of restarting from zero.

## Why sspec

AI coding sessions usually fail at continuity:

- decisions get lost after context compression,
- implementation intent drifts between sessions,
- humans repeat the same project background.

sspec solves this by storing working state in `.sspec/` and defining agent behavior in `AGENTS.md`.

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

Then fill `.sspec/project.md` with your stack, conventions, and key paths.

### 3) Create a request

```bash
sspec request new add-password-reset
```

Write the request in `.sspec/requests/...` (problem, initial direction, success criteria).

### 4) Hand it to your agent

In chat with your coding agent:

```text
@change add-password-reset
```

The agent should run the SSPEC lifecycle, update change files, and ask for human decisions at `@ask` gates.

### 5) Resume later

```text
@resume
```

The agent reloads `handover.md`, `tasks.md`, and `spec.md` to continue from the previous stopping point.

## Lifecycle

Each phase has a dedicated SKILL in `.sspec/skills/`.

```text
[Request] -> [Research] -> [Design] -> [Plan] -> [Implement] -> [Review] -> [Handover]
                     (ask)      (ask)         (ask)        (feedback loop)
```

Core rules:

- `Research` focuses on understanding problem space and code context.
- `Design` and `Implement` are mandatory `@ask` checkpoints.
- `Plan` uses a lightweight `@ask` confirmation.
- `Implement` and `Review` form a feedback loop until user acceptance.
- `Handover` is not optional cleanup; it is a lifecycle phase.

## What sspec creates

```text
project/
├── AGENTS.md
└── .sspec/
    ├── project.md
    ├── changes/
    ├── requests/
    ├── asks/
    ├── spec-docs/
    ├── skills/
    └── tmp/
```

- `project.md`: project identity, conventions, long-term notes.
- `changes/<id>/spec.md`: problem and proposed solution.
- `changes/<id>/tasks.md`: executable checklist and progress.
- `changes/<id>/handover.md`: session memory and next steps.
- `requests/`: user intents before formal change creation.
- `asks/`: agent-to-user Q&A records.

## Human vs Agent

**Human responsibilities**

- create requests,
- answer `@ask` questions,
- approve design and review outcomes.

**Agent responsibilities**

- assess scope (micro/single/multi-change),
- create and maintain change files,
- keep tasks and handover current,
- drive the ask-feedback loop until accepted.

## Chat Directives

These directives are interpreted by agents that load your `AGENTS.md`.

| Directive | Typical use |
|-----------|-------------|
| `@change <name>` | Start/resume work on a change |
| `@resume` | Continue the active change |
| `@handover` | Persist state for next session |
| `@sync` | Reconcile docs (`tasks.md`, `handover.md`) with code reality |
| `@argue` | Stop current approach and reassess scope |

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

### Asks

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
- use claude skills.

## License

AGPL-V3.0
