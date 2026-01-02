<!-- SSPEC:START -->
# .sspec Agent Protocol

SSPEC_SCHEMA::{{SCHEMA_VERSION}}

## 0) Hard Rules
- High-signal only: bullets > prose. No filler.
- Treat `.sspec` as the single source of truth for planning/tracking/handover.
- All `@xxx` triggers are explicit user commands, not auto-executable.

## 1) Status Definitions

### Change Status (in spec.md front yaml)
| Status | Meaning | Agent Action |
|--------|---------|--------------|
| PLANNING | Defining scope & approach | Update spec.md (A, B, C sections) |
| DOING | Implementation in progress | Update tasks.md progress, handover.md |
| BLOCKED | Waiting on external dependency | Document blocker in spec.md section D |
| REVIEW | Implementation complete, awaiting verification | Prepare demo, summarize in handover.md |
| DONE | Completed and verified | Ready for `sspec archive` |

### Request Status (in request front yaml)
| Status | Meaning |
|--------|---------|
| OPEN | New request, not yet processed |
| DOING | In progress, linked to a change |
| DONE | Completed |

---

## 2) User Triggers

### 2.1 `@change <name>` — Switch/Create change context
1. Set active change = `<name>`
2. If `changes/<name>/` exists → read spec.md, tasks.md, handover.md (in order)
3. If not exists → run `sspec change <name>`, then fill spec.md
4. Output: context summary + next 3 actions

### 2.2 `@resume` — Recover session context
1. Select active change:
  - If user specified name → use it
  - Else → pick most recently modified change with status ∈ {DOING, BLOCKED, REVIEW}
2. Read: handover.md → tasks.md → spec.md
3. Output: "Resuming <name>..." + current state + next actions

### 2.3 `@handover` — End session cleanly
1. Update `changes/<change>/handover.md` with session summary
2. Update `tasks.md`: mark completed tasks, add discovered tasks
3. Update front yaml `status` if changed
4. Output: confirmation + handover content written

### 2.4 `@sync` — Sync .sspec with current reality
**Purpose**: After autonomous coding sessions (Claude Code, Copilot, etc.), ensure .sspec reflects actual progress.

Do:
1. Scan recent file changes in repo (git diff or file timestamps)
2. For active change, update:
  - `tasks.md`: mark completed tasks, add discovered tasks
  - `spec.md`: update status in front yaml if appropriate
  - `handover.md`: summarize what was accomplished
3. Output: diff summary of .sspec updates

---

## 3) Folder Structure
```
.sspec/
├── project.md              # Project overview, conventions, constraints
├── changes/<name>/
│   ├── spec.md             # WHY/WHAT: problem, constraints, decisions, solution
│   ├── tasks.md            # HOW: executable tasks with verification
│   └── handover.md         # SESSION BRIDGE: done/now/next
├── requests/*.md           # Incoming requests backlog
└── skills/*.md             # Reusable knowledge & prompts
```

---

## 4) File Responsibilities

### spec.md (WHY/WHAT)
- **Contains**: problem statement, constraints, decisions, solution outline
- **Front yaml**: status, type, created
- **Update when**: strategy/decision changes, status transitions

### tasks.md (HOW)
- **Contains**: tasks completable in <2h, each with verification criteria
- **Update when**: before coding (plan), after completing tasks (progress)

### handover.md (SESSION BRIDGE)
- **Contains**: Done / Now / Next / Key Files / Commands
- **Update when**: end of session, before switching changes, after `@sync`

### requests/*.md (INTAKE)
- **Contains**: raw user requests with front yaml metadata
- **Lifecycle**: OPEN → link to change → DOING → DONE
<!-- SSPEC:END -->
