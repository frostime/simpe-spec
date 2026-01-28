# sspec

[中文](./README_zh-CN.md)

Document-driven AI collaboration framework. Persistent memory across sessions via structured files.

## Problem

AI assistants forget context when conversations end. You waste time re-explaining the project, decisions, and progress.

## Solution

sspec provides structured files (`.sspec/`) that persist across sessions:
- **spec.md**: Problem, solution, design decisions
- **tasks.md**: Executable tasks with progress tracking
- **handover.md**: Session bridge—what was done, what's next
- **spec-docs/**: Project-level specifications (architecture, APIs, standards)

## Install

```bash
pip install sspec
```

## Quick Start

```bash
cd your-project
sspec project init
```

Creates `.sspec/` with:
- `project.md` - Project context (tech stack, constraints)
- `spec-docs/` - Specifications directory
- `changes/` - Active changes (features, bugs, refactors)
- `skills/` - Custom AI skills and guidance

## Workflow

### 1. Create Change

```bash
sspec change new add-auth
```

AI creates:
```
.sspec/changes/add-auth/
├── spec.md      # WHY and WHAT
├── tasks.md     # HOW (tasks <2h each)
└── handover.md  # Session continuity
```

### 2. Implement

AI reads spec.md, executes tasks, updates progress in tasks.md.

Optional auxiliary files:
```
.sspec/changes/add-auth/
├── reference/   # Design docs, research notes
└── scripts/     # Migration scripts, test data
```

### 3. End Session

Tell AI: `@handover`

AI updates handover.md with:
- Background (what this change is about)
- Accomplished (what was done this session)
- Status (PLANNING/DOING/BLOCKED/REVIEW)
- Next Steps (immediately actionable)

### 4. Resume

Next session: `@resume`

AI reads handover.md and continues from exactly where you left off.

## Specifications

Create project-level specs (persistent, not tied to changes):

```bash
sspec spec new "API Design"           # Single file
sspec spec new "Payment System" --dir # Directory
sspec spec list                       # List all
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `sspec project init` | Initialize .sspec/ |
| `sspec project status` | Show overview |
| `sspec project update` | Update templates |
| `sspec change new <name>` | Create change |
| `sspec change list` | List changes |
| `sspec change archive <name>` | Archive completed |
| `sspec doc new <name>` | Create spec doc |
| `sspec doc list` | List specs doc |
| `sspec skill new <name>` | Create skill |
| `sspec skill list` | List skills |

## File Structure

```
.sspec/
├── project.md              # Project context
├── spec-docs/                   # Project specifications document
├── changes/<name>/
│   ├── spec.md             # Change specification
│   ├── tasks.md            # Tasks and progress
│   ├── handover.md         # Session bridge
│   ├── reference/          # Optional: design docs
│   └── scripts/            # Optional: utilities
└── skills/                 # AI guidance
```

## Status Lifecycle

```
PLANNING → DOING → REVIEW → DONE
     ↓        ↓
  BLOCKED  BLOCKED
```

## Agent Directives

| Directive | Action |
|-----------|--------|
| `@change <name>` | Switch to change |
| `@resume` | Resume active work |
| `@handover` | Write session handover |
| `@sync` | Reconcile .sspec/ with code |

See `AGENTS.md` template for full protocol.

## Compatibility

Works with any AI tool that reads Markdown context files:
- Claude Code, Cursor, Windsurf, GitHub Copilot, VS Code Copilot

Tell your AI: "Read `.sspec/AGENTS.md` first"

## When NOT to Use

- Quick bug fixes
- Typos and formatting
- Simple config changes

For trivial work, just do it. No ceremony needed.

## License

MIT
