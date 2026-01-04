# sspec

[中文文档](./README_zh-CN.md)

**Lightweight specification workflow for AI coding assistants.**

sspec solves a simple problem: AI assistants forget everything when a conversation ends. Your carefully explained context, decisions, and progress—all gone.

sspec gives AI a persistent memory through structured files that survive across sessions.

---

## How It Works

```
You: "Add user authentication"
AI: reads .sspec/AGENTS.md → understands the workflow
AI: creates proposal, breaks into tasks, tracks progress
... conversation ends ...

New session:
You: "Continue where we left off"
AI: reads handover.md → knows exactly what was done and what's next
```

---

## Quick Start

### Install

```bash
pip install sspec
```

### Initialize

```bash
cd your-project
sspec project init
```

This creates:
```
.sspec/
├── AGENTS.md           # AI reads this first
├── project.md          # Project context (tech stack, constraints, notes)
├── changes/            # Active change proposals
├── requests/           # Ad-hoc user requests for the AI
└── skills/             # Custom AI skills and guidance
```

### Configure

Edit `.sspec/project.md` with your project info:
- Tech stack
- Coding conventions
- Key constraints

This is the primary project context the AI will use when assisting you.

---

## Daily Workflow

### Starting a Feature

Tell your AI (chat command):
```
/propose add-user-auth
```

Or use the CLI to create a change:
```
sspec change new add-user-auth
```

AI will:
1. Create `changes/add-user-auth/` with `spec.md`, `tasks.md`, and `handover.md`
2. Help you define what and why
3. Break work into small, verifiable steps

### During Work

AI automatically tracks:
- **Progress**: What's done, what's next
- **Decisions**: Why you chose X over Y
- **Pivots**: When you change direction

You can check status anytime:
```
/status
```

### Ending a Session

Before closing the conversation:
```
/handover
```

AI writes a handover document capturing:
- What was accomplished
- Current state
- Exact next steps
- Gotchas to remember

### Next Session

Start with:
```
/context
```

AI reloads everything and continues seamlessly.

---

## Commands

| Command | What it does |
|---------|--------------|
| `/propose <name>` | Create new change proposal |
| `/status` | Show current state |
| `/pivot` | Record when you change direction |
| `/handover` | Generate session handover |
| `/context` | Reload project context |
| `/archive` | Archive completed change |

These are chat workflow examples that AI assistants can follow. CLI equivalents (use these in your shell) include `sspec change new`, `sspec change status`, `sspec change archive`, `sspec request`, and `sspec skill`.

---

## CLI Commands

```bash
# Project-level
sspec project init              # Initialize .sspec in current directory
sspec project update            # Update built-in templates
sspec project status            # Show project overview

# Change management
sspec change new <name>         # Create a new change (proposal)
sspec change list               # List active changes
sspec change status <name>      # Show detailed status for a change
sspec change archive <name>     # Archive completed change

# Requests
sspec request                   # Create a new request (opens file)
sspec request --list            # List requests
sspec request --show <name>     # Show a request
sspec request <name> --link <change>  # Link a request to a change

# Skills
sspec skill list                # List skills
sspec skill new <name>          # Create a new skill (simple or complex)
```

---

## File Structure Explained

### For the Project

| File | Purpose | You edit? |
|------|---------|-----------|
| `project.md` | Project context, tech stack, conventions | Yes, initially |
| `requests/*.md` | Ad-hoc requests for the AI | As needed |
| `skills/*.md` | Custom skills & guidance for assistant | As needed |
| `handover.md` | Global cross-session state (optional) | AI updates |

### For Each Change

| File | Purpose | You edit? |
|------|---------|-----------|
| `proposal.md` | Why and what to change | Review & approve |
| `tasks.md` | Plan, progress, decisions | AI updates |
| `memo.md` | Research notes, code snippets | AI's scratchpad |
| `handover.md` | Session continuity | AI updates |

---

## Example Session

**Session 1:**
```
You: Let's add dark mode to the app. /propose dark-mode

AI: Created change: dark-mode
    - Proposal: Add dark mode toggle with system preference detection
    - Tasks: 5 steps identified
    Ready to review?

You: Looks good, let's start.

AI: [implements first 3 tasks, updates progress]

You: I need to go. /handover

AI: Handover saved.
    Done: Theme provider, toggle component, CSS variables
    Next: Persist preference, add to settings page
```

**Session 2:**
```
You: /context

AI: Context loaded.
    Project: my-app (React + TypeScript)
    Active: dark-mode (IN_PROGRESS, 3/5 tasks)
    Next: Persist user preference to localStorage

    Continuing from where we left off...
```

---

## Tips

### For Best Results

1. **Start with good context**: Fill `.sspec/project.md` thoroughly (tech stack, constraints, common commands, and important files).
2. **Review proposals**: Don't let AI guess requirements
3. **Use `/handover` religiously**: It's the bridge between sessions
4. **Keep changes small**: One feature = one change

### When to Skip sspec

- Quick bug fixes
- Typos and formatting
- Simple config changes

Just do these directly—no proposal needed.

---

## FAQ

**Q: Does this work with [my AI tool]?**

Any tool that reads AGENTS.md files: Claude Code, Cursor, Windsurf, GitHub Copilot, etc.

**Q: What if AI doesn't follow the workflow?**

Tell it: "Read .sspec/AGENTS.md first"

**Q: Can I customize the assistant's behavior?**

Yes. Add or edit files under `.sspec/skills/` to provide skills and usage guidance; edit `.sspec/project.md` for project-specific context. Templates in the package (used by `sspec project init`) can be updated via `sspec project update`.

**Q: How is this different from just chatting?**

Chat context disappears. sspec files persist. You never re-explain your project.

---

## License

MIT
