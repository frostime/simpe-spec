# sspec

Lightweight AI collaboration spec for solo/small projects.

## Philosophy

**sspec** is a simplified alternative to [OpenSpec](https://openspec.dev/) designed for:

- Solo developers or small teams
- Projects that don't need formal spec validation
- Quick iteration with AI assistants

### Compared to OpenSpec

| Aspect | OpenSpec | sspec |
|--------|----------|-------|
| Change structure | `changes/<id>/specs/<cap>/` nested | `changes/<name>/` flat |
| Knowledge | Scattered in `project.md` | `knowledge/` with index |
| Spec validation | `openspec validate --strict` | None (trust the human) |
| Delta semantics | ADDED/MODIFIED/REMOVED formal | Plain description |
| Archive | Updates `specs/` directory | Just moves to `archive/` |
| Handover | User writes manually | Built-in per change |
| Slash commands | Via `.github/prompts/` | Built-in `/handover`, `/pivot`, etc. |

## Installation

```bash
# Using uv (recommended)
uv tool install sspec

# Using pip
pip install sspec

# From source
git clone https://github.com/yourname/sspec
cd sspec
uv sync
```

## Quick Start

```bash
# Initialize in your project
sspec init

# Create a new change
sspec new add-user-auth

# List changes
sspec list

# Archive completed change
sspec archive add-user-auth
```

## Directory Structure

After `sspec init`:

```
.sspec/
├── AGENTS.md                 # Entry point for AI (read first)
├── knowledge/                # Stable project knowledge
│   ├── index.md             # Required: project overview
│   ├── architecture.md      # Optional: system design
│   ├── conventions.md       # Optional: coding standards
│   └── decisions.md         # Optional: ADRs
├── changes/                  # Active changes
│   ├── <change-name>/
│   │   ├── proposal.md      # Why and what
│   │   ├── tasks.md         # Plan, progress, decisions, pivots
│   │   └── handover.md      # Session continuity
│   └── archive/             # Completed changes
├── prompts/                  # Slash command definitions
│   ├── handover.md
│   ├── pivot.md
│   ├── status.md
│   └── ...
└── handover.md              # Global cross-change handover
```

## Slash Commands

sspec includes predefined prompts for common workflows. Tell your AI assistant:

| Command | Purpose |
|---------|---------|
| `/handover` | Generate handover document for session continuity |
| `/pivot` | Record intent change and update plan |
| `/status` | Summarize current state |
| `/propose <name>` | Create new change proposal |
| `/archive <name>` | Archive completed change |

These are defined in `.sspec/prompts/` and can be customized.

## Workflow

### 1. Start Session

Tell AI: "Read `.sspec/AGENTS.md` first"

The agent will:
1. Read `knowledge/index.md` for project context
2. Check `changes/` for active work
3. Read relevant `handover.md` for continuity

### 2. During Work

- Agent updates `tasks.md` progress in real-time
- On intent change → agent records in `## Pivot` section
- Important decisions → recorded in `## Decisions`

### 3. End Session

Use `/handover` or tell AI "I'm leaving, update handover"

### 4. Complete Change

```bash
sspec archive <change-name>
```

## CLI Reference

```bash
sspec init [--force]           # Initialize .sspec directory
sspec new <name>               # Create new change
sspec list [--all]             # List changes (--all includes archived)
sspec status [<name>]          # Show status summary
sspec archive <name> [--yes]   # Archive completed change
sspec prompt <command>         # Show prompt content
sspec help                     # Show help
```

## Configuration

Optional `.sspec/config.yaml`:

```yaml
# Default language for templates
language: en  # or zh

# Auto-archive after N days of DONE status
auto_archive_days: 7

# Custom prompt directory
prompts_dir: .sspec/prompts
```

## License

MIT
