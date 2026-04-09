# sspec

[English](README.md)

> **S**spec **S**ynthesizes **P**rograms from **E**xplicit **C**ontext.

## sspec 是什么

sspec 是一套面向编码 Agent 的文档驱动工作流。

它把项目上下文、请求入口、变更规格、执行计划和 scoped memory 保存在仓库里，而不是只留在聊天记录中。聊天负责推进工作，仓库文件负责保存长期状态。

## sspec 解决什么问题

如果只靠聊天推进 AI 编程，常见问题有：

- 跨会话时上下文和关键决策容易丢失；
- 设计与实现的确认点不明确；
- 项目约定需要反复重述；
- 复杂工作容易在一条聊天线程里不断膨胀，最后难以审阅和追踪。

sspec 会把工作状态明确写进仓库：

- `AGENTS.md` 定义协作协议；
- `.sspec/project.md` 记录项目身份、技术栈、关键路径和约定；
- `.sspec/requests/` 保存请求入口；
- `.sspec/changes/` 保存每次变更的规格、任务、memory 和辅助材料；
- `.sspec/spec-docs/` 保存应当跨变更保留的架构知识；
- `.sspec/asks/` 在关键决策需要显式记录时保存结构化问答。

继续工作时，Agent 读取的是仓库中的显式上下文，而不是从上一段聊天里重建状态。

## 这套方法对使用者的要求

sspec 采用 human-led, agent-accelerated 的工作方式。

开发者需要：

- 把请求写清楚，让 Agent 有明确起点；
- 在对齐节点回答设计和范围问题；
- 审查实现结果并识别错误；
- 判断工作应该保留在一个 `change` 中，还是拆成多个 `change`。

如果你不打算审查设计、不审查代码、也不判断实现是否正确，sspec 通常不适合作为工作方式。

## 核心概念

先理解两个核心概念：`request` 和 `change`。

- `request`：由开发者编写的任务入口，描述背景、约束、方向和成功标准。
- `change`：一次内聚、可追踪的工作单元。一个 `change` 应保持在可审阅、可推理的范围内。

一个 `change` 中最核心的文件是：

- `spec.md`：问题与方案的契约；
- `tasks.md`：执行清单与进度；
- `memory.md`：当前状态、持久知识和里程碑。

一个 `change` 中可选的文件包括：

- `design.md`：当接口、数据模型或架构逻辑很重要时，用来承载详细技术设计；
- `revisions/`：design gate 之后的修订；
- `reference/`：补充说明、调研材料和辅助文件。

如果工作量超出单个 `change` 的可追踪范围，可以使用 root change 协调多个 sub-change。

## 目录结构

`sspec project init` 会创建项目脚手架：

```text
project/
├── AGENTS.md
├── .agents/               # 可选的宿主同步位置
└── .sspec/
    ├── project.md
    ├── requests/
    ├── changes/
    ├── asks/
    ├── skills/
    ├── spec-docs/
    ├── howto/
    └── tmp/
```

一个典型的变更目录如下：

```text
.sspec/changes/<ts>_<name>/
├── spec.md
├── tasks.md
├── memory.md
├── design.md        # 可选
├── revisions/       # 可选
└── reference/
```

主要目录说明：

- `project.md`：项目身份与约定；
- `requests/`：开发者编写的请求文件；
- `changes/`：每次变更的工作文档；
- `asks/`：按需记录结构化问答；
- `skills/`：面向 Agent 的技能说明，可同步到不同宿主；
- `spec-docs/`：长期保留的架构与项目知识；
- `howto/`：面向具体任务的操作指南；
- `tmp/`：临时草稿与中间材料。

## 工作流

sspec 的默认生命周期是：

```text
Clarify → Design → Plan → Implement → Review
```

各阶段职责：

- **Clarify**：结合用户意图和代码库现实，建立一致理解；
- **Design**：创建 `change`，编写 `spec.md`，必要时补充 `design.md`，然后与用户对齐；
- **Plan**：把设计拆成 `tasks.md` 中的文件级任务；
- **Implement**：执行任务、更新进度，并持续维护 `memory.md`；
- **Review**：收集反馈、迭代修改并完成闭环。

两个实用规则：

- `memory.md` 是 Agent 恢复工作的连续性文件；
- 如果已确认的范围或设计之后需要调整，就在 `revisions/NNN-*.md` 中记录，并同步更新 `tasks.md`。

## 快速开始

### 1）安装

```bash
pip install sspec
# 或
uv tool install sspec
```

### 2）在项目中初始化

```bash
cd your-project
sspec project init
```

然后补全 `.sspec/project.md`，写清：

- 技术栈；
- 关键路径；
- 编码约定；
- 项目级说明。

### 3）创建一个 request

```bash
sspec request new add-password-reset
```

在生成的 request 文件中写清背景、问题、方向和成功标准。一个最小示例：

```markdown
# Request: add-password-reset

## Background
当前仅支持邮箱加密码登录。

## Problem
用户忘记密码后无法自行重置。

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

### 4）把 request 交给 Agent

你可以直接在聊天里给出 request 文件路径，并要求 Agent 遵循 `AGENTS.md`：

```text
请基于这个 request 工作：
.sspec/requests/<your-request-file>.md

请遵循 `AGENTS.md` 和 `.sspec/skills/`。
先进入 `sspec-clarify`，然后创建并维护对应的 change 文档。
在设计和实现的 gate 停下来给我 review。
```

Agent 通常会这样创建工作中的变更：

```bash
sspec change new --from <request>
```

### 5）跟踪变更进度

可以用 CLI 查看进度和当前状态：

```bash
sspec change list
sspec change status <name>
```

如果设计需要单独的技术文档：

```bash
sspec change scaffold design <change>
```

### 6）完成后归档

工作完成后，归档变更以及其关联 request：

```bash
sspec change archive --with-request [name]
```

## 关键规则与职责边界

**开发者负责**

- 编写 `request`，把背景、约束和成功标准说清楚；
- 回答关键设计与范围问题；
- 批准设计方向与实现结果；
- 判断何时需要拆分 `change`。

**Agent 负责**

- 在进入设计前先澄清问题；
- 为这项工作创建并维护 `change` 文档；
- 提出方案，与用户对齐后再开始实现；
- 在变更进行期间持续维护 `tasks.md` 和 `memory.md`。

**工作流规则**

- 从 `request` 开始，而不是只从聊天历史开始；
- 设计和实现都要在显式 review 点停下来；
- 长期状态写入仓库文件，而不是只留在聊天中；
- 复杂工作应拆成可追踪的多个变更，而不是堆积在一条线程里。

## 常用命令

大多数用户常用的命令如下；完整列表请运行 `sspec --help`。

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
sspec request archive [name] --with-change
```

### Change

```bash
sspec change new <name>
sspec change new --from <request>
sspec change new <name> --root
sspec change new <name> --scaffold design
sspec change scaffold design <change>
sspec change scaffold revision <change> --title "scope-update"
sspec change status <name>
sspec change list --all
sspec change validate <name>
sspec change archive [name] --with-request
```

### Ask

```bash
sspec ask create <name>
sspec ask prompt <ask-file>
sspec ask list --all
sspec ask archive [name]
```

### 规范文档、HOWTO、skills 与 tools

```bash
sspec doc list
sspec doc new "<name>"
sspec howto list
sspec howto resume-change
sspec skill list
sspec tool now
sspec tool mdtoc README.md
sspec tool view-tree .
```

## 进阶说明

### Root change

当工作量大到不适合作为一个可追踪单元时，使用 root change：

```bash
sspec change new <name> --root
```

root change 负责定义整体问题和阶段拆分；文件级设计与执行放在各个 sub-change 中。

### `design.md` 与 `revisions/`

当变更涉及新接口、数据模型或架构行为时，创建 `design.md`。

如果后续需要调整已确认的设计或范围，就创建 revision 文件并同步更新计划：

```bash
sspec change scaffold revision <change> --title "<reason>"
```

### `memory.md`

`memory.md` 是变更的连续性表面，通常包含：

- `State`：当前做到哪里、下一步做什么；
- `Key Files`：继续工作时需要优先关注的非显然文件；
- `Knowledge`：持久的决策、约束和注意事项；
- `Milestones`：按会话追加的一行事实记录。

root change 还会使用 `Coordination` 汇总各个 sub-change 的状态。

### Skills 与同步布局

`.sspec/skills/` 是 skills 的源目录。`.agents/skills/` 等宿主位置由 `sspec project init` 与 `sspec project update` 从这里同步。

### Builtin tools

`sspec tool` 提供一组适合 Agent 工作流的命令行补充工具，包括：

- `now`
- `ask`
- `mdtoc`
- `view-tree`
- `fileinfo`
- `patch`
- `write`
- `treesitter`
- `pack-zip`

完整列表请运行 `sspec tool --help`。

## 兼容性

sspec 假定 Agent 运行环境具备以下能力：

- 可以读写本地仓库文件；
- 能遵循 `AGENTS.md` 中的指令；
- 可以执行本地命令行命令；
- 能加载并遵循 `.sspec/skills/` 下的技能说明。

## License

AGPL-V3.0
