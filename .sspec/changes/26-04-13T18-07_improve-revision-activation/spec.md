---
name: improve-revision-activation
status: REVIEW
type: ""
change-type: single
created: 2026-04-13T18:07:00
reference: null
---

# improve-revision-activation

## Problem Statement

Review 阶段 agent 收到用户反馈后，直接修改代码和 tasks.md，未经 revision 分类就跳过了 revision 流程。根因有三：

1. **触发分类隐式**：`sspec-review` 的分类判断在 agent 头脑里完成，无强制输出步骤
2. **minor-fix 定义过宽**：边界模糊导致 amend 被错误归入 minor-fix
3. **tasks.md 模板存在语义冲突**：`Feedback Tasks` 注释写"先更新 spec.md"，与 design SKILL 的 post-gate 不可变规则直接冲突，误导 agent 跳过 revision

## Proposed Solution

### Approach

在 `sspec-review` SKILL 中引入**强制显式分类步骤**：agent 必须先输出 `@feedback-class`，再进入任何代码或文档修改。同时收紧 `minor-fix` 定义，并修正 `tasks.md` 模板冲突。

核心判定标准统一为一句话（注入进所有相关 SKILL 和 HOWTO）：

> **原 spec/design 是否还能准确预测修改后的代码？能 → minor-fix；不能 → amend → revision**

变更只涉及 template 文件，不涉及 Python 代码。

### Key Change

**Fix A: sspec-review — 强制显式 feedback 分类**
在 Review SKILL 的 Feedback Loop 入口，要求 agent 先输出 `@feedback-class` 标注，才能进入后续动作。把"隐式判断"变为"显式步骤"。

**Fix B: 统一 minor-fix 收紧定义 + 单句判定标准**
所有相关 SKILL（sspec-review / sspec-implement / handle-review-scope-change HOWTO）加入统一判定标准，并收紧 minor-fix 为：命名调整 / typo / 明显 bug / 已有验收边界内的修复。

**Fix C: 修正 tasks.md 模板语义冲突**
`Feedback Tasks` 注释把 pre-gate / post-gate 两种路径写清楚：
- pre-gate：更新 spec.md/design.md
- post-gate：**先创建 revisions/NNN-*.md，再更新 tasks.md**

**Fix D: sspec-implement — 显式标注 post-gate revision 触发**
在"Implementation reveals design issue"那一行，把 revision 提升为更显眼的强制动作，而不是附属条款。

**Fix E: 双向引用 — spec.md ↔ revision ↔ tasks.md**
- `spec.md` frontmatter `reference:` 扩展 `type: revision` 枚举，每次创建 revision 后回写一条引用条目
- `tasks.md` Feedback Tasks section header 固定格式，包含对应 revision 文件的相对链接
- `sspec-review` SKILL 和 `handle-review-scope-change` HOWTO 加入"创建 revision 后回写引用"的步骤

### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/templates/skills/sspec-review/SKILL.md` | Fix A + Fix B + Fix E：强制分类步骤 + 收紧 minor-fix + revision 回写引用步骤 |
| `src/sspec/templates/skills/sspec-implement/SKILL.md` | Fix B + Fix D：统一判定标准 + 强化 revision 触发 |
| `src/sspec/templates/change/tasks.md` | Fix C + Fix E：修正冲突注释 + Feedback Tasks header 引用格式 |
| `src/sspec/howto/handle-review-scope-change.md` | Fix B + Fix E：加入判定标准 + 回写引用步骤 |
| `src/sspec/templates/change/spec.md` | Fix E：`@RULE` 注释扩展 `type: revision` 枚举说明 |

### Design Reference

→ 详细 SKILL 改动内容见 [design.md](./design.md)
