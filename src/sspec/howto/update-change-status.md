---
name: update-change-status
desc: Update `<change>/spec.md` status using the change lifecycle state machine.
---

The status in `<change>/spec.md` frontmatter should be updated according to the change's progress, following the state machine below:

| From | Trigger | To |
|------|---------|-----|
| PLANNING | user approves design+plan | DOING |
| DOING | all tasks `[x]` and work is ready for user review | REVIEW |
| DOING | missing info or external blocker stops execution | BLOCKED |
| DOING | accepted scope/design change requires replanning inside the same change | PLANNING |
| REVIEW | accepted feedback needs more work in the same change | DOING |
| REVIEW | accepted redesign still belongs to the same change | PLANNING |
| REVIEW | user accepts the result | DONE |
| REVIEW | user agrees the current change is superseded by a replacement change | BLOCKED |

**FORBIDDEN**: PLANNING->DONE, DOING->DONE - never skip REVIEW.

## Notes

- Use `BLOCKED` when the current change cannot continue as-is: a hard blocker exists, or the user agrees the change should be replaced by a new direction.
- Do **not** use `BLOCKED` for ordinary follow-up work. If the current change still stands on its own and the user wants more afterward, finish it normally and create a new follow-up change.
- Any split into a follow-up or replacement change is a direction decision and must be approved through `@align` before you create the new change.
