---
name: write-handover
desc: Route to the focused HOWTO for the exact handover job you need.
---

Use this as the entry point, not as the full rulebook.

- Need to write a new `Session Log` batch? -> `sspec howto write-handover-log`
- Need to add or update `Durable Memory`? -> `sspec howto write-handover-memory`
- Need to clean up stale/invalid durable memory? -> `sspec howto handle-obsolete-memory`
- Need a final quality pass after editing? -> `sspec howto handover-checklist`

For the full lifecycle contract (when handover is mandatory, how it interacts with `tasks.md`,
`project.md`, and spec-doc prompts), read the `sspec-handover` SKILL instead of relying on HOWTOs.
