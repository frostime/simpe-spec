# sspec Instructions

Entry point for AI assistants. Read this file first when starting a session.

## Quick Start

1. Read `knowledge/index.md` for project context
2. Check `changes/` for active work
3. Read relevant `handover.md` for session continuity

## Workflow

### Starting a Session

```
knowledge/index.md   → Project background, tech stack, conventions
changes/             → List active changes
changes/<n>/handover.md → Previous session state
```

### During Work

| Event | Action |
|-------|--------|
| Step completed | Update `tasks.md` Progress section |
| User changes mind | Record in `tasks.md` Pivot section |
| Important decision | Add to `tasks.md` Decisions section |
| New knowledge discovered | Consider adding to `knowledge/` |

### Ending a Session

Update the current change's `handover.md` with:
- Progress summary
- Unfinished items
- Next steps
- Key context for continuation

## File Responsibilities

| File | Purpose | Update Frequency |
|------|---------|-----------------|
| `knowledge/index.md` | Project overview, tech stack | Rarely |
| `knowledge/*.md` | Domain knowledge, architecture | As needed |
| `changes/<n>/proposal.md` | Why and what to change | At creation |
| `changes/<n>/tasks.md` | Plan, progress, decisions, pivots | Real-time |
| `changes/<n>/handover.md` | Session continuity | End of session |
| `handover.md` | Cross-change global state | Periodically |

## Slash Commands

Predefined prompts in `prompts/` directory. User can invoke with:

- `/handover` — Generate session handover
- `/pivot` — Record intent change
- `/status` — Summarize current state
- `/propose` — Create new change
- `/archive` — Archive completed change

Read `prompts/<command>.md` for full prompt content.

## Pivot Handling

When user says "wait", "change of plans", "let's do X instead":

1. **Stop** current work immediately
2. **Confirm** new intent: "You want to change to X?"
3. **Record** in `tasks.md` under `## Pivot`:
   ```markdown
   ### YYYY-MM-DD HH:MM
   - Previous: [what was planned]
   - New: [new direction]
   - Reason: [user's reasoning]
   ```
4. **Update** the Plan section accordingly

## Key Principles

- `tasks.md` is the single source of truth for current state
- Read before doing, update after doing
- Always update handover before ending session
- Stable knowledge goes to `knowledge/`, not conversation

## Directory Quick Reference

```
.sspec/
├── AGENTS.md           ← You are here
├── knowledge/
│   └── index.md        ← Read this for context
├── changes/
│   └── <current>/
│       ├── proposal.md ← Why we're doing this
│       ├── tasks.md    ← What to do, current state
│       └── handover.md ← Session continuity
├── prompts/            ← Slash command definitions
└── handover.md         ← Global cross-change state
```
