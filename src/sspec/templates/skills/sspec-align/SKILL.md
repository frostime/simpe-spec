---
name: sspec-align
description: "Agent-user alignment via persistent Q&A. USE ACTIVELY — guessing wastes more tokens than aligning."
metadata:
  author: frostime
  version: 9.2.0
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

## 4. Use of sspec ask

Treat `sspec ask` as one atomic flow:

1. `sspec ask create <topic>`
2. Fill `reason`
3. Fill `question`
4. `sspec ask prompt <path>`

Do not stop halfway unless you intentionally want to leave a draft for later refinement.

**Minimum content**:
- `reason`: why alignment is needed now, and what risk exists if you proceed without it
- `question`: current state, decision needed, and the exact ask to the user
- long analysis: write it to `.sspec/tmp/` and link it instead of pasting everything into the ask body

Minimal skeleton:

```yaml
reason: |
  <why alignment is needed now>
question: |
  <current state>
  <decision needed>
  See: <path if useful>

  <explicit ask>
```

For the exact CLI procedure, read: `sspec howto use-sspec-ask`
For a tighter writing template, read: `sspec howto write-sspec-ask`

---

## 5. `@force-end-align`

If a task explicitly requests `@force-end-align`, treat it as a high-priority end-of-turn instruction.

Meaning: when you believe the work is done and would normally stop, do one last user-facing alignment instead of silently ending the turn. Prefer the built-in `question` tool. Use `sspec ask` only if that final check also needs durable record, approval, or sign-off.
📚 `sspec howto force-end-align`

