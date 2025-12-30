# sspec Instructions

Instructions for AI assistants using sspec for collaboration.

## TL;DR Quick Checklist

**Session start:**
- [ ] Read `knowledge/index.md` for project context
- [ ] Run `sspec list` to see active changes
- [ ] Read current change's `handover.md` for previous session state
- [ ] Read current change's `spec.md` for plan and progress

**During work:**
- [ ] Update `spec.md` Progress after completing steps
- [ ] Record important decisions in `spec.md` Decisions
- [ ] If user changes direction, record PIVOT in Decisions immediately

**Session end:**
- [ ] Write to `handover.md`: Done, Current State, Next Steps, Gotchas
- [ ] Update timestamp in handover.md

**Creating new change:**
1. Run `sspec new <name>`
2. Fill `spec.md`: Why (1-2 sentences), What (bullets), Tasks (ordered steps)
3. Review with user before implementation

## Three-Stage Pattern

### Stage 1: Context Loading
User says: `@context`, "load context", or starts new session

**Workflow:**
1. Read `knowledge/index.md`
2. List active changes with `sspec list`
3. Read `changes/<name>/handover.md` — where previous session left off
4. Read `changes/<name>/spec.md` — current plan and state
5. Output: "Loaded context for <name>. Status: <STATUS>, Progress: <X/Y>. Last session: [brief summary from handover]."

### Stage 2: Working
During active work, track progress in files:

**When user requests new feature/change:**
- Simple fix (bug, typo, config)? → Do directly
- Structural change? → Create proposal with `@new`

**When user changes direction:**
- User says: "wait", "actually", "change plans"
- Stop immediately, confirm new intent
- Record in `spec.md` Decisions:
  ```
  [YYYY-MM-DD] PIVOT
  - From: [old plan]
  - To: [new direction]
  - Reason: [why]
  - Tried: [what didn't work, if applicable]
  ```
- Update Tasks section (strike through abandoned: `~~- [ ] old~~`, add new)

**Recording decisions:**
- Format: `[YYYY-MM-DD] Decision — Rationale`
- Example: `[2025-01-01] Use SQLite over Postgres — Simpler for MVP, can migrate later`

**Recording progress:**
- Format: `[YYYY-MM-DD] What was done`
- Reverse chronological (latest on top)
- Be specific: files modified, features working

### Stage 3: Handover
User says: `@handover`, "end session", "I'm leaving"

**Workflow:**
1. Write to `changes/<name>/handover.md`:
```markdown
# Handover: <name>

**Updated**: [current timestamp]

## Done
- [Specific files modified]
- [Features implemented]
- [Tests passing]

## Current State
**Working**: [what functions correctly]
**Not working**: [what's broken/incomplete]

## Next Steps
1. [First concrete action — file path, function name, exact command]
2. [Second action]
3. [Third action]

## Gotchas
- [Non-obvious issues next session should know]
- [Failed approaches to avoid]
```
2. Verify: Could another AI continue without asking questions?

## File Structure

```
.sspec/
├── AGENTS.md           # This file
├── knowledge/
│   └── index.md        # Project context
├── changes/
│   ├── <name>/
│   │   ├── spec.md     # Plan, tasks, progress, decisions
│   │   └── handover.md # Session bridge
│   └── archive/
├── requests/           # User feature requests
└── handover.md         # Global project state
```

## File Formats

### spec.md

```markdown
# <change-name>

STATUS::PLANNING
<!-- PLANNING | IN_PROGRESS | BLOCKED | REVIEW | DONE -->

## Why
[1-2 sentence problem statement]

## What
- [Concrete change 1]
- [Concrete change 2]

## Tasks
- [ ] 1. [First verifiable step]
- [ ] 2. [Second step]
- [ ] 3. [Verification/testing]

## Progress
[YYYY-MM-DD] Completed X
[YYYY-MM-DD] Started Y

## Decisions
[YYYY-MM-DD] Chose A over B — Reason
[YYYY-MM-DD] PIVOT
- From: X
- To: Y
- Reason: ...
- Tried: ...

## Notes
[Research notes, code snippets, references]
```

### handover.md

```markdown
# Handover: <name>

**Updated**: [timestamp]

## Done
[What was completed — files, features, tests]

## Current State
**Working**: [what functions]
**Not working**: [what's broken]

## Next Steps
1. [Concrete action with file paths/commands]
2. [Second action]

## Gotchas
- [Non-obvious issues]
- [Failed approaches]
```

## CLI Commands

| Command | Usage |
|---------|-------|
| `sspec new <name>` | Create change (generates spec.md + handover.md) |
| `sspec list` | List all changes |
| `sspec list --all` | Include archived |
| `sspec status` | Show overview |
| `sspec status <name>` | Show specific change detail |
| `sspec archive <name> --yes` | Archive completed change |
| `sspec request <name>` | Create user request |

**Important:** Use CLI to create/archive changes. Do not manually create directories.

## Decision Logic

```
User request →
├─ Bug fix / typo / config?
│   → Do directly
│
├─ New feature / structural change?
│   → User says "@new" or "create proposal"
│   → Run: sspec new <name>
│   → Fill spec.md
│   → Review with user
│
├─ Direction change mid-work?
│   → User says "wait" / "actually" / "change plans"
│   → Stop current work
│   → Confirm new intent
│   → Record PIVOT in spec.md Decisions
│   → Update Tasks
│
├─ Session ending?
│   → User says "@handover" or "end session"
│   → Write to handover.md
│   → Update timestamp
│
└─ Session starting?
    → User says "@context" or "load context"
    → Read knowledge/, handover.md, spec.md
    → Output brief confirmation
```

## Common Triggers

**@context** variations:
- "load context", "reload context", "what's the state", "where are we"

**@new** variations:
- "create proposal", "new feature", "start new change"

**@pivot** variations:
- "wait", "actually", "change of plans", "let's do X instead"

**@handover** variations:
- "end session", "I'm leaving", "write handover", "session end"

**@archive** variations:
- "archive this", "this is done", "complete this change"

## Error Handling

| Situation | Action |
|-----------|--------|
| No handover.md from previous session | Note gap, ask user for context |
| Invalid STATUS in spec.md | Ask user to clarify or default to PLANNING |
| Multiple active changes | Ask: "Which change should I work on?" |
| Unclear user intent | Ask clarifying question before proceeding |
| Missing files | Note issue, suggest running appropriate CLI command |

## Principles

1. **Handover bridges sessions** — Always update before ending
2. **Context before action** — Load state at session start
3. **Pivot immediately** — When direction changes, stop and record
4. **Be specific** — File paths, function names, exact commands in handover
5. **Mark uncertainty** — Use `[?]` for unclear requirements
6. **CLI for structure** — Don't manually create change directories

## Before Any Task

**Context Checklist:**
- [ ] Read `knowledge/index.md`
- [ ] Check active changes with `sspec list`
- [ ] Read relevant `handover.md` and `spec.md`
- [ ] Understand current STATUS and progress

**Before Creating Change:**
- Check if similar change already exists
- Confirm with user if it's worth a formal proposal
- Ask 1-2 clarifying questions if request is ambiguous

## Validation Checklist

**Before ending session:**
- [ ] handover.md has current timestamp
- [ ] Next Steps are concrete (not vague like "continue working")
- [ ] Gotchas document failed approaches
- [ ] Current State is accurate right now
- [ ] Another AI could continue without questions

**Before implementing:**
- [ ] spec.md Why and What are clear
- [ ] Tasks are ordered by dependency
- [ ] Each task is verifiable
- [ ] User has reviewed and approved

## Quick Reference

### File Purposes
- `spec.md` — Plan and tracking
- `handover.md` — Session bridge
- `knowledge/*.md` — Stable context
- `requests/*.md` — User feature requests

### Status Values
`PLANNING` → `IN_PROGRESS` → `BLOCKED` | `REVIEW` → `DONE`

### Key Insight
AI loses context between sessions. sspec persists state in files. The handover.md file is the bridge between sessions.
