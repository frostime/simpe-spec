---
name: update-change-status
desc: Use `sspec tool mdtoc` before reading long markdown files.
---

The status in `<change>/spec.md` frontmatter should be updated according to the change's progress, following the state machine below:

| From | Trigger | To |
|------|---------|-----|
| PLANNING | user approves design+plan | DOING |
| DOING | all tasks `[x]` | REVIEW |
| DOING | missing info | BLOCKED |
| DOING | scope changed | PLANNING |
| REVIEW | accepted | DONE |
| REVIEW | needs changes | DOING |

**FORBIDDEN**: PLANNING→DONE, DOING→DONE — never skip REVIEW.
