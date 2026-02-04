# sspec

**S**spec **S**ynthesizes **P**rograms from **E**xplicit **C**ontext

一个简单的 spec 驱动 Vibe Coding 框架，为个人开发者设计。

---

## 为什么需要 sspec？

你在用 AI 写代码。一开始很顺利——AI 理解你的意图，代码质量不错。

然后项目变大了。AI 开始：
- 忘记你上周做的设计决策
- 不知道哪些功能已经完成、哪些还在进行
- 每次新会话都要重新解释项目背景
- 在复杂任务上迷失方向，做出不一致的修改

**根本问题**：AI 没有跨会话的记忆。每次对话都是从零开始。

**sspec 的解法**：把项目状态写进文件。AI 每次启动时读取这些文件，就能"记住"一切。

---

## sspec 做了什么？

运行 `sspec project init` 后，你的项目会多出：

```
your-project/
├── AGENTS.md                    # AI 协议：告诉 AI 如何使用 sspec
├── .sspec/
│   ├── project.md               # 项目背景、技术栈、约定
│   ├── spec-docs/               # 项目级设计文档
│   ├── changes/                 # 进行中的变更
│   ├── requests/                # 想法草稿
│   └── asks/                    # 人机问答记录
└── .claude/skills/              # AI 技能参考（也可以是 .github/skills/）
    ├── sspec/SKILL.md
    ├── sspec-ask/SKILL.md
    └── write-spec-doc/SKILL.md
```

**AGENTS.md** 是关键——它定义了 AI 应该如何与 `.sspec/` 目录交互。把它放在根目录，AI 工具（Claude Code、Cursor、Copilot）会自动读取。

---

## 核心概念

### Change（变更）

Change 是 sspec 的核心工作单元。一个 feature、一个 bug fix、一次重构，都是一个 change。

每个 change 有三个文件：

```
.sspec/changes/add-auth/
├── spec.md      # 问题是什么？方案是什么？
├── tasks.md     # 具体要做哪些事？每个任务 <2 小时
└── handover.md  # 会话交接：做了什么、下一步做什么
```

**spec.md** 回答 WHY 和 WHAT：
- Section A: 问题描述（量化的痛点）
- Section B: 解决方案（为什么选这个方案）
- Section C: 实施计划（具体改哪些文件）
- Section D: 阻塞和反馈

**tasks.md** 回答 HOW：
- 可执行的任务清单
- 每完成一个就标记 `[x]`
- AI 每次都能看到进度

**handover.md** 是会话间的桥梁：
- Background: 这个变更在做什么
- Accomplished: 本次会话完成了什么
- Next Steps: 下次应该做什么

AI 读完 handover.md，30 秒内就能继续工作。

### Request（请求）

Request 是变更之前的想法草稿。

当你有个模糊的想法（"认证系统好像有点慢"），但还没想清楚怎么做时，先写成 request：

```bash
sspec request new slow-auth
```

Request 只需要描述问题和初步想法。等想清楚了，再转成 change：

```bash
sspec request link slow-auth auth-optimization
```

### Spec-doc（规范文档）

Spec-doc 是项目级的设计文档，不绑定到具体的 change。

比如 API 设计规范、数据库 schema、架构决策——这些文档应该长期存在，供所有 change 参考：

```bash
sspec doc new "API 设计规范"
sspec doc new "支付系统" --dir  # 复杂主题用目录
```

存放在 `.sspec/spec-docs/`，AI 在做相关 change 时会参考。

### sspec ask（人机协作）

当 AI 在执行过程中需要你的输入时，它使用两步流程：

```bash
# 步骤 1：AI 创建问题模板
sspec ask create --name api_style

# 步骤 2：AI 编辑 .py 文件，填写 REASON + QUESTION
# （或者你可以在文件中预先填写 USER_ANSWER）

# 步骤 3：执行并收集回答
sspec ask prompt .sspec/asks/<timestamp>_api_style.py
```

AI 会暂停等待你的回答。问答记录保存在 `.sspec/asks/`，下次 AI 还能看到。

**好处**：
- 没有 shell 转义/编码问题（直接编辑 Python 文件）
- 你可以在文件中预先填写回答（跳过终端提示）
- 减少 AI 在不确定时的猜测
- 问答记录可追溯
- 在以 Credit 计费的 AI Coding 环境(Copilot)下能省计费消耗
  - Traditional: Turn 1 (5 tool calls) → Stop → 1 Credit + Turn 2 (5 tool calls) → 1 Credit = **2 Credits**
  - Sspec ask: Turn 1 (5 tool calls → ask user → 5 tool calls) = **1 Credit**

---

## 工作流程

### 开始新任务

```bash
# 1. 创建 change
sspec change new add-user-auth

# 2. AI 会帮你填写 spec.md 和 tasks.md
#    它会用 sspec ask 来澄清不确定的地方

# 3. 确认方案后，AI 开始执行任务
```

### 结束会话

告诉 AI：`@handover`

AI 会更新 handover.md，记录本次进度和下一步计划。

### 恢复工作

下次开始时：`@resume`

AI 读取 handover.md，从上次中断的地方继续。

### 任务完成

当所有任务完成后，change 进入 REVIEW 状态。你确认没问题后：

```bash
sspec change archive add-user-auth
```

Change 被归档到 `.sspec/changes/.archive/`。

---

## 状态流转

每个 change 有状态：

```
PLANNING ──→ DOING ──→ REVIEW ──→ DONE
    ↑          │
    │          ↓
    └─────── BLOCKED
```

- **PLANNING**: 还在设计，spec.md 没定稿
- **DOING**: 在实施，tasks.md 在更新
- **BLOCKED**: 卡住了，等外部依赖
- **REVIEW**: 做完了，等你验收
- **DONE**: 归档

AI 会根据状态决定该做什么。

---

## 安装

```bash
pip install sspec
```

## 初始化项目

```bash
cd your-project
sspec project init
```

交互式选择 skill 安装位置（.claude、.github、.agent）。

## CLI 速查

```bash
# 项目
sspec project init          # 初始化
sspec project status        # 查看状态
sspec project update        # 更新模板

# 变更
sspec change new <name>     # 创建
sspec change list           # 列表
sspec change archive <name> # 归档

# 请求
sspec request new <name>    # 创建想法草稿
sspec request link <req> <change>  # 关联到变更

# 规范文档
sspec doc new <name>        # 创建
sspec doc list              # 列表

# 人机协作
sspec ask create [--name <n>]  # 创建问题模板
sspec ask prompt <path>        # 执行问题提示
```

---

## AI 指令

在对话中使用这些指令控制 AI：

| 指令 | 作用 |
|------|------|
| `@change <name>` | 切换到某个 change（或创建新的） |
| `@resume` | 恢复上次的工作 |
| `@handover` | 结束会话，写交接文档 |
| `@sync` | 同步代码变更到 tasks.md |
| `@argue` | 停下来，我有不同意见 |

---

## 兼容性

sspec 生成的是 Markdown 文件。任何能读取项目文件的 AI 工具都能用：

- Claude Code
- Cursor
- Windsurf
- GitHub Copilot
- VS Code Copilot

只需告诉 AI："先读 AGENTS.md"。

---

## 什么时候不需要 sspec

- 改个错别字
- 快速修个小 bug
- 调整一下配置

简单的事情直接做，不需要走流程。sspec 是为那些"跨越多个会话、需要记住上下文"的任务设计的。

---

## License

AGPL-V3.0

