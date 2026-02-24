---
name: sspec-ask
description: "Mid-execution user consultation via persistent Q&A. USE ACTIVELY — guessing wastes more tokens than asking."
metadata:
  author: frostime
  version: 6.0.0
---

# SSPEC Ask

Persist questions to disk, collect answers via terminal, continue — all within one session.

**Cost equation**: One ask ≈ 30 seconds. One wrong guess ≈ full rework cycle.

---

## When to Use

**REQUIRED**:
1. User explicitly requested consultation
2. Information missing — can't proceed reliably
3. Directional choice — multiple valid approaches
4. Work completion — believe task is done, need verification
5. Repeated failures — multiple attempts failed

**DON'T ask** when: only one reasonable approach, easily reversible, answer in project.md/spec-docs.

**Simple questions**: Use agent env question tool (e.g. VS Code Question).
**Complex / needs record**: Use `sspec ask`.

---

## CLI Workflow

```bash
sspec ask create <topic>         # Create .py template
# → Edit: fill REASON + QUESTION
sspec ask prompt <path-to-py>    # Collect user answer → auto-converts to .md
sspec ask list                   # Check pending/completed asks
```

### Steps

1. `sspec ask create <topic>` — creates `.sspec/asks/<timestamp>_<topic>.py`
2. Edit the `.py`: fill `REASON` (why asking) and `QUESTION` (specific, with options)
3. `sspec ask prompt <path>` — user answers → file converts to `.md` → `.py` deleted
4. Read the `.md` for user's answer, continue work

### Error Handling

If `prompt` says file not found → check if `.md` already exists (`sspec ask list`).

---

## Patterns

### Plan Confirmation (Most Common)

```python
REASON = r"""Change plan ready for review"""
QUESTION = r"""
Here's my plan for <change-name>:
**Problem**: <summary>
**Approach**: <core idea>
**Key files**: <list>
**Tasks**: <count>
Proceed? Adjustments?
"""
```

### Decision with Options

```python
REASON = r"""Multiple valid approaches for caching"""
QUESTION = r"""
**A) Redis** — fast, needs infra
**B) SQLite** — persistent, zero-config
**C) In-Memory** — simple, lost on restart
Which aligns with project priorities?
"""
```

### Batched Questions

```python
REASON = r"""Several design decisions needed before starting"""
QUESTION = r"""
1. **Token format**: JWT or opaque?
2. **Session storage**: Redis or DB?
3. **Password hashing**: bcrypt or argon2?
"""
```

## Long Content

Long drafts → write to `.sspec/tmp/`, reference path in QUESTION.
Ask files should stay focused.

## Guidelines

| Do | Don't |
|----|-------|
| Descriptive topic (`auth_approach`) | Generic name (`q1`) |
| Fill REASON with context | Leave REASON empty |
| Provide options when possible | Leave open-ended if you have candidates |
| Batch related questions | Create separate asks for related items |
| Link important asks in handover.md | Let records become disconnected |
