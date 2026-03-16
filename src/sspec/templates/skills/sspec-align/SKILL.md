---
name: sspec-align
description: "Agent-user alignment via persistent Q&A. USE ACTIVELY — guessing wastes more tokens than aligning."
metadata:
  author: frostime
  version: 9.2.0
---

# SSPEC Align

Before continuing execution, choose whether the current moment only needs a summary or truly needs a user decision.

**Core principle**: `@align` is not automatically a hard stop. Use a hard stop only when the user must decide something before safe progress can continue.

---

## 1. Levels

| Level | Agent behavior | Typical situations |
|---|---|---|
| `report` | Summarize current state and continue execution | Plan done, progress update, low-risk confirmation, lightweight preference |
| `gate` | Present the decision or review target, then stop and wait for user response | Design gate, implement complete / review request, blocker, wrong assumption, rejected tool call, scope or direction change, irreversible action, split / replace current change |

**Rule**: If safe progress depends on a user decision, use `gate`. Otherwise prefer `report`.

---

## 2. How To Gate

- If a built-in `question`-like tool is available, first present the context in normal output, then use the tool only for the concise question itself.
- Otherwise, state the question clearly in normal output and end the turn.

For large context, write analysis to `.sspec/tmp/` and link it instead of pasting everything inline.

**Question-tool rule**: do not stuff long context, tradeoff tables, or multi-paragraph analysis into the `question` tool payload. Show the summary first; let the tool carry only the decision prompt.

---

## 3. After Align — Update Records

Alignment without record = information lost on next session.

| What changed | Where to record |
|---|---|
| Design confirmed/revised | `spec.md` B |
| Plan confirmed/revised | `tasks.md` |
| Direction changed, key decision made | `handover.md` Durable Memory |
| User feedback received | `handover.md` Session Log (new `user-feedback` entry) |

**No separate ask record is required.** Put the decision in its natural home.

---

## 4. Message Shape

### `report`

Keep it short:
- what just completed
- what happens next
- any risk or assumption worth surfacing

### `gate`

Make the stop explicit:
- current state
- decision / review needed
- what changes based on the answer
- link to `spec.md`, `tasks.md`, or `.sspec/tmp/...` if useful

When a `question` tool is available, the normal output carries the context and the tool carries the final short ask.

