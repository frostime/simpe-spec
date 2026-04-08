---
name: sspec-review
description: "User acceptance and feedback loop. Handle argue-improve cycles until user is satisfied."
metadata:
  author: frostime
  version: 3.0.0
---

# SSPEC Review

Collect user feedback, iterate improvements, close the loop.

---

## Feedback Loop

```
User feedback ─→ Assess scope ─→ Act ─→ @align "Fixed. Check again?"
                                  ↑                    │
                                  └────────────────────┘
                            (repeat until user satisfied)
```

## Assess Feedback Scope

| Class | Signal | Action |
|-------|--------|--------|
| **Minor fix** | "This variable name", "Fix this edge case" | Keep current change; fix directly or add `Feedback Tasks` if non-trivial |
| **Amend** | "This still needs extra validation" | Re-enter Clarify posture to understand the gap; if spec/design already gated → `sspec change scaffold revision <change> --title "..."` first; update tasks.md; return to DOING |
| **Follow-up** | "After this, also add export" | `@align` user before opening a new change with `prev-change` reference |
| **Supersede** | "This whole approach is wrong" | `@align` user before marking current change `BLOCKED` and opening a replacement |

📚 `sspec howto handle-review-scope-change`

### Feedback Tasks

Use `Feedback Tasks` only for work that still belongs to the current change. Do **not** use it as a dumping ground for follow-up or replacement work.

### Rejection Protocol (@argue)

1. **Stop immediately** — do not continue current work
2. **Assess scope** using the table above
3. **Acknowledge** the disagreement explicitly
4. **Act** based on classification

### Git-Aware Review

When `handover.md` has a `Git Baseline (Immutable)` section, use it as the review anchor.

📚 `sspec howto review-git-baseline`

For independent review, consider subagent audits to avoid context blind spots.

📚 `sspec howto make-subagent-audit` | Directive: `@subagent-audits`

## Close Loop

When user is satisfied:
1. Ensure all tasks marked `[x]`; update status: `REVIEW → DONE`
2. If change produced architectural knowledge → `@align` user about creating/updating a spec-doc
3. Suggest archive or `@handover`

## Status Flow

```
DOING (implement complete) → REVIEW (user reviewing)
  → DONE (user satisfied)
  → DOING (needs more work → implement feedback tasks → REVIEW again)
  → PLANNING (accepted redesign → back to design/plan)
  → BLOCKED (user chooses replacement or external blocker)
```

**FORBIDDEN**: PLANNING→DONE, DOING→DONE — never skip REVIEW.
