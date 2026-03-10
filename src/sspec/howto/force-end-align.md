---
name: force-end-align
desc: Handle `@force-end-align` — do one final user-facing alignment before ending the turn.
---

`@force-end-align` is set per-task. When present and work is done, do **not** end silently.

## What to do

Perform one final user-facing alignment before ending the turn.

**Channel choice**:
- Use the built-in `question` tool by default.
- Use `sspec ask` only when the final check also requires a durable record or sign-off.

**Why it matters** (especially in credit-gated hosts like Copilot): one end-of-turn question may keep the session alive and save the user another paid interaction round.

## Guards

- If the directive is absent → skip. Do not add unsolicited end-of-turn questions.
- If a design or implement gate is still open → that gate takes precedence. Close it first, then apply `@force-end-align`.
- If the question is really design approval or review sign-off → use `sspec ask` regardless of channel default.
