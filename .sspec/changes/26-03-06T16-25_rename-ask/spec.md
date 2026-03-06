---
name: rename-ask
status: DONE
type: ''
change-type: single
created: 2026-03-06 16:25:27
reference:
- source: .sspec/requests/26-03-06T16-07_rename-ask.md
  type: request
  note: Linked from request
---
<!-- @RULE: Frontmatter
status: PLANNING | DOING | REVIEW | DONE | BLOCKED
change-type: single | sub
reference?: Array<{source, type: 'request'|'root-change'|'sub-change'|'prev-change' |'doc', note?}>

Sub-change MUST link root:
reference:
  - source: ".sspec/changes/<root-change-dir>"
    type: "root-change"
    note: "Phase <n>: <phase-name>"

Single-change common reference:
reference:
  - source: ".sspec/requests/<request-file>.md"
    type: "request"
  - source: ".sspec/changes/<change-dir>"
    type: "prev-change"
    note: "This change is a follow-up to <change-name> which introduced <feature/bug>. This change addresses <issue> with that feature/bug."
-->

# rename-ask

## A. Problem Statement

`@ask` 是 sspec 协议中的核心指令，用于指示 Agent 主动和用户对齐意图。
然而`@ask` 这个名称存在歧义：它与 `sspec ask` CLI 命令名称相近，容易让 Agent 混淆「协议指令 `@ask`」和「CLI 工具 `sspec ask`」。
同时，`sspec-ask` SKILL 与 `@ask` 指令同名，进一步加剧混乱。

`@align` 更准确地表达了该操作的核心意图——Agent 与 User 对齐想法——而非仅仅「提问」。

## B. Proposed Solution

### Approach

将协议指令从 `@ask` 重命名为 `@align`，并将 SKILL 从 `sspec-ask` 重命名为 `sspec-align`：
- `@align` = Agent 主动与 User 对齐，消除歧义
- `sspec ask` CLI 命令**保持不变**（只是 SKILL 名称变化）
- `sspec project update` 的孤儿检测机制会自动清理旧的 `sspec-ask` 目录，安装新的 `sspec-align`

### Key Design

| File | Change |
|------|--------|
| `src/sspec/templates/AGENTS.md` | `@ask` → `@align`，Section 3 重命名，SKILL 引用更新 |
| `src/sspec/templates/skills/sspec-ask/` | 目录重命名为 `sspec-align/`，SKILL.md frontmatter 更新 |
| `src/sspec/templates/skills/sspec-design/SKILL.md` | `@ask` → `@align` |
| `src/sspec/templates/skills/sspec-plan/SKILL.md` | `@ask` → `@align` |
| `src/sspec/templates/skills/sspec-implement/SKILL.md` | `@ask` → `@align` |
| `src/sspec/templates/skills/sspec-review/SKILL.md` | `@ask` → `@align` |
| `src/sspec/templates/skills/sspec-handover/SKILL.md` | `@ask` → `@align` |
| `src/sspec/templates/skills/sspec-research/SKILL.md` | `@ask` → `@align` |
| `.github/skills/sspec-ask/SKILL.md` | 目录重命名为 `sspec-align/`，内容更新 |
| `AGENTS.md` (root, SSPEC block) | 通过 `sspec project update` 自动更新 |
