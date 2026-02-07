---
name: sspec-ask
description: Mid-execution user consultation. USE ACTIVELY to reduce errors and save cost.
metadata:
  author: frostime
  version: 4.0.0
---

# SSPEC Ask Skill

**USE ACTIVELY** — Guessing wastes more tokens than one ask. When in doubt, ask.

---

## When to Trigger (Critical Decision Points)

**REQUIRED use cases** — Agent MUST use sspec ask when:

1. **User explicitly requested** — User mentions ask/confirmation in their request
2. **Information missing** — Cannot proceed reliably without user clarification
3. **Directional choice needed** — Multiple valid approaches exist (not minor tweaks)
4. **Work completion check** — Agent believes task is done
5. **Repeated failures** — Multiple attempts failed, need user insight

**Cost principle**: One ask < rework from wrong guess. Prefer asking over guessing.

### When NOT to Ask

Don't create an ask for trivial decisions where:
- Only one reasonable approach exists
- The choice is easily reversible (e.g., variable naming)
- The answer is available in project.md or existing spec-docs

---

## Workflow

**Step 1**: Create template
```bash
sspec ask create <topic>
```
Creates `.sspec/asks/<timestamp>_<topic>.py`

**Step 2**: Edit the `.py` file
- Fill `REASON` (why asking — for future reference)
- Fill `QUESTION` (what to ask — be specific, provide options when possible)
- Do NOT edit `USER_ANSWER`

**Step 3**: Execute
```bash
sspec ask prompt <path-to-py-file>
```
Prompts user in terminal and captures their answer.

**Step 4**: Automatic lifecycle
After execution, the `.py` file is appended with the user's `ANSWER`, then **converted to `.md`** for permanent record. The `.py` file is deleted.

### Checking Ask History

```bash
sspec ask list
```
Shows pending asks (`.py` — unanswered) and completed asks (`.md` — answered).

### Error Handling

If `sspec ask prompt` reports file not found:
- The ask may have already been answered and archived. Check if `<timestamp>_<topic>.md` exists in `.sspec/asks/`.
- If the `.md` file exists, read the answer from it directly.

---

## Template Format

```python
CREATED = "<iso_timestamp>"

REASON = r"""
<why you're asking - for future reference>
"""

QUESTION = r"""
<your question here>
"""

# User can pre-fill to skip terminal prompt
USER_ANSWER = r""""""
```

After execution, `ANSWER` is appended automatically. Then the file converts to `.md`.

---

## Patterns

### Single Decision Ask

```python
REASON = r"""
Multiple valid approaches for caching layer refactor
"""

QUESTION = r"""
I've identified 3 approaches:

**A) Redis + In-Memory Fallback**
- Pros: High performance, resilient
- Cons: Operational complexity

**B) Pure In-Memory (LRU)**
- Pros: Simple, no external deps
- Cons: Lost on restart

**C) SQLite Cache**
- Pros: Persistent, zero-config
- Cons: Slower than Redis

Which aligns with project priorities?
"""
```

### Batched Questions

When multiple related questions arise, **batch them in a single ask**:

```python
REASON = r"""
Starting auth module implementation, several design decisions needed
"""

QUESTION = r"""
Before starting the auth module, I need a few decisions:

1. **Token format**: JWT (stateless, standard) or opaque tokens (revocable, simpler)?
2. **Session storage**: Redis (fast, needs infra) or DB table (simpler, slower)?
3. **Password hashing**: bcrypt (proven) or argon2 (newer, more resistant)?

For each, my recommendation is in bold if it helps. Override any as you see fit.
"""
```

### Confirmation Before Major Action

```python
REASON = r"""
About to delete and recreate the database schema — irreversible action
"""

QUESTION = r"""
I'm about to run the migration that drops and recreates the `users` table.
This will delete all existing user data in dev.

Proceed? (yes/no)
"""
```

---

## Guidelines

| Do | Don't |
|----|-------|
| Use descriptive topic name (e.g., `auth_approach`) | Use generic names (`q1`, `ask`, `question`) |
| Keep topic name to letters and underscores only | Use non-ASCII or special characters in names |
| Fill `REASON` with context for future reference | Leave `REASON` empty or vague |
| Ask early when uncertain | Guess and risk rework |
| Provide options when choices exist | Leave open-ended if you already have candidates |
| Batch related questions in one ask | Create 3 separate asks for related decisions |
| Check project.md/spec-docs before asking | Ask for info that's already documented |
