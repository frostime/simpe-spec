# sspec

[English](README.md)

**S**spec **S**ynthesizes **P**rograms from **E**xplicit **C**ontext.

sspec 是一个面向 AI 辅助开发的文档驱动工作流。它把规划、决策与交接写入仓库文件，让 Agent 可以跨会话延续工作，而不是每次从零开始。

## sspec 解决什么问题

AI 编程在连续性上常见三类问题：

- 上下文压缩后，关键决策丢失；
- 多轮会话后，实现方向发生漂移；
- 人工反复解释项目背景，成本高。

sspec 的做法是：把工作状态放进 `.sspec/`，把 Agent 行为约束放进 `AGENTS.md`。

## 快速开始

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

在 `.sspec/requests/...` 中写清问题、初始方向、成功标准。

### 4) 交给 Agent 执行

在 Agent 对话中输入：

```text
@change add-password-reset
```

Agent 应按 SSPEC 生命周期推进，更新变更文件，并在 `@ask` 关卡向你确认关键决策。

### 5) 后续恢复

```text
@resume
```

Agent 会读取 `handover.md`、`tasks.md`、`spec.md`，从上次停止点继续。

## 生命周期

每个阶段都有对应 SKILL（位于 `.sspec/skills/`）。

```text
[Request] -> [Research] -> [Design] -> [Plan] -> [Implement] -> [Review] -> [Handover]
                     (ask)      (ask)         (ask)        (feedback loop)
```

核心规则：

- `Research` 重点是理解问题空间和代码上下文。
- `Design` 与 `Implement` 是强制 `@ask` 关卡。
- `Plan` 采用轻量 `@ask` 确认。
- `Implement` 与 `Review` 构成反馈闭环，直到用户满意。
- `Handover` 不是收尾装饰，而是生命周期中的正式阶段。

## sspec 会创建哪些内容

```text
project/
├── AGENTS.md
└── .sspec/
    ├── project.md
    ├── changes/
    ├── requests/
    ├── asks/
    ├── spec-docs/
    ├── skills/
    └── tmp/
```

- `project.md`：项目身份、约定与长期记忆。
- `changes/<id>/spec.md`：问题定义与方案说明。
- `changes/<id>/tasks.md`：可执行任务清单与进度。
- `changes/<id>/handover.md`：会话记忆与下一步。
- `requests/`：从意图到变更前的请求入口。
- `asks/`：Agent 与用户的问答记录。

## 人与 Agent 的分工

**人工负责**

- 创建请求；
- 回答 `@ask`；
- 批准设计与 Review 结果。

**Agent 负责**

- 评估规模（micro/single/multi-change）；
- 创建并维护变更文件；
- 持续更新任务和交接；
- 驱动 ask-feedback 闭环直到验收通过。

## 对话指令

这些指令由加载了 `AGENTS.md` 的 Agent 解释执行。

| 指令 | 常见用途 |
|------|----------|
| `@change <name>` | 启动或恢复某个变更 |
| `@resume` | 继续当前活动变更 |
| `@handover` | 持久化当前状态，便于下次会话恢复 |
| `@sync` | 让文档状态（`tasks.md`、`handover.md`）与代码现状一致 |
| `@argue` | 停止当前方案并重新评估范围 |

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

### Ask

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
- 能使用 claude skills。

## License

AGPL-V3.0
