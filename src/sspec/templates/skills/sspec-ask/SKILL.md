---
skill: sspec-ask
version: 3.0.0
description: Mid-execution user consultation with file-based Q&A workflow. USE ACTIVELY to reduce errors and align with user intent.
---

# SSPEC Ask Skill

**USE THIS SKILL ACTIVELY** - Don't hesitate to ask when uncertain. Better to confirm than guess.

---

## When to Trigger (Critical Decision Points)

**REQUIRED use cases** - Agent MUST use sspec ask when:

1. **User explicitly requested** - User mentions ask/confirmation in their request
2. **Information missing** - Cannot proceed reliably without user clarification
   - Example: User mentions ambiguous terms without context → Ask for specific meaning
3. **Directional choice needed** - Multiple valid approaches exist (not minor tweaks)
   - Example: Component refactor could use multiple architecture styles → Ask for user preference
4. **Work completion check** - Agent believes task is done
   - Example: Code changes completed → Ask user to verify satisfaction before ending turn
5. **Repeated failures** - Multiple attempts failed, need user insight
   - Example: CLI command fails 3+ times → Ask user for environment details

**Why active use matters**: Reduces guessing, prevents directional errors, saves tokens by avoiding rework, ensures alignment with user intent.

---

## Workflow Overview

**Two-step process**:
1. **Create template**: `sspec ask create [--name <name>]` → generates `.py` file
2. **Execute prompt**: Edit template → `sspec ask prompt <path>` → prompts user and creates `.md` record

**Why file-based?** Eliminates shell escaping, encoding issues, and multi-line fragility.

---

## Command Syntax

### Step 1: Create Template

```bash
sspec ask create [--name <name>]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--name` | "ask" | Ask identifier (lowercase letters and underscores only) |

**Output**: Creates `.sspec/asks/<timestamp>_<name>.py` with template:

```python
CREATED = "<iso_timestamp>"

REASON = r"""
Ask user for <brief_reason>
"""

QUESTION = r"""
<YOUR_QUESTION_HERE>
"""

# AGENT SHOULD NOT EDIT THIS!
# User can pre-fill answer here to skip terminal input.
USER_ANSWER = r""""""
```

### Step 2: Edit Template

Agent edits the .py file:
- Fill in `REASON` (why asking)
- Fill in `QUESTION` (what to ask)
- Do NOT edit `USER_ANSWER` (user may pre-fill it)

### Step 3: Execute Prompt

```bash
sspec ask prompt <path_to_py_file>
```

**Behavior**:
- If `USER_ANSWER` has content → use it directly (no terminal prompt)
- If `USER_ANSWER` empty → prompt user interactively in terminal
- Appends answer to `.py` file
- Converts to `.md` format and deletes `.py`

---

## Example: Directional Choice

```bash
# Step 1: Create template
sspec ask create --name refactor_approach
```

Agent edits `.sspec/asks/260204120000_refactor_approach.py`:
```python
REASON = r"""
Multiple valid refactoring strategies exist for caching layer
"""

QUESTION = r"""
I've identified 3 approaches to refactor the caching layer:

**Option A: Redis + In-Memory Fallback**
Pros: High performance, resilient
Cons: Operational complexity, external dependency

**Option B: Pure In-Memory (with LRU eviction)**
Pros: Simple, no external deps
Cons: Lost on restart, limited by RAM

**Option C: SQLite Cache**
Pros: Persistent, zero-config
Cons: Slower than Redis, disk I/O

Which approach aligns with project priorities?
(Consider: performance, simplicity, persistence needs)
"""

USER_ANSWER = r""""""  # Empty - will prompt user
```

```bash
# Step 3: Execute and get user's choice
sspec ask prompt .sspec/asks/260204120000_refactor_approach.py
```

User responds in terminal or can pre-fill `USER_ANSWER` in the file before execution.

---

## Guidelines

| Do | Don't |
|----|-------|
| Use descriptive `--name` (e.g., `api_design`) | Use generic names (`question1`) |
| Fill `REASON` for future context | Leave `REASON` empty |
| Ask one focused question | Bundle multiple unrelated questions |
| Ask early when uncertain | Guess and risk wrong direction |

---

## File Lifecycle

```
1. create  → .sspec/asks/<timestamp>_<name>.py     (template)
2. edit    → Agent fills REASON + QUESTION
3. prompt  → Executes, collects answer
           → Appends ANSWER to .py
           → Converts to .md
           → Deletes .py
4. final   → .sspec/asks/<timestamp>_<name>.md     (persistent record)
```

---

## Final Record Format

```markdown
---
created: '<iso_timestamp>'
name: <name>
why: <reason>
---

# Ask: <name>

## Question
<question_text>

## Answer
<answer_text>
```

