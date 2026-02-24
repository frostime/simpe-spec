# sspec

**S**spec **S**ynthesizes **P**rograms from **E**xplicit **C**ontext

spec 驱动的 AI 辅助开发框架。

---

## 问题

AI 辅助开发的记忆丢失问题：
- 会话 3："为什么用 Redis 而不是 Postgres 做缓存？"——AI 不记得决策
- 会话 7："认证逻辑在哪个文件？"——AI 给出多个冲突位置
- 会话 14：新对话窗口——AI 要求重新解释整个项目

**根本原因**：AI 缺乏跨会话持久化。每次对话从零开始。

**解决方案**：项目状态存于文件。AI 从磁盘读取上下文，在 handover 文件中维护记忆，通过 `@ask` 设置人工检查点。

---

## 工作流

### 1. 创建 Request

```bash
sspec request new forgot-password
```

编辑生成的文件。


### 2. 委托给 AI

在 AI 对话中：

```
@change forgot-password
```

AI 工作流：

1. **分析** — 评估规模（micro/single/multi-change）
2. **澄清** 通过 `sspec ask`：
   ```bash
   sspec ask create token-storage
   # AI 填写提问："重置令牌存 Redis 还是 DB？"
   # User 在自动生成的 py 文件中填写回答
   sspec ask prompt .sspec/asks/<file>.yml
   # AI 接收决策
   ```
3. **创建变更** — AI 执行 `sspec change new --from forgot-password`
4. **编写规格** — AI 填充 `spec.md`：
   - Section A：问题（量化："50+ 工单/月，$200 成本"）
   - Section B：方案（"邮件重置，15 分钟 TTL，bcrypt"）
   - Section C：实施（文件级分解）
5. **请求批准** — AI 通过 `@ask` 展示方案
6. **实施** — 批准后，AI 编写代码
7. **跟踪进度** — AI 在 `tasks.md` 中标记 `[x]`
8. **维护记忆** — AI 在 `handover.md` 中记录决策

### 3. 会话结束

AI 在终止前自动执行 `@handover`，更新记忆文件。

### 4. 会话恢复

```
@resume
```

AI 读取 `handover.md` → 恢复上下文 → 继续工作。

---

## 职责矩阵

### 人工

| 操作 | 触发时机 |
|------|---------|
| `sspec request new <idea>` | 捕获想法（3-5 句话） |
| `@change <n>` | 启动 request 工作 |
| `@resume` | 恢复上次会话 |
| 回答 AI 提问  | Agent 运行 ``sspec ask create` 之后 |
| 批准方案 | 响应设计 `@ask` |
| 验证实现 | 审查 REVIEW 状态变更 |

### AI

| 职责 | 替代内容 |
|------|---------|
| 执行 `sspec change new` | 手动创建变更 |
| 填充 `spec.md` 各节 | 编写正式规格 |
| 维护 `tasks.md` | 手动任务跟踪 |
| 更新 `handover.md` | 重新解释决策 |
| 执行 `sspec ask create` | 决定何时提问 |
| 参考 `project.md`、`spec-docs/` | 提醒 AI 项目约定 |
| 归档完成工作 | 手动组织 |

决策权通过 `@ask` 检查点保留在人工侧。行政开销由 AI 处理。

---

## 安装

```bash
pip install sspec
# 或
uv tool install sspec
```

## 项目设置

```bash
cd project-root
sspec project init
```

生成结构：

```
project/
├── AGENTS.md                    # AI 协议（工具自动加载）
├── .sspec/
│   ├── project.md               # 身份、约定、记忆
│   ├── spec-docs/               # 架构文档（AI 生成）
│   ├── changes/                 # 活动工作（AI 管理）
│   ├── requests/                # 意图捕获（人工创建）
│   └── asks/                    # AI 对人提问
└── .xxx/skills/              # AI 技能定义
```

---

## 核心概念

### Request（人工创建）

工作入口点。尽可能清晰地描述意图。

```bash
sspec request new <idea>
```


在对话中引用 reqeust 文件，并告知 Agent "ssepc@change from this request".

### Change（AI 管理）

AI 的工作单元：

```
.sspec/changes/<timestamp>_<n>/
├── spec.md      # 问题、方案、实施计划
├── tasks.md     # 清单，执行中更新
└── handover.md  # 会话记忆、决策、引用
```

状态流转：
```
PLANNING → DOING → REVIEW → DONE
    ↑       ↓
    └─── BLOCKED
```

规模评估（AI 确定）：
- **Micro**（≤3 文件，≤30 分钟）：无变更仪式，直接执行
- **Single**（1 周，≤15 文件）：标准变更
- **Multi**（>1 周，>15 文件）：根变更 + 子变更

### Handover（AI 记忆）

跨会话持久化机制：

- **Background**：变更目的
- **Accomplished**：会话工作
- **Next Steps**：恢复点
- **References & Memory**：
  - **Key Files**：关键文件路径
  - **Decisions & Rationale**：设计选择和推理
  - **Gotchas & Context**：边缘情况、风险、隐性知识

工作中和会话结束时更新。`@resume` 时首先读取。

### Spec-doc\

超越单个变更的项目级设计文档：

- API 标准
- 架构决策
- Schema 定义

告知 Agent 创建文档 `sspec@doc`，Agent 调用 CLI 并自动填写。

### sspec ask（AI 对人提问）

同步澄清机制。

AI 创建：
```bash
sspec ask create <topic>
```

生成提问文档，人工在文档中填写回答。

Agent 运行指令获取回答。
```bash
sspec ask prompt .sspec/asks/<file>.yml
```

> [!note]
> 这个流程依赖工具调用审批
> 人工回答的时机应在 `sspec ask prompt` 工具运行之前

---

## 指令

基于对话的工作流控制：

| 指令 | 功能 |
|------|------|
| `@status` | 项目概览（活动变更、阻塞点） |
| `@change <n>` | 加载变更上下文（handover → tasks → spec） |
| `@resume` | 继续上次活动变更 |
| `@handover` | 持久化状态（会话结束时自动执行） |
| `@sync` | 协调代码更改与 tasks.md |
| `@ask` | 建议 AI 咨询（AI 决定执行） |
| `@argue` | 停止当前方法 |

---

## CLI 参考

### 人工执行命令

```bash
# 捕获意图
sspec request new <idea>

# 状态检查
sspec project status

sspec request archive
sspec change archive
```

### AI 执行命令

```bash
# 变更管理
sspec change new --from <request>
sspec change new <n>
sspec change new --root           # 多变更
sspec change list
sspec change archive <n>

# 文档
sspec doc new "<topic>"
sspec doc new "<topic>" --dir
sspec doc list

# 查询系统
sspec ask create <topic>
sspec ask list

# Request 管理
sspec request list
sspec request link <req> <change>
```

---

## 兼容性

适用于支持基于文件上下文的 AI 工具，在 project init 的时候会创建填写 `AGENTS.md`。

---

## License

AGPL-V3.0
