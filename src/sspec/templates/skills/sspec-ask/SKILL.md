---
name: sspec-ask
description: "Mid-execution user consultation via persistent Q&A. USE ACTIVELY — guessing wastes more tokens than asking."
metadata:
  author: frostime
  version: 7.0.0
---

# SSPEC Ask

Persist questions to disk, collect answers via terminal, continue — all within one session.

**Cost equation**: One ask ≈ 30 seconds. One wrong guess ≈ full rework cycle.

---

## sspec ask vs Built-in Question Tool

Two tools, different purposes. Choose correctly:

| | `sspec ask` (CLI) | Built-in question tool (e.g. VS Code Question) |
|---|---|---|
| **Record** | Persists as `.md` file in `.sspec/asks/` | Gone after session |
| **Use when** | Architecture decisions, plan approval, direction choices, anything worth recording | Quick yes/no, mode switch confirmation, session-end check |
| **Content** | Structured (REASON + QUESTION with options) | One-liner |
| **Default** | **Prefer this** when uncertain | Only when answer is ephemeral |

**Rule**: If the question involves a decision that future agents might need to understand → use `sspec ask`.

---

## CLI Workflow

```bash
sspec ask create <topic>          # Create .yml template
# → Edit: fill reason + question
sspec ask prompt <path-to-yml>    # Collect user answer → auto-converts to .md
sspec ask list                   # Check pending/completed asks
```

### Steps

1. `sspec ask create <topic>` — creates `.sspec/asks/<timestamp>_<topic>.yml`
2. Edit the `.yml`: fill `reason` (why asking) and `question` (specific, with options)
3. `sspec ask prompt <path>` — user answers → file converts to `.md` → pending `.yml` deleted
4. Read the `.md` for user's answer, continue work

### Error Handling

If `prompt` says file not found → check if `.md` already exists (`sspec ask list`).

---

## Content Rules

**Keep ask files focused.** The QUESTION field is for the question itself, not for long analysis.

| Content type | Where to put it |
|---|---|
| The question + brief options | `question` field in `.yml` |
| Long analysis, draft plans, design docs | Write to `.sspec/tmp/<topic>.md`, reference path in QUESTION |
| Code samples or large tables | Write to file, reference path |

**Anti-pattern**: Stuffing 200+ lines of analysis into QUESTION field.
**Correct**: Write analysis to `.sspec/tmp/design-draft.md`, then in QUESTION: "See draft at `.sspec/tmp/design-draft.md`. Does this approach work?"

---

## Patterns

### Plan Confirmation (Most Common)

```yaml
reason: |
  Change plan ready for review
question: |
Here's my plan for <change-name>:
**Problem**: <summary>
**Approach**: <core idea>
**Key files**: <list>
**Tasks**: <count>
Proceed? Adjustments?
```

### Decision with Options

```yaml
reason: |
  Multiple valid approaches for caching
question: |
**A) Redis** — fast, needs infra
**B) SQLite** — persistent, zero-config
**C) In-Memory** — simple, lost on restart
Which aligns with project priorities?
```

### Batched Questions

```yaml
reason: |
  Several design decisions needed before starting
question: |
1. **Token format**: JWT or opaque?
2. **Session storage**: Redis or DB?
3. **Password hashing**: bcrypt or argon2?
```

---

## Guidelines

| Do | Don't |
|----|-------|
| Descriptive topic (`auth_approach`) | Generic name (`q1`) |
| Fill REASON with context | Leave REASON empty |
| Provide options when possible | Leave open-ended if you have candidates |
| Batch related questions | Create separate asks for related items |
| Link important asks in handover.md | Let records become disconnected |
| Long content → write to file, reference in QUESTION | Stuff everything into QUESTION field |
