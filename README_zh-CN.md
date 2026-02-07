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

编辑生成的文件（3-5 句话）：

```markdown
## Problem
用户无法重置密码。每月 50+ 客服工单。

## Initial Direction
邮件重置链接，15 分钟过期。
```

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
   # AI 填写："重置令牌存 Redis 还是 DB？"
   sspec ask prompt .sspec/asks/<file>
   # 人工回答 → AI 接收决策
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
| `sspec ask prompt <file>` | 回答 AI 提问 |
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
└── .claude/skills/              # AI 技能定义
```

支持工具：Claude Code、Cursor、Windsurf、GitHub Copilot、VS Code Copilot

---

## 核心概念

### Request（人工创建）

工作入口点。3-5 句话描述意图。

```bash
sspec request new <idea>
```

示例：
- "认证延迟 5 秒，用户投诉增加"
- "需要 Google/GitHub OAuth 支持"
- "支付 webhook 返回 500，Stripe 日志失败"

AI 将 request 转换为 change。

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

上下文窗口接近限制时（>50 次交互）触发会话中更新。

### Spec-doc（AI 生成）

超越单个变更的项目级设计文档：

- API 标准
- 架构决策
- Schema 定义

AI 识别项目级模式时通过 `sspec doc new` 创建。变更执行时自动引用。

### sspec ask（AI 对人提问）

同步澄清机制。

AI 创建：
```bash
sspec ask create <topic>
```

人工响应：
```bash
sspec ask prompt .sspec/asks/<file>
```

使用示例：
- 设计选择解决（"Redis vs Postgres 缓存？"）
- 破坏性操作确认（"删除测试数据？"）
- 多个有效方法（"认证策略 A vs B？"）

相关问题批量处理在单个 ask 中。

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

# 响应 AI 查询
sspec ask prompt .sspec/asks/<file>

# 状态检查
sspec project status
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
sspec request archive <n>
```

---

## 兼容性

适用于支持基于文件上下文的 AI 工具：

- Claude Code（代理式 CLI）
- Cursor（AI 优先编辑器）
- Windsurf（流程式编码）
- GitHub Copilot（编辑器内）
- VS Code Copilot（对话 + 内联）

要求项目根目录有 `AGENTS.md`（自动加载）。

---

## 不适用场景

跳过以下情况：
- 错字修正
- 5 分钟 bug 修复
- 配置调整

使用于需要以下的工作：
- 多会话连续性
- 决策文档化
- 跨文件协调

---

## 使用示例

### SaaS 开发

```
工作流：
├── sspec request new stripe-integration
├── @change stripe-integration
│   └── AI：设计 → 询问 webhook 处理 → 实现
├── @handover（会话结束）
├── @resume（下次会话）
└── sspec change archive stripe-integration（完成）

项目结构：
├── project.md：Next.js + Postgres + Railway
├── spec-docs/api-standards.md：REST 约定
└── changes/stripe-integration/：功能历史
```

### 开源维护

```
工作流：
├── GitHub issue → sspec request new issue-245
├── @change issue-245
├── AI：分析 → 询问兼容性 → 实现
└── REVIEW → 验证 → 归档

项目结构：
├── requests/：问题分类
├── changes/：活动工作
└── spec-docs/architecture.md：贡献者参考
```

### 咨询

```
工作流：
├── 客户需求 → sspec request new payment-fix
├── @change payment-fix
├── AI：设计 → 询问环境 → 实现
└── handover 记录计费工作

项目结构：
├── project.md：客户约定、部署
├── changes/：交付物跟踪
└── handover.md：交接就绪文档
```

---

## FAQ

**spec.md 填充？**
AI 自动化。人工编写 3-5 句 request。

**何时执行 `sspec change new`？**
很少手动。AI 在 `@change <request>` 指令后执行。

**handover.md 维护？**
AI 管理。工作中更新，`@handover` 时自动。人工恢复时读取。

**分歧处理？**
发出 `@argue` 指令重新规划，或拒绝批准 `@ask`。

**无 AI 使用？**
可能但次优。框架为 AI 协作设计。

---

## License

MIT

---

## 链接

- 仓库：[github.com/frostime/sspec](https://github.com/frostime/sspec)
- Issues：[GitHub Issues](https://github.com/frostime/sspec/issues)

---

**总结**：Request 捕获意图，AI 实现并维护记忆，人工通过检查点控制。
