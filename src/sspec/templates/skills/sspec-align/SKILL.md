---
name: sspec-align
description: "Agent-user alignment via persistent Q&A. USE ACTIVELY — guessing wastes more tokens than aligning."
metadata:
  author: frostime
  version: 9.1.0
---

# SSPEC Align

Before continuing execution, eliminate critical uncertainty and obtain explicit user confirmation.

**Core principle**: `@align` is not "asking a question" — it is **stopping before wrong action**.

---

## 1. When To Align

| Strength | Situation |
|---|---|
| **Mandatory** | Design gate |
| **Mandatory** | Implement complete / review request |
| **Mandatory** | Blocker, wrong assumption, rejected tool call |
| **Mandatory** | Scope or direction change |
| **Mandatory** | Irreversible action |
| **Optional** | Straightforward plan confirmation |
| **Optional** | Minor preference or low-risk mode switch |
| **Optional/Mandatory** | Session-end acknowledgement after all mandatory gates cleared; Mandatory if @force-end-align specified |
| **Optional** | Spec-doc follow-up |

**Rule**: If unsure whether to align -> align. 30 seconds now beats a rework cycle later.

---

## 2. Choose the Channel

- No built-in `question` tool -> use `sspec ask`
- Built-in `question` tool available -> choose by persistence

| Situation | Tool |
|---|---|
| Design approval, implement review, blocker resolution, anything future agents may need to trace | `sspec ask` |
| Quick yes/no, light preference, temporary confirmation | `question` tool |

**Plan rule**: Treat plan confirmation as lightweight by default. Upgrade it to `sspec ask` only when the plan introduces meaningful tradeoffs, scope changes, or decisions worth tracing later.

**Do not use "session end" as the deciding factor.** If the final question is really design approval or review sign-off, it still needs `sspec ask`.

---

## 3. After Align — Update Records

Alignment without record = information lost on next session.

| What changed | Where to record |
|---|---|
| Design confirmed/revised | `spec.md` B |
| Plan confirmed/revised | `tasks.md` |
| Direction changed, key decision made | `handover.md` Decisions |
| User feedback received | `handover.md` Session Log (new `user-feedback` entry) |
| Needs standalone Q&A record | `.sspec/asks/` via `sspec ask` |

---

## 4. Phase Gate Patterns

These are structure guides for `sspec ask`, not literal presets. For built-in `question` tools, ask the same decision in plain language and keep it short.

### `sspec ask` skeleton

```yaml
reason: |
  <why alignment is needed now>
question: |
  <change-name>:
  **Context**: <problem / state>
  **Decision**: <what user needs to approve>
  **See**: <file path if needed>

  <explicit ask>
```

### What to include by phase

- **Design**: Problem, Approach, key design decisions, Scope, `spec.md`
- **Plan**: Phases, total tasks, key files, verification, `tasks.md`; default to `question` unless durable approval is needed
- **Implement review**: What was done, tasks completed, what to review
- **Blocker / wrong assumption**: Briefly state `design says X, found Y`, then ask for direction
- **Mid-research clarification**: Present interpretation A/B and ask which is correct

---

## 5. `@force-end-align`

If a task explicitly requests `@force-end-align`, treat it as a high-priority end-of-turn instruction.

Meaning: when you believe the work is done and would normally stop, do one last user-facing alignment instead of silently ending the turn. Prefer the built-in `question` tool. Use `sspec ask` only if that final check also needs durable record, approval, or sign-off.

This is especially useful in credit-based hosts (for example Copilot): one last question can keep the productive session alive and save the user another paid round.

---

## 6. `sspec ask` Workflow

From the agent's perspective, treat this as **one atomic work unit**: `create` -> edit -> `prompt`.

- It prevents half-finished ask files from being left behind
- In hosts that gate `sspec ask prompt` for approval, the approval pause gives the user time to prepare the answer
- It preserves the real interaction boundary: the user responds at `prompt`, not at `create`

```bash
sspec ask create <topic>          # Create .yml template
# → Edit file: fill reason + question fields
sspec ask prompt <path-to-yml>    # User answers → converts to .md record
sspec ask list                    # Show pending/completed asks
```

Default posture: do all three steps in one flow unless you are intentionally stopping to let another agent or the user refine the draft file first.

**Content rules**:
- Keep the `question` field focused on the actual question
- Long analysis/drafts → write to `.sspec/tmp/<topic>.md`, reference path in question
- Batch related questions in one ask, don't create separate asks per item

Adapt the wording to the decision; keep the create/edit/prompt flow intact.

```yaml
# Anti-pattern: 200 lines of analysis stuffed into question field
# Correct:
reason: |
  Architecture decision needed
question: |
  See draft at .sspec/tmp/design-draft.md.

  **Option A**: <brief>
  **Option B**: <brief>

  Which approach?
```

