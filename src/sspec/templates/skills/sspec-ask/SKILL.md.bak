---
name: sspec-ask
description: "Mid-execution user consultation via persistent Q&A. USE ACTIVELY — especially in agent scenarios where @ask extends single-session effectiveness."
metadata:
  author: frostime
  version: 5.0.0
---

# SSPEC Ask Skill

**USE ACTIVELY** — Guessing wastes more tokens than one ask. When in doubt, ask.

---

## Why @ask Matters

In agent/copilot scenarios, the interaction model is: Agent works autonomously → hits a decision point → needs user input.

Some platforms offer basic tools like `Question` in copilot， opencode etc. However, these solutions are insufficient for handling complex, multi-turn consultations.

Without `@ask`: Agent guesses, potentially wastes an entire implementation cycle. Or stops and loses context while waiting.

With `@ask`: Agent persists the question to disk, collects the answer via terminal, and continues — all within the same session. The ask record also serves as permanent decision documentation.

**Cost equation**: One ask ≈ 30 seconds of user time. One wrong guess ≈ full rework cycle.

---

## When to Trigger (Critical Decision Points)

**REQUIRED use cases** — Agent MUST use sspec ask when:

1. **User explicitly requested** — User mentions ask/confirmation in their request
2. **Information missing** — Cannot proceed reliably without user clarification
3. **Directional choice needed** — Multiple valid approaches exist (not minor tweaks)
4. **Work completion check** — Agent believes task is done, needs user verification
5. **Repeated failures** — Multiple attempts failed, need user insight

### When NOT to Ask

Don't create an ask for trivial decisions where:
- Only one reasonable approach exists
- The choice is easily reversible (e.g., variable naming)
- The answer is available in project.md or existing spec-docs

**Use question tool (if exists) for simple question**.

---

## Workflow

### CLI Commands (Agent-Driven)

| Command | When | Notes |
|---------|------|-------|
| `sspec ask create <topic>` | Need to ask user something | `<topic>` is a slug: `auth_approach`, `redis_vs_db` |
| `sspec ask prompt <file.py>` | Collect user's answer | Pass the `.py` file path from create output |
| `sspec ask list` | Check pending/completed asks | Shows `.py` (pending) and `.md` (answered) |

**Ergonomics**:
- `create` generates the `.py` template → Agent fills REASON + QUESTION → runs `prompt`
- `prompt` opens terminal for user input OR get the user prefilled answer before `prompt` is approvaed to run → auto-converts to `.md` record → deletes `.py`
- The entire cycle happens within one agent session — no context loss

### Step-by-Step

**Step 1**: Create template
```bash
sspec ask create <topic>
```
Creates `.sspec/asks/<timestamp>_<topic>.py`

**Step 2**: Edit the `.py` file
- Fill `REASON` (why asking — for future reference and memory)
- Fill `QUESTION` (be specific, provide options when possible)
- Do NOT edit `USER_ANSWER`

**Step 3**: Execute
```bash
sspec ask prompt <path-to-py-file>
```

**Step 4**: Automatic lifecycle
After execution: user's answer appended → file converted to `.md` → `.py` deleted.

### Error Handling

If `sspec ask prompt` reports file not found:
- The ask may have already been answered. Check if `<timestamp>_<topic>.md` exists in `.sspec/asks/`, or use `sspec ask list`.
- If the `.md` file exists, read the answer from it directly.

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

### Plan Confirmation (Most Common)

```python
REASON = r"""
Change plan ready for review before starting implementation
"""

QUESTION = r"""
Here's my plan for <change-name>:

**Problem**: <one-line summary>
**Approach**: <core idea>
**Key files**: <list>
**Estimated tasks**: <count>

Proceed with this plan? Any adjustments?
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

## Long Content Handling

If long reusable design doc / research finding / other drafts need to be attached:

1. Write them in `.sspec/tmp/` as standalone files
2. Reference the file path in QUESTION
3. After user reply: move useful drafts to `change/reference/`, or discard

**Why**: Ask files should stay focused. Long content in QUESTION makes the `.md` record hard to review later.

---

## Memory Integration

Ask records serve as permanent decision documentation:

- Link completed ask `.md` files in handover.md Key Files when the decision is important
- The ask record preserves context that handover.md summaries may lose (exact user wording, full option analysis)
- Future agents can trace: handover says "chose Redis" → ask record explains the full discussion

---

## Guidelines

| Do | Don't |
|----|-------|
| Use descriptive topic name (`auth_approach`) | Use generic names (`q1`, `ask`, `question`) |
| Keep topic name to letters and underscores only | Use non-ASCII or special characters |
| Fill `REASON` with context for future reference | Leave `REASON` empty or vague |
| Ask early when uncertain | Guess and risk rework |
| Provide options when choices exist | Leave open-ended if you have candidates |
| Batch related questions in one ask | Create 3 separate asks for related decisions |
| Check project.md/spec-docs before asking | Ask for info that's already documented |
| Link important ask records in handover.md | Let ask records become disconnected from change context |
