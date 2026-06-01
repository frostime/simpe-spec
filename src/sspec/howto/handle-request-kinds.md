---
name: handle-request-kinds
desc: Decide whether a file under .sspec/requests/ is a task to act on or a backlog record to leave alone.
---

A request file under `.sspec/requests/` has two origins:

- the **user** writes one to hand the agent a task, or
- the **agent** files one as an issue / PRD / backlog note for later.

The `kind` frontmatter says which, and therefore whether to act:

| kind | Meaning | Agent behavior |
|---|---|---|
| `directive` (or missing) | A task for the agent | Assess scale → Change Lifecycle |
| `observe` | A recorded phenomenon, triaged later by a human | Read for context; do NOT create a change |
| `idea` | A memo / backlog note | Read; may use as context; do NOT create a change unless explicitly asked |

`observe` and `idea` are backlog records, not work orders — the default is to
leave them alone. Any kind MAY be linked to a change later via
`sspec request link`.
