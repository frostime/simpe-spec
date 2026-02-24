---
name: sspec-review
description: "User acceptance and feedback loop. Handle argue-improve cycles until user is satisfied."
metadata:
  author: frostime
  version: 2.0.0
---

# SSPEC Review

Collect user feedback, iterate improvements, close the loop.

---

## When This Phase Starts

After `sspec-implement` completes and user begins reviewing:
- User tests the implementation
- User examines code changes
- User provides feedback (approval, issues, or rejection)

## Feedback Loop

```
User feedback ─→ Assess scope ─→ Act ─→ @ask "Fixed. Check again?"
                                  ↑                    │
                                  └────────────────────┘
                            (repeat until user satisfied)
```

### Assess Feedback Scope

When user provides feedback or disagrees:

| Scope | Signal | Action |
|-------|--------|--------|
| **Implementation detail** | "This variable name", "Move this function", "Fix this edge case" | Fix directly, update tasks.md |
| **Design decision** | "I don't want Redis, use SQLite", "Wrong approach for this module" | Revise spec.md B → regenerate affected tasks → re-implement |
| **Requirement itself** | "Actually I don't need this feature", "The real problem is different" | Revise spec.md A, mark scope change in handover.md, return to `sspec-design` |

### Adding Feedback Tasks

When fixes require non-trivial work, add them to tasks.md:

```markdown
### Feedback Tasks 🚧
- [ ] Fix edge case in `src/auth/jwt.py` — handle expired refresh tokens
- [ ] Rename `process()` to `validate_token()` per user feedback
**Verification**: User confirms fixes are satisfactory
```

Then implement these tasks following `sspec-implement` workflow.

## Rejection Protocol

If user strongly disagrees (`@argue`):

1. **STOP immediately** — don't continue current work
2. **Assess scope** using the table above
3. **Acknowledge** the disagreement explicitly
4. **Act** based on scope:
   - Implementation: fix and continue
   - Design: return to `sspec-design`, `@ask` for new direction
   - Requirement: return to `sspec-design`, reassess from problem statement

## Close Loop

When user is satisfied:

1. Ensure all tasks (including feedback tasks) are marked `[x]`
2. Update spec.md frontmatter: `status: REVIEW → DONE`
3. If change produced architectural knowledge → `@ask` user: "Should I create/update a spec-doc for X?" (use `write-spec-doc` SKILL if yes)
4. Suggest next actions:
   - Archive the change if work is complete
   - `@handover` if session is ending

**FORBIDDEN transitions**: PLANNING→DONE, DOING→DONE — never skip REVIEW.

## Status Flow

```
DOING (implement complete) → REVIEW (user reviewing)
  → DONE (user satisfied)
  → DOING (needs more work → implement feedback tasks → REVIEW again)
  → PLANNING (requirement/design changed → back to design)
```
