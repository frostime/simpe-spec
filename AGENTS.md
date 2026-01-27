# SSPEC Project Development Guide

## What is This Project?

**sspec** is a spec-driven CLI framework that helps users practice vibe coding with AI agents. This project is **self-hosted** - we use sspec itself to manage sspec's development.

⚠️ **Important for Agents**: This project develops the SSPEC framework itself. Do NOT use the SSPEC protocol embedded below for development guidance - it may be outdated.

---

## For AI Agents Working on SSPEC

### 📍 Ground Truth

**The authoritative SSPEC protocol is the template we're developing**:
- **Template source**: [src/sspec/templates/AGENTS.md](src/sspec/templates/AGENTS.md)
- This is what gets copied to user projects during `sspec project init`

**When working on SSPEC features**:
1. Read the template files to understand current behavior
2. Test changes using `.venv\Scripts\sspec.exe` in `tmp/` directories
3. Refer to [.sspec/](.sspec/) for this project's changes and tasks

### 🧪 Testing Protocol

**Always test CLI changes before considering them complete**:

```powershell
# Create test directory
cd tmp
New-Item -ItemType Directory test_<feature_name>
cd test_<feature_name>

# Test using the editable install
..\..\..\.venv\Scripts\sspec.exe project init [--options]
..\..\..\.venv\Scripts\sspec.exe change new example
# ... test other commands
```

**Verification checklist**:
- ✅ Generated files match templates in `src/sspec/templates/`
- ✅ CLI output is clear and helpful
- ✅ File structure is correct
- ✅ Error handling works as expected

### 🛠️ Development Setup

**Tech Stack**:
- Python 3.11+
- uv for package management
- Click for CLI
- Rich for terminal output

**Key directories**:
- `src/sspec/` - Source code
  - `cli.py` - Entry point
  - `commands/` - CLI command implementations
  - `core.py` - Core utilities
  - `templates/` - File templates (AGENTS.md, spec.md, etc.)
- `.sspec/` - This project's own sspec data (dogfooding)
- `tmp/` - Testing sandbox

**Installation (editable mode)**:
```powershell
# Install/reinstall after code changes
uv pip install -e .
```

### 📋 Conventions

**Code Style**:
- Follow existing patterns in codebase
- Line length ≤ 90 characters (linter enforced)
- Use type hints for function signatures
- Docstrings for public functions

**Testing Philosophy**:
- Real CLI testing over mocks (test in `tmp/`)
- Verify generated output matches templates
- Test both happy path and error cases

**Commit Message Style**:
- Prefix: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`
- Example: `feat: add --skill-loc parameter to project init`

---

## Project Context and Glossary

| Term | Definition |
|------|------------|
| **sspec** | The CLI tool / framework this project builds |
| **template** | Files in `src/sspec/templates/` copied to user projects |
| **AGENTS.md** | The protocol file for AI agents (the template we're developing) |
| **self-hosting** | Using sspec to manage sspec's own development |
| **change** | A unit of work tracked in `.sspec/changes/` |
| **vibe coding** | Iterative, AI-assisted development workflow |

---

**Agent Recommendations**:
1. **Always test in tmp/**: Don't assume template changes work until tested
2. **Use .sspec/ for planning**: The structure genuinely helps organize complex refactors
3. **Update handover.md**: It's tedious but critical for session continuity
4. **Leverage auto mode**: For medium complexity tasks, it saves back-and-forth

---

## Quick Reference

### Frequently Modified Files

When working on features:

| File | Purpose | When to Edit |
|------|---------|--------------|
| `src/sspec/templates/AGENTS.md` | User-facing protocol | Improving agent guidance |
| `src/sspec/templates/skills/sspec/SKILL.md` | Extended reference | Status rules, edge cases |
| `src/sspec/commands/*.py` | CLI implementations | Adding/modifying commands |
| `src/sspec/core.py` | Shared utilities | Cross-cutting functionality |
| `pyproject.toml` | Package metadata | Dependencies, version, entry points |

### Common Development Tasks

```powershell
# Reinstall after changes
uv pip install -e .

# Test in clean environment
cd tmp; mkdir test_xyz; cd test_xyz
..\..\..\.venv\Scripts\sspec.exe project init

# Check errors
cd src; python -m pylance (if available)

# List changes (dogfooding)
.venv\Scripts\sspec.exe change list
```

---

**Remember**: You're developing the framework that guides other agents. Test thoroughly, write clear templates, and use `.sspec/` to track your own work.

---

<!-- Legacy SSPEC protocol below - OUTDATED, kept for historical reference only -->
<!-- For current protocol, see src/sspec/templates/AGENTS.md -->

<details>
<summary>⚠️ MIGHT BE OUTDATED SSPEC Protocol (Click to expand - DO NOT USE for development)</summary>

<!-- SSPEC:START -->
# .sspec Agent Protocol

SSPEC_SCHEMA::3.1

## Hard Rules
- `.sspec` = single source of truth for planning/tracking/handover.
- All `@xxx` are explicit user commands, not auto-executable.
------

## Workflow Overview

**Typical session flow**:
1. **Start**: User triggers `@change <name>` or `@resume` → Agent loads context
2. **Work**: Agent implements tasks, updates `tasks.md` progress
3. **Pivot**: If user says `@argue` → Agent stops, reassesses, revises plan
4. **Sync**: After autonomous coding → User says `@sync` → Agent updates .sspec
5. **End**: User says `@handover` → Agent writes session summary

**Cross-session continuity**: `handover.md` bridges sessions. Each handover should enable next session to start in <30 seconds.
------

## User Triggers

### `@change <name>`
Switch/create change context.
1. If `changes/<name>/` exists → read spec.md, tasks.md, handover.md
2. If not exists → run shell `sspec change new <name>`,  fill spec.md with user's help
3. Output: context summary + next actions

### `@resume`
Resume work after session break. e.g. Start a New Chat in copilot, cursor etc, or start new cli for claude code.
1. Pick user specified change with status ∈ {DOING, BLOCKED, REVIEW}
2. Read: handover.md → tasks.md → spec.md
3. Output: current state + next actions

### `@handover`
End session and write handover doc, enabling next agent quickly know the context.
1. Update handover.md with session summary, must include
  * Background of the Major Task
  * What Was Accomplished in the Previous (Current) Session
  * Current Status
  * Next Steps
  * Conventions and Standards to Follow
2. Update tasks.md progress
3. Update spec.md status if changed

### `@sync`
After autonomous coding sessions (Claude Code, Copilot, etc.), ensure .sspec reflects actual progress.
1. Scan recent changes (agent chat history, git diff or timestamps)
2. For active change, update:
   - `tasks.md`: mark completed tasks, add discovered tasks
   - `spec.md`: update status in front yaml if appropriate


### `@argue`
Handle user disagreement with implementation approach, design, or requirements during implementing.
1. STOP current implementation
2. Analyze scope: detail / design / requirement level
3. Update relevant files, add PIVOT marker if major change
4. Await user confirmation
------

## Folder Structure

```text
.sspec/
├── project.md              # Project overview, conventions
├── changes/<name>/
│   ├── spec.md             # WHY/WHAT: problem, decisions
│   ├── tasks.md            # HOW: executable tasks + progress
│   └── handover.md         # SESSION BRIDGE: done/now/next
└── requests/*.md           # Incoming requests
```
------

## File Responsibilities

| File | Content | Update When |
|------|---------|-------------|
| spec.md | Problem, constraints, decisions | Strategy/status change |
| tasks.md | Tasks (<2h each) + progress | Planning, task completion |
| handover.md | Done / Now / Next | Every session end |
| requests/*.md | Raw user requests | Lifecycle: OPEN → DOING → DONE |

------

## Skills

For detailed guidance on status definitions, transitions, and edge cases, read the **sspec** skill:
- Location: `.github/skills/sspec/SKILL.md` or `.claude/skills/sspec/SKILL.md`
- Use when: uncertain about status meanings, transition rules, or quality standards

## CLI Reference

```shell
sspec change new <name>      # Create change
sspec change list            # List changes
sspec change archive <name>  # Archive completed change
sspec project status         # Show project overview
sspec request <name>         # Create request
```
<!-- SSPEC:END -->

</details>