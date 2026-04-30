# Memory: {{CHANGE_NAME}}

**Updated**: <!-- ISO timestamp, minute precision -->

## Git Baseline (Immutable)
<!-- Captured during `sspec change new` before any change files are written.
This section records the change starting point in git and MUST NOT be edited or refreshed later. -->

{{GIT}}

## State
<!-- 当前在哪、下一步做什么 — 一到三行
这是恢复入口；Agent 冷启动时第一个读的 section。 -->

<!-- @REPLACE:STATE -->


## Key Files
<!-- 对理解/继续这个 change 至关重要的文件
- `path/file` — what it contains, why it matters -->

<!-- @REPLACE:KEY_FILES -->


## Knowledge
<!-- @RULE: Write-gate is "If this item were lost, would the next agent make a wrong decision?"
Yes → write it. No → skip.

Target reader: a cold-starting agent that can only see spec + design + tasks + this Knowledge.
Exclude: anything already covered by spec/design/tasks (no restating).
Include: rejected approaches with reasons, implicit constraints, user preferences, API/env traps, insights that shaped design choices.

Format: - [timestamp] [Type] content
Types: Decision | Constraint | Gotcha | Rejected | Insight
  Decision  = directional choice made (with rationale)
  Constraint = hard limit imposed externally or by user
  Gotcha     = trap invisible without reading code/docs
  Rejected   = approach considered and discarded (with why — prevents successor from re-trying)
  Insight    = finding that shaped understanding but is not itself a decision

Project-level discoveries → ALSO append to project.md Notes.
Obsolete items → mark [obsolete: timestamp], never silently delete. -->

<!-- @REPLACE:KNOWLEDGE -->


## Milestones
<!-- @RULE: 每 session 一行，纯事实记录；新记录直接追加
CLI 会把最后一条有效 bullet 视为 latest milestone
- [ISO timestamp] 一句话概要 -->

<!-- @REPLACE:MILESTONE -->