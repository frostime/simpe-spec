# sspec

[English](README.md)

> **S**spec **S**ynthesizes **P**rograms from **E**xplicit **C**ontext.

## sspec 是什么

sspec 是一套给编码 Agent 使用的文档驱动协作工作流。

它把任务入口、设计、任务清单和交接记录保存在仓库里，而不是只留在聊天记录中。聊天用来推进工作，仓库文件用来保存长期状态。你负责目标、约束和关键决策；Agent 负责执行工作，并持续更新这些文件，让任务可以跨会话继续。

## sspec 解决什么问题

如果只靠聊天推进 AI 编程，常见问题有：

- 会话一长，尤其跨会话之后，上下文和关键决策容易丢失；
- Agent 持续改动代码，但开发者很难快速看清它为什么这么做、已经做到哪里；
- 项目背景、约定和限制要一遍又一遍重复解释；
- 复杂任务容易在聊天里不断膨胀，最后变成一个难以追踪的大变更。

sspec 会把长期工作状态明确写进仓库：

- `AGENTS.md` 定义协作协议；
- `.sspec/project.md` 记录项目身份、技术栈、关键路径和约定；
- `.sspec/requests/` 保存任务入口；
- `.sspec/changes/` 保存每次变更的规格、任务和交接；
- `.sspec/asks/` 保存关键问题与答案。

继续工作时，Agent 读取的是仓库里的显式上下文，而不是从上一段聊天里重建状态。

## 这套方法对使用者的要求

sspec 的使用前提是：开发者负责定义需求和审查结果，Agent 负责调研、设计、实现和文档更新。

使用它通常要求：

- 能把需求写成清晰的 `request`；
- 能在设计对齐和实现审查时给出明确反馈；
- 具备基本开发能力，能判断实现是否正确，并指出 Agent 的错误。

所以，sspec 更适合希望自己驾驭 Agent、而不是被 Agent 牵着走的开发者。对于完全没有编程能力、也不打算审查代码的人，它通常不是一个合适的起点。

## 核心概念与目录

理解两个核心概念：`request` 和 `change`。

- `request`：由开发者写的任务入口。它说明背景、约束、方向和成功标准，是整个工作流的起点。
- `change`：一次内聚、原子化、可追踪的变更提案。一个 `change` 应保持在可审阅、可跟踪的范围内。

围绕一个 `change`，最重要的三份文件是：

- `spec.md`：这次变更准备怎么做，以及为什么这样做；
- `tasks.md`：执行事项和当前进度；
- `handover.md`：会话状态、关键发现和下次继续所需的信息。

如果工作超出单个 `change` 的可追踪范围，应改为：

- 用 `root-change` 协调多个 `sub-change`，把复杂工作拆成几个可独立推进的部分；
- 或在已有变更之后，新建一个引用 `prev-change` 的后续 `change`，而不是把旧变更扩张成一个庞大、不可追踪的容器。

更多概念和进阶用法，见后文的“进阶说明”。

`sspec project init` 会创建最小结构：

```text
project/
├── AGENTS.md
└── .sspec/
    ├── project.md
    ├── requests/
    ├── changes/
    │   └── <ts>_<name>/
    │       ├── spec.md
    │       ├── tasks.md
    │       ├── handover.md
    │       └── reference/
    ├── asks/
    ├── skills/
    ├── spec-docs/
    └── tmp/
```

主要目录：

- `project.md`：项目身份层。写清技术栈、关键路径、约定和项目级笔记。
- `requests/`：你写的 `request` 入口文件。
- `changes/`：每次变更的文档目录；每个变更包含 `spec.md`、`tasks.md`、`handover.md`。
- `asks/`：关键问题与答案的记录，避免决策只存在于聊天里。
- `spec-docs/`：超出单次变更范围的长期架构知识。
- `skills/`：按阶段拆分的技能说明，可同步到不同 Agent 宿主需要的位置。

## 最小工作流

一次典型流程如下：

1. 你运行 `sspec project init`，然后补全 `.sspec/project.md`。
2. 你运行 `sspec request new <name>`，写好 `request`。
3. 你把 request 文件路径发给 Agent，并要求它遵循 `AGENTS.md` 工作。
4. Agent 先调研背景和代码，再给出设计与计划，并在关键节点停下来和你对齐。
5. 对齐之后，Agent 开始实现；你负责 review，并给出反馈。
6. Agent 根据反馈继续修改，直到你满意。
7. 会话结束时，Agent 会更新 `handover.md`；工作完成后，再归档这个 `change`。

这个流程包含文档更新和用户确认步骤，不依赖单次聊天上下文。

## 快速开始

### 1) 安装

```bash
pip install sspec
# 或
uv tool install sspec
```

### 2) 在项目里初始化

```bash
cd your-project
sspec project init
```

然后补全 `.sspec/project.md`，写清：

- 技术栈；
- 关键路径；
- 代码约定；
- 项目级注意事项。

### 3) 创建一个 request

```bash
sspec request new add-password-reset
```

在生成的 request 文件里写清背景、问题、方向和成功标准。一个最小示例如下：

```markdown
# Request: add-password-reset

## Background
当前仅支持邮箱加密码登录。

## Problem
用户忘记密码后无法自助重置。

## Initial Direction
- 使用邮箱重置 token
- token 必须限时且一次性
- 不引入新的外部服务

## Success Criteria
- 用户可以请求重置邮件
- token 会过期且不可重复使用
- 核心流程有测试覆盖

## Relational Context
- 相关代码：`src/auth/*`
- 现有邮件：`src/notifications/email/*`
```

### 4) 把 request 交给 Agent

可以直接在聊天里给出 request 文件路径，并要求 Agent 遵循 `AGENTS.md`：

```text
请基于这个 request 工作：
.sspec/requests/<your-request-file>.md

请遵循 `AGENTS.md` 和 `.sspec/skills/`。
为这项工作创建并维护对应的 change 文档。
遇到关键决策先停下来问我。
```

### 5) 完成后归档

确认工作完成后，归档变更及其关联 request：

```bash
sspec change archive --with-request [name]
```

## 关键规则与职责边界

**开发者负责**

- 写 `request`，把背景、约束和成功标准说清楚；
- 回答关键决策问题；
- 批准设计方向和实现结果；
- 判断是否需要拆分 `change`，避免范围失控。

**Agent 负责**

- 调研代码、背景和约束，先理解问题，再进入设计；
- 为这次工作创建并维护 `change` 文档；
- 给出方案，与用户对齐，再开始实现；
- 随执行进度更新 `tasks.md` 和 `handover.md`，并在 review 反馈后继续迭代。

**工作流规则**

- 从 `request` 开始，而不是从一段聊天历史开始；
- `Design` 和 `Implement` 阶段都包含强制确认点；
- `Handover` 不是收尾装饰，而是正式生命周期的一部分；
- 长期状态以 `change` 文档为准，而不是只以聊天记录为准。

## 常用命令

常用命令通常只有这些；更完整的列表请看 `sspec --help`。

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
sspec request archive [name] --with-change
```

### Change

```bash
sspec change new <name>
sspec change new --from <request>
sspec change new <name> --root
sspec change list --all
sspec change archive [name] --with-request
```

## 进阶说明

### `ask`：把关键问答落盘

当 Agent 需要关键决策、发现需求有歧义、或者需要把重要问题正式记录下来时，可以使用 `ask`。

常用命令：

```bash
sspec ask create <topic>
sspec ask prompt <ask-file>
sspec ask list --all
sspec ask archive [name]
```

### `spec-docs/`：保存跨变更的长期知识

`spec-docs/` 用于记录跨变更长期保留的知识，例如架构接口、数据模型、设计模式或约定。

常用命令：

```bash
sspec doc list
sspec doc new "<name>"
```

### `skills/`：`.sspec/skills/` 是源目录

sspec 在项目里安装 skills 时采用 hub-spoke 方案：

- `.sspec/skills/` 是 hub，是 SKILL 的源目录
- `.agents/skills/`、`.claude/skills/`、`.github/skills/` 等外部位置属于 spoke
- spoke 默认使用符号链接或者Junction链接引用 .sspec/skills
- `sspec project init` 和 `sspec project update` 会负责这套 hub-spoke 同步，无需用户自行更改

## 其他

### 如果你用过 openspec

sspec 和 openspec 解决的是相近的问题，但工作方式不同。

- sspec 从人写的 `request` 开始，而不是让 Agent 先生成整套前置产物。
- sspec 把长期状态保存在仓库文档里；`spec.md`、`tasks.md`、`handover.md` 是每个 `change` 的真实记录，CLI 主要负责创建和查看。
- sspec 强调关键节点的人类确认，而不是让 Agent 一路自动推进。
- sspec 以一个内聚、原子、可追踪的 `change` 作为基本工作单位。更复杂的工作应拆成 `root-change` / `sub-change`，或通过 `prev-change` 在已有变更之后继续演进，而不是把所有内容堆进一个庞大、不可追踪的变更里。

### 兼容性

sspec 依赖 Agent 环境具备以下能力：

- 可读写本地仓库文件；
- 能遵循 `AGENTS.md` 指令；
- 可执行本地命令行命令；
- 能加载并遵循 `.sspec/skills/` 中的技能说明。

## License

AGPL-V3.0
