---
name: generalize-align-interaction
status: DOING
type: "refactor"
change-type: single
created: 2026-03-17T00:57:34
reference: null
---

# generalize-align-interaction

## A. Problem Statement

### Current Situation

SSPEC 的交互层（`@align` / `sspec ask` / `@force-end-align`）是为 GitHub Copilot Agent Mode 的约束量身设计的：

- **按次计费**：Agent 结束 turn = 用户多花一次交互，所以大量机制围绕"防止 Agent 结束 turn"
- **缺乏内置 question 工具**：`sspec ask` 被迫同时承担交互和归档两个职责
- **`@force-end-align`**：纯粹为了"在 turn 结束前多问一句以保持 session alive"

这导致在非 Copilot 系统（Claude Code、OpenCode、Cursor 等）中使用 SSPEC 时：

1. `sspec ask` 的 create → edit YAML → prompt 流程需要 3-4 个 tool call，仅为了问一个问题
2. 所有 mandatory `@align` gate 都要求 Agent 停下来等用户回复，简单任务被过度流程化
3. `@force-end-align` 在非按次计费系统里是无意义的"还有什么需要帮忙的吗"
4. Agent 面对复杂的 channel 选择矩阵（question 工具 vs sspec ask vs 结束 turn），认知负担高

### Goal

将 SSPEC 的交互层从 Copilot-specific 改为 platform-agnostic，保留结构化价值，去掉"防止 Agent 结束 turn"的焦虑感。

## B. Proposed Solution

### Approach

核心思路：**保留 change lifecycle 骨架，重写交互层**。

change lifecycle（Research → Design → Plan → Implement → Review → Handover）、spec.md/tasks.md/handover.md 三件套、spec-docs、scale assessment 等骨架完全不动。只改 Agent 与用户之间的交互方式和流程强度。

### Key Design

#### Change A: @align 简化为两级

现有的 `@align` 是单一强度（mandatory = 必须停下来等回复）。改为两级：

| 级别 | Agent 行为 | 场景 |
|------|-----------|------|
| `report` | 输出摘要，**继续执行**，不等回复 | Plan 完成、进度汇报 |
| `gate` | 输出问题，**停下来等用户回复** | Design 完成、Implement 完成、不可逆操作、scope 变更、方向分歧、blocker、ambiguity |

关键规则：
- **Design 和 Implement 阶段结束时是 hard gate**，必须等用户明确确认
- Plan 完成时是 `report`，Agent 输出摘要后继续
- 其他需要用户做决策的场景也是 `gate`
- `gate` 的实现方式：有 question 工具 → 用 question 工具（同步，不结束 turn）；没有 → 在输出中提问，结束 turn
- 用户随时可以打断 Agent，不需要 Agent 主动停

#### Change B: 删除 `@force-end-align`

整个概念删除。涉及：
- `AGENTS.md` §3 中的 `@force-end-align` 段落
- `sspec-align/SKILL.md` §5
- `howto/force-end-align` 整个文件
- `sspec-align/SKILL.md` §1 表格中 `@force-end-align` 相关行

#### Change C: `sspec ask` 退出主流程

`sspec ask` 不再出现在 AGENTS.md、SKILL、HOWTO 的推荐主流程中。交互职责完全交给平台原生能力（question 工具或对话）。

**本轮实现范围**：先把模板协议和 HOWTO/提示文案去耦合；现有 `sspec ask` CLI 代码暂时保留原位置，不做兼容迁移。

具体改动：
- `AGENTS.md` §3 重写：删除 channel 选择矩阵，不再提及 `sspec ask`
- `sspec-align/SKILL.md` §2 (Choose the Channel) 删除，§4 (Use of sspec ask) 删除
- 各 phase SKILL 中引用 `sspec ask` 的地方全部移除
- CLI Quick Reference 中移除 `sspec ask` 条目

**后续可选项**：如果后面仍然需要保留 ask 能力，再单独把它迁移为 `sspec tool ask`，并处理命令兼容与文档更新。

决策记录的归宿改为已有机制：

| 决策类型 | 归档位置 |
|---------|---------|
| 设计决策 | `spec.md` Section B |
| 方向变更 | `handover.md` Durable Memory |
| Scope 变更 | `spec.md` frontmatter + `handover.md` |
| 用户反馈 | `handover.md` Session Log |

#### Change D: 强化 Micro 路径

现有 micro 路径只有一行"Do directly, no change needed"。加强描述，给 Agent 明确的跳过许可：

```
Micro task (≤3 files, ≤30min, obvious):
  Skip the entire change workflow. No spec.md, no tasks.md, no @align gates.
  Just do the work. Optionally update handover.md if the session has one.
```

#### Change E: 删除 Copilot-specific HOWTO

以下 HOWTO 直接删除：
- `force-end-align` — 随 Change B 删除
- `use-sspec-ask` — 随 Change C，sspec ask 不再是主流程
- `write-sspec-ask` — 同上

### Review Amendments

- `question`-like 工具默认只承载短问题本身；复杂上下文、汇总、参考路径应先通过普通输出呈现，再附上清晰的短 question，避免把长上下文塞进工具参数。
- `sspec ask` 不能只停留在“退出主流程”的语义；需要恢复为 `sspec tool ask` 的 fallback 能力，并在 `--prompt` 参数的帮助信息/文档里明确用法。

### Scope Summary

| File / Area | Change |
|-------------|--------|
| `src/sspec/templates/AGENTS.md` | 重写 §3 Alignment（两级 report/gate）；删除 `@force-end-align`；移除 sspec ask 引用；强化 micro 路径；CLI Quick Reference 移除 ask |
| `src/sspec/templates/skills/sspec-align/SKILL.md` | 重写为两级 @align；删除 §2 Channel 选择、§4 sspec ask 用法、§5 force-end-align |
| `src/sspec/templates/skills/sspec-design/SKILL.md` | exit 段保持 gate（用户确认设计），移除 sspec ask 引用 |
| `src/sspec/templates/skills/sspec-plan/SKILL.md` | exit 段从 mandatory gate 改为 report |
| `src/sspec/templates/skills/sspec-implement/SKILL.md` | exit 段保持 gate（用户 review），移除 sspec ask 引用 |
| `src/sspec/templates/skills/sspec-review/SKILL.md` | 移除 sspec ask 引用 |
| `src/sspec/templates/skills/sspec-research/SKILL.md` | 移除 sspec ask 引用 |
| `src/sspec/templates/skills/sspec-handover/SKILL.md` | 移除 sspec ask 引用 |
| HOWTO `force-end-align` | 删除 |
| HOWTO `use-sspec-ask` | 删除 |
| HOWTO `write-sspec-ask` | 删除 |
| `src/sspec/howto/use-sspec-cli.md` | 移除 howto 中的 `sspec ask` 示例 |
| `src/sspec/commands/change.py` | 移除 change 创建成功后的旧 `sspec ask` 提示文案 |
| `src/sspec/commands/tool.py` / `src/sspec/builtin_tools/` | 增加 `sspec tool ask` 入口与 `--prompt` 使用说明 |

### 不改的部分

- Change lifecycle（Research → Design → Plan → Implement → Review → Handover）
- spec.md / tasks.md / handover.md 三件套结构和模板
- spec-docs 系统
- Scale assessment 逻辑（micro/single/multi）
- `sspec ask` CLI 代码本身（本轮保留，不迁移；后续可单独处理）
- Handover 机制（保留，仍然 mandatory at session end）
- Design / Implement 的 hard gate 性质（保留，只是实现方式从 sspec ask 改为 question 工具/对话）
