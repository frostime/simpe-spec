---
name: use-sspec-cli
desc: Use the common `sspec` CLI commands intentionally instead of guessing the workflow.
---

If syntax is uncertain, use `sspec --help` or `sspec <command> --help`, then choose the shortest command that matches the job.

**Frequent commands**

| Command | Use |
|---------|-----|
| `sspec change new <name>` | Create a change |
| `sspec change new <name> --root` | Create a root change |
| `sspec change new --from <path>` | Create change from request file |
| `sspec change list` / `sspec change find <name>` | Locate active changes |
| `sspec change archive [<name>]` | Archive one change or open the selector |
| `sspec request list` | List request records |
| `sspec doc new "<name>"` | Create spec-doc |
| `sspec tool mdtoc <file>` | Pre-scan Markdown |
| `sspec tool now [--date|--utc|--json]` | Get reliable current time |

