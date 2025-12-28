<!-- SSPEC:START -->
# sspec Instructions

Lightweight specification workflow for AI coding assistants. Read this file to begin.

---

## Purpose

sspec enables **cross-session collaboration** by persisting context, plans, and decisions in structured files. It prevents context loss when conversations reset.

---

## Session Lifecycle

### Starting a Session

```
knowledge/index.md      → Project background, tech stack, conventions
changes/                → List active changes
changes/<n>/handover.md → Previous session state
```

**First action**: Run `/context` or manually read the files above.

### During Work

| Event | Action |
|-------|--------|
| Step completed | Update `tasks.md` Progress section |
| User changes direction | Execute `/pivot` |
| Important decision made | Record in `tasks.md` Decisions section |
| Research findings, code snippets | Record in `memo.md` |
| Stable knowledge discovered | Add to `knowledge/` |

### Ending a Session

Update the current change's `handover.md` with:
- Progress summary
- Unfinished items
- Concrete next steps
- Key context for continuation

**Critical**: Always update handover before session ends. This is the bridge to the next session.

---

## Commands

Invoke these in conversation. Full definitions in `prompts/<command>.md`.

### /propose [name]

Create a new change proposal.

**Steps**:
1. Run `sspec new <name>` to scaffold files
2. Fill `proposal.md`: Why (1-2 sentences), What (bullet list), Impact, Out of Scope
3. Draft `tasks.md`: Break into small, verifiable steps ordered by dependency
4. Review with user before implementation

**Skip for**: Bug fixes, typos, config tweaks, adding tests. Do these directly.

**Key principle**: Mark unclear requirements with `[NEEDS CLARIFICATION: question]`. Do not guess.

---

### /status

Report current state.

**Output format**:
```
## Status: [change-name]
State: [STATUS] | Progress: [X/Y]

Recent: [latest accomplishment]
Next: [immediate next action]
Blockers: [none / list]
```

**Data source**: `changes/<n>/tasks.md`

---

### /pivot

Record direction change when user changes their mind.

**Triggers**: User says "wait", "actually", "change of plans", "let's do X instead"

**Steps**:
1. **Stop** current work immediately
2. **Confirm** new intent: "You want to [new direction], correct?"
3. **Record** in `tasks.md > ## Pivot`:
   ```markdown
   ### YYYY-MM-DD HH:MM
   - Previous: [what was planned]
   - New: [new direction]
   - Reason: [why changing]
   ```
4. **Update** Plan section accordingly
5. **Adjust** Status if major pivot (e.g., back to `PLANNING`)

**Principle**: Don't delete history. Pivots are valuable context.

---

### /handover

Generate session handover document.

**Output structure**:
- **Background**: Brief context of task/project
- **Done**: What was accomplished this session
- **Current State**: What works, what doesn't
- **Next Steps**: Concrete actions in priority order
- **Notes**: Constraints, patterns, gotchas

**Style**: High information density. Include file paths, function names, error messages. No filler.

**After writing**: Update the relevant `handover.md` file.

---

### /context

Reload project context.

**Use when**: Starting new session, after long tangent, before major decisions.

**Read**:
1. `knowledge/index.md` + relevant knowledge files
2. Active changes in `changes/`
3. Current change's `proposal.md`, `tasks.md`, `handover.md`

**Output**: Brief confirmation of loaded context.

---

### /archive

Archive a completed change.

**Prerequisites**:
- Status is `DONE` or `REVIEW`
- All tasks completed or explicitly deferred
- No unresolved blockers

**Steps**:
1. Verify change is ready
2. Update final state documents
3. Run `sspec archive <name> --yes`
4. Update global `handover.md` if needed

---

## File Reference

| File | Purpose | Update Frequency |
|------|---------|-----------------|
| `knowledge/index.md` | Project overview, tech stack, conventions, constraints | Stable (rarely) |
| `knowledge/*.md` | Domain knowledge, architecture, decisions | As needed |
| `changes/<n>/proposal.md` | Why and what to change | At creation |
| `changes/<n>/tasks.md` | Plan, progress, decisions, pivots, blockers | Real-time |
| `changes/<n>/memo.md` | Research notes, code snippets, ideas (scratchpad) | During work |
| `changes/<n>/handover.md` | Session continuity | End of session |
| `handover.md` | Cross-change global state | Periodically |

### File Responsibility Boundaries

**`tasks.md`** = Structured project state
- Plan (ordered steps)
- Progress (reverse chronological log)
- Decisions (with reasoning)
- Pivot (direction changes)
- Blockers (current impediments)

**`memo.md`** = Unstructured exploration
- Research notes
- Code snippets
- Half-formed ideas
- References

**Rule**: Mature findings move from `memo.md` → `tasks.md` or `knowledge/`.

### Status Values

`PLANNING` → `IN_PROGRESS` → `BLOCKED` | `REVIEW` → `DONE`

---

## Principles

1. **`tasks.md` is the single source of truth** for current state
2. **Read before doing, update after doing** — avoid duplicate work, keep state in sync
3. **Always update handover before ending** — this is the cross-session bridge
4. **Stable knowledge goes to `knowledge/`** — don't leave valuable info buried in chat
5. **Mark ambiguity explicitly** — use `[NEEDS CLARIFICATION]` instead of guessing

---

## Directory Structure

```
.sspec/
├── AGENTS.md           ← You are here
├── knowledge/
│   └── index.md        ← Project context (read first)
├── changes/
│   ├── <current>/
│   │   ├── proposal.md ← Why and what
│   │   ├── tasks.md    ← Plan and current state
│   │   ├── memo.md     ← Research scratchpad
│   │   └── handover.md ← Session continuity
│   └── archive/        ← Completed changes
├── prompts/            ← Command definitions
└── handover.md         ← Global handover state
```
<!-- SSPEC:END -->
