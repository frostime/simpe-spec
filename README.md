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
sspec init
```

This creates:
```
.sspec/
├── AGENTS.md           # AI reads this first
├── knowledge/
│   └── index.md        # Your project context
├── changes/            # Active work
├── prompts/            # Command definitions
└── handover.md         # Cross-session state
```

### Configure

Edit `.sspec/knowledge/index.md` with your project info:
- Tech stack
- Coding conventions
- Key constraints

This is the context AI will always have access to.

---

## Daily Workflow

### Starting a Feature

Tell your AI:
```
/propose add-user-auth
```

AI will:
1. Create `changes/add-user-auth/` with proposal, tasks, memo, handover
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

These work in any AI tool that reads AGENTS.md (Claude Code, Cursor, etc.)

---

## CLI Commands

```bash
sspec init              # Initialize .sspec in current directory
sspec new <name>        # Create new change
sspec list              # List all changes
sspec status            # Show status overview
sspec archive <name>    # Archive completed change
sspec prompt --list     # List available prompts
```

---

## File Structure Explained

### For the Project

| File | Purpose | You edit? |
|------|---------|-----------|
| `knowledge/index.md` | Project context, tech stack, conventions | Yes, initially |
| `knowledge/*.md` | Domain knowledge, architecture docs | As needed |
| `handover.md` | Global cross-change state | AI updates |

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

1. **Start with good context**: Fill `knowledge/index.md` thoroughly
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

**Q: Can I customize the prompts?**

Yes. Edit files in `.sspec/prompts/` to match your preferences.

**Q: How is this different from just chatting?**

Chat context disappears. sspec files persist. You never re-explain your project.

---

## License

MIT
