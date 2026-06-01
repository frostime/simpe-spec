# sspec

[English](README.md)

> AI 编码的规格驱动开发。开发者控制 Agent，状态存文件而非聊天。

---

## 核心理念

AI 编码 Agent 能廉价地生成大量代码，但判断代码是否正确是最昂贵的操作——发生在最后，且难以撤回。

sspec 的核心策略：把验证从昂贵的最终产物前移到廉价的忠实代理上——规格。你能从 spec 预测代码会是什么样，在动手之前就做出判断。

协作的目标不是 Agent 听用户的话，而是双方共同收敛于**意图 ∧ 现实**：你真正想要的，加上世界实际允许的。

三个原则：

- **验证前移**：spec 是忠实代理，你从 spec 预测结果，而非从代码判断。
- **状态外化**：意图与决策存于仓库文件，Agent 从中恢复，不依赖聊天历史。
- **强制对齐**：在不可逆投入前停下，确认意图 ∧ 现实一致。

## sspec 适合你吗？

**适合**，如果你：
- 能判断代码是否正确，想让 Agent 帮你加速而非替你决策
- 愿意在动手前花时间对齐方向

**不太适合**，如果你：
- 无法判断代码质量，需要 Agent 全权负责
- 偏好快速迭代，不审查中间产物

## 工作原理

### Request — 用户意图


```bash
sspec request new add-password-reset                # directive（默认）
sspec request new strange-logout-bug --kind observe
sspec request new async-refactor --kind idea
```

### Change — 原子工作单元

change 是一次内聚、可审查的工作。存放在 `.sspec/changes/<name>/`，包含：

| 文件 | 用途 |
|------|------|
| `spec.md` | 问题、方案、范围和成功标准——**这是合约** |
| `tasks.md` | 文件级执行清单与进度 |
| `memory.md` | 当前状态、关键决策、里程碑——**跨会话的连续性** |
| `design.md` | （可选）接口、数据模型、架构等技术设计 |
| `revisions/` | （可选）design gate 之后的修订 |

### 生命周期

```
澄清  →  设计  →  规划  →  实现  →  审查
          ■              ■
```

`■` = 硬性停止。Agent **必须**等你审查后才能继续。

- **设计门**：审查 `spec.md`（+ `design.md`）。方案合约就此固定。此后的变更记录在 `revisions/` 里。
- **实现门**：审查代码。修复问题、调整范围，或批准完成。

### Memory — 连续性文件

`memory.md` 是 Agent 恢复工作的入口。下一会话中，Agent 先读 `memory.md`——它知道工作进展到哪、哪些文件关键、为什么做了那些决策。不需要从聊天历史重建。

### Spec-docs — 长期知识

架构决策、设计模式、平台约束——那些超越单次 change 的知识。存于 `.sspec/spec-docs/`，Agent 在任意 change 中均可引用。

## 目录结构

```
project/
├── AGENTS.md              ← 协议（Agent 首先读这个）
├── .agents/skills/        ← 从 .sspec/skills/ 同步
└── .sspec/
    ├── project.md         ← 技术栈、约定、关键路径
    ├── requests/          ← 意图记录（directive / observe / idea）
    ├── changes/           ← 活跃与已归档变更
    │   └── <name>/
    │       ├── spec.md
    │       ├── tasks.md
    │       └── memory.md
    ├── spec-docs/         ← 架构与设计知识
    ├── skills/            ← Agent 技能定义
    ├── asks/              ← 结构化问答记录
    ├── howto/             ← 操作指南
    └── tmp/               ← 临时草稿
```

## 快速开始

### 1. 安装并初始化

```bash
pip install sspec
cd your-project
sspec project init
```

然后补全 `.sspec/project.md`，写清技术栈、关键路径和编码约定。

### 2. 启动工作——两种方式

**方式 A：直接告诉 Agent 你的需求。** 把需求描述清楚。有能力的 Agent 会读取 `AGENTS.md` 并遵循 sspec 协议——先澄清，创建 change，写 spec，然后在设计门停下来等你审查。

**方式 B：手写 request 文件。** 如果你想法清晰，自己创建一个 request：

```bash
sspec request new add-dark-mode
```

填好背景、问题、方向和成功标准。Agent 会从这里接手。

### 3. 在门节点审查

Agent 会在两个节点停下：
- **设计门**：读 `spec.md`，确认方案方向，然后告诉 Agent 继续。
- **实现门**：审查代码，要求修复或批准完成。

### 4. 完成后归档

```bash
sspec change archive --with-request <name>
```

## 常用命令

```bash
# Request
sspec request new <name> [--kind directive|observe|idea]
sspec request list

# Change
sspec change new <name> [--from <request>] [--root]
sspec change status <name>
sspec change list
sspec change archive <name> --with-request

# 项目
sspec project status
sspec project update --dry-run

# 文档
sspec doc new "Architecture Overview"

# 工具
sspec tool now
sspec tool mdtoc README.md
```

完整命令列表请运行 `sspec --help`。

## License

AGPL-3.0
