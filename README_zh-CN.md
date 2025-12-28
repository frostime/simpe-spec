# sspec

[English](./README.md)


**为 AI 编码助手设计的轻量级规范工作流。**

sspec 解决一个简单的问题：AI 助手在对话结束后会忘记一切。你精心解释的上下文、做过的决策、完成的进度——全部消失。

sspec 通过结构化文件给 AI 一个持久记忆，让它能跨会话延续工作。

---

## 工作原理

```
你: "添加用户认证功能"
AI: 读取 .sspec/AGENTS.md → 理解工作流程
AI: 创建提案，分解任务，跟踪进度
... 对话结束 ...

新会话:
你: "继续上次的工作"
AI: 读取 handover.md → 准确知道做了什么、下一步是什么
```

---

## 快速开始

### 安装

```bash
pip install sspec
```

### 初始化

```bash
cd your-project
sspec init
```

生成的目录结构：
```
.sspec/
├── AGENTS.md           # AI 首先读取这个
├── knowledge/
│   └── index.md        # 项目上下文
├── changes/            # 进行中的工作
├── prompts/            # 命令定义
└── handover.md         # 跨会话状态
```

### 配置

编辑 `.sspec/knowledge/index.md`，填入项目信息：
- 技术栈
- 编码规范
- 关键约束

这是 AI 永远可以访问的上下文。

---

## 日常工作流

### 开始新功能

告诉 AI：
```
/propose add-user-auth
```

AI 会：
1. 创建 `changes/add-user-auth/` 目录，包含 proposal、tasks、memo、handover
2. 帮你定义要做什么、为什么做
3. 把工作拆分成小的、可验证的步骤

### 工作过程中

AI 自动跟踪：
- **进度**：完成了什么，下一步是什么
- **决策**：为什么选择 X 而不是 Y
- **转向**：你什么时候改变了方向

随时可以查看状态：
```
/status
```

### 结束会话前

关闭对话前：
```
/handover
```

AI 会写一份交接文档，记录：
- 完成了什么
- 当前状态
- 具体的下一步
- 需要记住的注意事项

### 下次会话

开始时：
```
/context
```

AI 重新加载所有上下文，无缝继续工作。

---

## 命令一览

| 命令 | 作用 |
|------|------|
| `/propose <名称>` | 创建新的变更提案 |
| `/status` | 显示当前状态 |
| `/pivot` | 记录方向变更 |
| `/handover` | 生成会话交接文档 |
| `/context` | 重新加载项目上下文 |
| `/archive` | 归档已完成的变更 |

这些命令在任何读取 AGENTS.md 的 AI 工具中都能使用（Claude Code、Cursor 等）

---

## CLI 命令

```bash
sspec init              # 在当前目录初始化 .sspec
sspec new <名称>        # 创建新变更
sspec list              # 列出所有变更
sspec status            # 显示状态概览
sspec archive <名称>    # 归档已完成的变更
sspec prompt --list     # 列出可用的提示词
```

---

## 文件结构说明

### 项目级别

| 文件 | 用途 | 你需要编辑？ |
|------|------|-------------|
| `knowledge/index.md` | 项目上下文、技术栈、规范 | 是，初始化时 |
| `knowledge/*.md` | 领域知识、架构文档 | 按需 |
| `handover.md` | 全局跨变更状态 | AI 更新 |

### 每个变更

| 文件 | 用途 | 你需要编辑？ |
|------|------|-------------|
| `proposal.md` | 为什么做、做什么 | 审核并确认 |
| `tasks.md` | 计划、进度、决策 | AI 更新 |
| `memo.md` | 研究笔记、代码片段 | AI 的草稿本 |
| `handover.md` | 会话延续 | AI 更新 |

---

## 示例会话

**第一次会话：**
```
你: 给应用加个深色模式。/propose dark-mode

AI: 已创建变更: dark-mode
    - 提案: 添加深色模式切换，支持跟随系统偏好
    - 任务: 识别出 5 个步骤
    需要审核吗？

你: 可以，开始吧。

AI: [实现前 3 个任务，更新进度]

你: 我要走了。/handover

AI: 交接已保存。
    已完成: 主题 Provider、切换组件、CSS 变量
    下一步: 持久化偏好、添加到设置页面
```

**第二次会话：**
```
你: /context

AI: 上下文已加载。
    项目: my-app (React + TypeScript)
    当前变更: dark-mode (进行中, 3/5 任务)
    下一步: 将用户偏好保存到 localStorage
    
    从上次中断处继续...
```

---

## 使用技巧

### 最佳实践

1. **写好上下文**：认真填写 `knowledge/index.md`
2. **审核提案**：不要让 AI 猜测需求
3. **坚持用 `/handover`**：这是会话之间的桥梁
4. **保持变更小**：一个功能 = 一个变更

### 什么时候不用 sspec

- 快速修 bug
- 改错别字、调格式
- 简单的配置变更

这些直接做就行，不需要正式提案。

---

## 常见问题

**Q: 能和 [某个 AI 工具] 一起用吗？**

任何读取 AGENTS.md 的工具都行：Claude Code、Cursor、Windsurf、GitHub Copilot 等。

**Q: AI 不按流程走怎么办？**

告诉它："先读 .sspec/AGENTS.md"

**Q: 可以自定义提示词吗？**

可以。编辑 `.sspec/prompts/` 下的文件。

**Q: 这和直接聊天有什么区别？**

聊天上下文会消失。sspec 文件会保留。你不用反复解释你的项目。

---

## 设计理念

### 为什么是文件而不是数据库？

- 文件可以用 Git 版本控制
- 文件对人和 AI 都可读
- 文件不需要额外的服务

### 为什么分 proposal/tasks/memo/handover？

- **proposal**：锁定意图，防止范围蔓延
- **tasks**：结构化的项目状态
- **memo**：自由探索，不污染结构化数据
- **handover**：专门为跨会话设计

### 借鉴了什么？

- [OpenSpec](https://github.com/Fission-AI/OpenSpec)：proposal → apply → archive 工作流
- [Spec Kit](https://github.com/github/spec-kit)：`[NEEDS CLARIFICATION]` 模式
- Claude Code 的 AGENTS.md 约定

---

## License

MIT
