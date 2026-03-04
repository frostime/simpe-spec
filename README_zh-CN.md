# sspec

[English](README.md)

**S**spec **S**ynthesizes **P**rograms from **E**xplicit **C**ontext.

sspec 是一个面向 AI 辅助开发的文档驱动工作流。它把规划、决策与交接写入仓库文件，让 Agent 可以跨会话延续工作，而不是每次从零开始。

## sspec 解决什么问题

AI 编程在连续性上常见三类问题：

- 长会话（尤其跨会话）后，上下文与关键决策容易丢失；
- Agent 在“vibe coding”式的狂飙中不断改动，开发者很难掌控它在做什么；
- 人工反复解释项目背景与约束，成本高。

sspec 的做法是：把工作状态放进 `.sspec/`，用 `AGENTS.md` + `.sspec/skills/`
把工作流和阶段规范固定下来，让 Agent 按流程推进。

## sspec 适合谁（也不适合谁）

sspec 是一个轻量、文件化的 Agent 协作工作流，目标是帮助你“控制 Agent”，而不是被 Agent 牵着走。

sspec 适合：

- 较为独立的开发者或小团队
- 希望 Agent 辅助开发而不是替你做决策
- 对可恢复性、可追踪性有要求（长会话、跨会话）
- 有能力写好 request 需求入口（上下文/约束/成功标准）

sspec 不适合：

- 随便玩玩、只想一句话就让 Agent 生成 App 的用法
- 不愿意写/维护 request、tasks、handover 的用法

sspec 特别适合从 1 到 N 的项目：你可以把它增量引入到已有项目中，只在需要的时候用。

sspec 不依赖平台特定的 slash prompt / slash command 机制。它的核心契约是文件：
`AGENTS.md` + `.sspec/` 目录（Agent 读写这些文件即可）。

## 核心概念与目录结构

`sspec project init` 会创建最小目录结构：

```text
project/
├── AGENTS.md
└── .sspec/
    ├── project.md
    ├── requests/
    ├── changes/
    ├── asks/
    ├── skills/
    ├── spec-docs/
    └── tmp/
```

核心概念：

- `request`：由开发者写的入口（上下文/约束/成功标准），位于 `.sspec/requests/`。
- `change`：一个被追踪的工作单元，位于 `.sspec/changes/<id>/`。
- `spec.md`：该 change 的问题定义与方案。
- `tasks.md`：可执行任务清单与进度（完成即更新）。
- `handover.md`：会话记忆与下一步（用于跨会话恢复）。
- 问答记录（`ask`）：当 Agent 需要关键决策或缺失信息时的问答记录，位于 `.sspec/asks/`（通过 `sspec ask` 创建）。

注：`sspec ask` 用于把关键问题与答案落盘，避免只存在于聊天记录里。

Skills（技能）：

- `.sspec/skills/` 是技能的“中心副本”（hub）。
- sspec 会把技能以 link/sync 的方式分发到不同宿主需要的位置（spoke），比如
  `.claude/`、`.github/`、`.agents/`，从而让同一套技能在不同 Agent 工具里复用。

## 设计原则

- **Request-first**：从 request 文件开始，而不是从聊天记录开始。
- **显式上下文**：尽早写清约束，并链接相关文件。
- **可追踪执行**：任务完成即更新 tasks。
- **人工关卡**：关键决策必须停下来向人确认。
- **可恢复性**：`handover.md` 是必须项，不是装饰。
- **开发者主导**：方向与范围由开发者掌控。

## 最小示例

1) 创建 request：

```bash
sspec request new add-password-reset
```

2) 在 request 里写清上下文与约束（示例结构）：

```markdown
# Request: add-password-reset

## Background
当前仅支持邮箱+密码登录。

## Problem
用户忘记密码后无法重置。

## Initial Direction
- 使用邮箱重置 token（限时、一次性）
- 不引入新的外部服务

## Success Criteria
- 用户可触发重置邮件
- token 过期且不可重复使用
- 有测试覆盖核心流程

## Relational Context
- 相关代码：`src/auth/*`
- 现有邮件：`src/notifications/email/*`
```

3) 交给 Agent 执行：

```text
请基于 sspec 规范完成这个 request：
.sspec/requests/<your-request-file>.md

请遵循 `AGENTS.md` 和已安装的 skills，保持 `spec.md` / `tasks.md` / `handover.md` 持续更新。
遇到关键决策先停下来问我确认。
```

Agent 会读取 request，产出 `spec.md` + `tasks.md`，并持续维护 `handover.md`，方便后续恢复。

## 快速开始

如果你是配合编码 Agent 使用，通常需要你手动运行的命令只有：

```bash
sspec project init
sspec request new <name>
sspec change archive --with-request [name]
```

### 1) 安装

```bash
pip install sspec
# 或
uv tool install sspec
```

### 2) 在项目中初始化

```bash
cd your-project
sspec project init
```

初始化后先补全 `.sspec/project.md`：技术栈、约定、关键路径。

### 3) 创建请求

```bash
sspec request new add-password-reset
```

在 `.sspec/requests/...` 中写清上下文、约束、成功标准。

然后在对话里直接粘贴 request 文件路径（`sspec request new` 会输出），并要求 Agent
遵循 `AGENTS.md`。

完成后可以用下面的命令归档 change，并一并归档关联的 request：

```bash
sspec change archive --with-request
```

提示：`sspec request new` 可以自动用编辑器打开新建文件（见下文）。

## 编辑器集成

创建 request 时，sspec 会尝试用你的编辑器打开该文件。

查找顺序：

1) 当前工作目录下的 `.env`：`SSPEC_EDITOR`
2) 环境变量：`SSPEC_EDITOR`
3) 环境变量：`EDITOR`

编辑器命令可以包含 `{file}`（会替换为新建文件路径）。

VS Code 示例：

```bash
SSPEC_EDITOR='code {file}'
```

## 生命周期

每个阶段都有对应 SKILL（位于 `.sspec/skills/`）。

```text
[Request] -> [Research] -> [Design] -> [Plan] -> [Implement] -> [Review] -> [Handover]
                (decision checkpoints)   (feedback loop)
```

核心规则：

- `Research` 重点是理解问题空间和代码上下文。
- `Design` 与 `Implement` 包含强制的关键决策确认。
- `Plan` 采用轻量确认。
- `Implement` 与 `Review` 构成反馈闭环，直到用户满意。
- `Handover` 不是收尾装饰，而是生命周期中的正式阶段。

## 人与 Agent 的分工

**人工负责**

- 创建请求；
- 回答关键决策问题（必要时沉淀为问答记录）；
- 批准设计与 Review 结果。

**Agent 负责**

- 评估规模（micro/single/multi-change）；
- 创建并维护变更文件；
- 持续更新任务和交接；
- 驱动反馈闭环直到验收通过，并在需要时记录问题/决策。

## CLI 参考

### Project

```bash
sspec project init
sspec project status
sspec project update --dry-run
```

### Request

```bash
sspec request new <name>
sspec request list
sspec request show <name>
sspec request find <query>
sspec request link <request> <change>
sspec request archive [name] --with-change
```

### Change

```bash
sspec change new <name>
sspec change new --from <request>
sspec change new <name> --root
sspec change list --all
sspec change find <query>
sspec change validate <name>
sspec change archive [name] --with-request
```

### 问答记录（`ask`）

```bash
sspec ask create <topic>
sspec ask prompt <ask-file>
sspec ask list --all
sspec ask archive [name]
```

### 规范文档

```bash
sspec doc list
sspec doc new "<name>"
sspec doc new "<name>" --dir
```

### 可选工具

```bash
sspec skill list
sspec skill new <name>
sspec cmd add
sspec cmd list
sspec cmd run <name>
sspec tmp new <name>
sspec tool mdtoc <file>
sspec tool view-tree
sspec tool pack-zip --dry-run
sspec tool patch --prompt
```

## 兼容性

sspec 适合能完成以下能力的 Agent 环境：

- 可读写本地仓库文件；
- 能遵循 `AGENTS.md` 指令；
- 可执行本地 CLI 命令；
- 能加载并遵循 skills。

## License

AGPL-V3.0
