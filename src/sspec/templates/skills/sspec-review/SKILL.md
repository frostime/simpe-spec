---
name: sspec-review
description: "User acceptance and feedback loop. Handle argue-improve cycles until user is satisfied."
metadata:
  author: frostime
  version: 2.1.0
---

# SSPEC Review

Collect user feedback, iterate improvements, close the loop.

---

## When This Phase Starts

After `sspec-implement` completes and user begins reviewing:
- User tests the implementation
- User examines code changes
- User provides feedback (approval, issues, or rejection)

If handover includes a `Git Baseline (Immutable)` section, use it as the review anchor:
- compare current work against that recorded branch / HEAD / status context
- prefer `git diff`, `git log`, and related history checks that explain what changed since the recorded start point

## Feedback Loop

```
User feedback ─→ Assess scope ─→ Act ─→ @align "Fixed. Check again?"
                                  ↑                    │
                                  └────────────────────┘
                            (repeat until user satisfied)
```

### Assess Feedback Scope

When user provides feedback or disagrees:

| Class | Signal | Action |
|-------|--------|--------|
| **Minor fix** | "This variable name", "Move this function", "Fix this edge case" | Keep current change; fix directly or add `Feedback Tasks` if non-trivial |
| **Current-change amend** | "This still needs extra validation", "The same feature needs one more acceptance condition" | Revise `spec.md` A/B as needed → update `tasks.md` → return to `DOING` or `PLANNING` depending on redesign impact |
| **Follow-up change** | "After this, also add export", "The original change is fine; now I want another capability" | `@align` user before opening a new change; if approved, create a new change with `prev-change` reference |
| **Supersede change** | "This whole approach is wrong", "Stop this direction and restart from a different goal" | `@align` user before marking current change `BLOCKED` and opening a replacement change |

📚 `sspec howto handle-review-scope-change`

### Using Feedback Tasks

Use `Feedback Tasks` only for execution work that still belongs to the current change.

When accepted feedback changes the design or scope of the current change, update `spec.md` first, then add or refresh the relevant tasks in `tasks.md`.

When non-trivial fixes stay in the current change, add them to tasks.md:

```markdown
### Feedback Tasks 🚧
- [ ] Fix edge case in `src/auth/jwt.py` — handle expired refresh tokens
- [ ] Rename `process()` to `validate_token()` per user feedback
**Verification**: User confirms fixes are satisfactory
```

Then implement these tasks following `sspec-implement` workflow.

Do **not** use `Feedback Tasks` as a dumping ground for work that should become a follow-up or replacement change.

### Git-Aware Review

When a change has a `Git Baseline (Immutable)` section in `handover.md`, use it as the review anchor:

📚 `sspec howto review-git-baseline`

It is recommended to use subagents to avoid potential context contamination (such as persistent blind spots or misunderstandings in the context) for independent and objective review.

Directive shortcut: `@subagent-audits`

📚 `sspec howto make-subagent-audit`

## Rejection Protocol

If user strongly disagrees (`@argue`):

1. **STOP immediately** — don't continue current work
2. **Assess scope** using the table above
3. **Acknowledge** the disagreement explicitly
4. **Act** based on scope:
   - Minor fix: fix and continue
   - Current-change amend: revise `spec.md` / `tasks.md`, then continue in the current change
   - Follow-up change: `@align` before creating a new linked change
   - Supersede change: `@align` before `BLOCKED` + replacement-change flow

## Close Loop

When user is satisfied:

1. Ensure all tasks (including feedback tasks) are marked `[x]`
2. Update spec.md frontmatter: `status: REVIEW → DONE`
3. If change produced architectural knowledge → `@align` user: "Should I create/update a spec-doc for X?" (use `write-spec-doc` SKILL if yes)
4. Suggest next actions:
   - Archive the change if work is complete
   - `@handover` if session is ending

**FORBIDDEN transitions**: PLANNING→DONE, DOING→DONE — never skip REVIEW.

## Status Flow

```
DOING (implement complete) → REVIEW (user reviewing)
  → DONE (user satisfied)
  → DOING (needs more work in the same change → implement feedback tasks → REVIEW again)
  → PLANNING (accepted redesign inside the same change → back to design/plan)
  → BLOCKED (user chooses replacement change or an external blocker stops the current change)
```
