---
name: review-feedback-sync
status: REVIEW
type: enhancement
change-type: single
created: 2026-03-10T22:06:26
reference: null
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

# review-feedback-sync

## A. Problem Statement

当前情况：

- [review 阶段常会追加 1-N 个非 trivial 任务] causing `spec.md` / `tasks.md` 只覆盖首轮设计，归档后难以准确回答「这个 change 最终交付了什么」。
- 当前规则虽然已有 `Feedback Tasks`，但对「已接受的范围变化」缺少强制同步回 `spec.md` 的约束，Agent 很容易只把新增事项写进 `handover.md`。

用户需求：

- 保留 review 阶段自然迭代，不把所有新增反馈都机械拆成新 change。
- 同时明确区分：小修小补、仍属于当前 change 验收前提的增量、更适合拆成 follow-up 的新请求，以及当前 change 已经走偏到应直接阻断并重开新 change 的情况，让归档后的 `spec.md` / `tasks.md` 继续作为可信事实源。

<!-- @RULE: Quantify impact. Format: "[metric] causing [impact]".
Simple: single paragraph. Complex: split "Current Situation" + "User Requirement". -->

## B. Proposed Solution

在 review 阶段引入明确的反馈分流规则，把新增请求分成四类：`minor-fix`、`current-change-amend`、`follow-up-change`、`supersede-change`。对用户而言主要是三种结果：留在当前 change、拆成 follow-up 新 change、或阻断当前 change 并让新 change 接管；其中凡是要拆出新 change 的动作，都必须先与用户 `@align`，Agent 不得擅自执行。

同时把这套规则写进 phase SKILL、模板注释和 `@sync` 语义：`handover.md` 继续负责解释「为什么变了 / 还剩什么」，但不再允许它成为已接受 review 变更的唯一记录载体。作为 review 阶段的常用策略，再补充一个轻量 directive：`@subagent-audits`，只负责提示 Agent 可以走独立审查流程，并引用 `sspec howto make-subagent-audit`，不在主文档里重复 HOWTO 细节。

### Approach

方案核心是补齐 review 阶段的「事实同步」闭环，而不是再引入一个新的重型流程。对于仍然属于当前 change 验收条件的反馈，Agent 必须先把范围和设计同步回 `spec.md`，再把执行项写入 `tasks.md`，然后回到实现/验证循环。

之所以不把所有 review 新增事项都强制拆成新 change，是因为这会割裂正常的 review 修正流程：很多反馈本质上仍是当前 change 成功交付的前提。相反，只有当新增请求已经形成独立目标、原 change 可以单独成立时，才要求新开 change 并通过 `prev-change` 建立追溯链路。

### Key Design

#### Interface Design

```python
from typing import Literal, TypedDict

FeedbackClass = Literal[
    "minor-fix",            # 实现细节修正，不改变已接受的问题/方案
    "current-change-amend", # 仍是当前 change 的验收前提
    "follow-up-change",     # 独立的新一轮目标，应该拆出去
    "supersede-change",     # 当前 change 已走偏，应 BLOCK 并由新 change 接管
]


class ReviewFeedbackDecision(TypedDict):
    classification: FeedbackClass
    requires_user_align: bool
    update_spec: bool
    update_tasks: bool
    create_new_change: bool
    handover_note_only: bool
```

该分类不是新增数据文件格式，而是写进 SKILL / HOWTO / 模板注释中的统一判断接口，让 Agent 在 review 和 `@sync` 时按同一套规则落盘。

#### Data Flow

```text
Review feedback
  |
  |-- minor-fix
  |   |-- keep current change
  |   |-- add/update `Feedback Tasks` when work is non-trivial
  |   `-- spec.md unchanged
  |
  |-- current-change-amend
  |   |-- keep current change
  |   |-- amend `spec.md` (inline A/B or append `### Review Amendments`)
  |   |-- add execution items under `Feedback Tasks`
  |   `-- return to DOING / PLANNING depending on impact
  |
  |-- follow-up-change
  |   |-- keep current change focused on already accepted scope
  |   |-- `@align` user before splitting
  |   |-- create new change with `prev-change` reference
  |   `-- record only the relationship / rationale in handover
  |
  `-- supersede-change
      |-- `@align` user before blocking / replacing
      |-- mark current change `BLOCKED`
      |-- create replacement change referencing blocked one
      `-- continue new direction in the replacement change
```

重点是把 `handover.md` 降回「解释和接力」角色：它记录原因、上下文、下一步，但不独占已接受范围事实。

#### Key Logic

**Rule A: Minor fix**

实现细节、命名调整、局部 edge case、不会改变问题定义或方案边界的反馈，允许只更新 `tasks.md` 的 `Feedback Tasks`（如果工作量极小，也可直接处理后补记完成状态），不要求改 `spec.md`。

**Rule B: Current-change amend**

只要新增反馈已经成为「当前 change 被接受的前提」，就必须把影响同步回 `spec.md`。默认优先直接修订 `A. Problem Statement` / `B. Proposed Solution`；如果需要保留 review 过程痕迹，可在 `B` 下追加 `### Review Amendments`，但它属于正式设计，不是旁注。

**Rule C: Follow-up change**

如果原 change 已经可以独立关闭，而用户又提出下一轮独立目标，则不再继续膨胀当前 change。此时必须先 `@align` 用户，确认要拆成 follow-up change；只有在用户明确同意后，才新开 change，并在新 change 的 `spec.md` 中记录 `prev-change` 指向当前 change。当前 change 只在 handover 中说明分流原因。

**Rule D: Supersede change**

如果 review 反馈表明当前 change 的问题定义、方案前提或方向已经整体失效，继续在原 change 上修补只会制造伪历史。此时也必须先 `@align` 用户，确认是否阻断当前 change 并重开 replacement change；未经用户确认，Agent 不得自行把 change 标记为 `BLOCKED` 或直接重开。确认后，新 change 使用 `prev-change` 指向被阻断的 change，并在 `note` 里明确这是一次 supersede，而不是普通 follow-up。

**Rule E: User gate for split / replace**

凡是会创建新 change、阻断当前 change、或改变 change 之间追溯关系的动作，都属于方向级决策，必须经过 `@align`。推荐使用可追溯的对齐记录，而不是只在普通对话里口头略过。

**Rule F: @sync contract**

`@sync` 需要从「同步 `tasks.md` / `handover.md`」升级为「按实际情况同步 `spec.md` / `tasks.md` / `handover.md`」。只要发现已接受的 review 变更仍然只存在于 handover，就视为需要补齐的文档漂移。

**Rule G: Review audit directive**

对于需要独立视角复核的 review 场景，SSPEC 应在 review 相关文档中显式暴露 `@subagent-audits` 这个 directive。它不是新的复杂流程，只是一个 point-of-need 入口：提醒 Agent 可发起 subagent 审查，并跳转到 `sspec howto make-subagent-audit` 查看具体做法。

#### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/templates/skills/sspec-review/SKILL.md` | 加入 review 反馈三分流规则、回写顺序，以及 `@subagent-audits` 指令入口 |
| `src/sspec/templates/change/tasks.md` | 明确 `Feedback Tasks` 适用边界，以及何时必须联动 `spec.md` |
| `src/sspec/templates/change/spec.md` | 明确 accepted review changes 必须并入正式设计，必要时允许 `Review Amendments` |
| `src/sspec/templates/skills/sspec-implement/SKILL.md` | 补充实现中发现范围漂移时先同步 spec/tasks 再继续 |
| `src/sspec/templates/skills/sspec-align/SKILL.md` | 明确 split / supersede change 属于必须先和用户对齐的方向级动作 |
| `src/sspec/templates/AGENTS.md` | 扩大 `@sync` 说明，并加入 `@subagent-audits` directive shortcut |
| `src/sspec/howto/update-change-status.md` | 补充 review / supersede 场景下的 `BLOCKED` 或回退状态说明 |
| `src/sspec/howto/handle-review-scope-change.md` | 提供例子驱动的判断指南，说明何时留当前 change、何时新开 change，以及何时必须先 `@align` |
