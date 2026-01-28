# sspec

[English](./README.md)

文档驱动的 AI 协作框架。通过结构化文件实现跨会话持久记忆。

## 问题

AI 助手在对话结束后丢失上下文。你不断重复解释项目、决策和进度。

## 解决方案

sspec 通过结构化文件（`.sspec/`）提供跨会话持久化：
- **spec.md**: 问题、方案、设计决策
- **tasks.md**: 可执行任务及进度跟踪
- **handover.md**: 会话桥梁——已完成内容、下一步工作
- **spec-docs/**: 项目级规范（架构、API、标准）

## 安装

```bash
pip install sspec
```

## 快速开始

```bash
cd your-project
sspec project init
```

创建 `.sspec/` 目录：
- `project.md` - 项目上下文（技术栈、约束）
- `spec-docs/` - 规范目录
- `changes/` - 活跃变更（功能、bug、重构）
- `skills/` - 自定义 AI 技能和指导

## 工作流

### 1. 创建变更

```bash
sspec change new add-auth
```

AI 创建：
```
.sspec/changes/add-auth/
├── spec.md      # 为什么（WHY）和做什么（WHAT）
├── tasks.md     # 如何做（HOW），每个任务 <2 小时
└── handover.md  # 会话连续性
```

### 2. 实施

AI 读取 spec.md，执行任务，在 tasks.md 中更新进度。

可选的辅助文件：
```
.sspec/changes/add-auth/
├── reference/   # 设计文档、调研笔记
└── scripts/     # 迁移脚本、测试数据
```

### 3. 结束会话

告诉 AI：`@handover`

AI 更新 handover.md：
- Background（变更背景）
- Accomplished（本次完成内容）
- Status（状态：PLANNING/DOING/BLOCKED/REVIEW）
- Next Steps（下一步行动）

### 4. 恢复工作

下次会话：`@resume`

AI 读取 handover.md，从上次中断处精确继续。

## 规范文档

创建项目级规范（持久化，不绑定到变更）：

```bash
sspec spec new "API 设计"           # 单文件
sspec spec new "支付系统" --dir     # 目录
sspec spec list                     # 列出全部
```

## CLI 参考

| 命令 | 说明 |
|------|------|
| `sspec project init` | 初始化 .sspec/ |
| `sspec project status` | 显示概览 |
| `sspec project update` | 更新模板 |
| `sspec change new <name>` | 创建变更 |
| `sspec change list` | 列出变更 |
| `sspec change archive <name>` | 归档已完成变更 |
| `sspec doc new <name>` | 创建规范文档 |
| `sspec doc list` | 列出规范文档 |
| `sspec skill new <name>` | 创建技能 |
| `sspec skill list` | 列出技能 |

## 文件结构

```
.sspec/
├── project.md              # 项目上下文
├── spec-docs/                   # 项目规范文档
├── changes/<name>/
│   ├── spec.md             # 变更规格
│   ├── tasks.md            # 任务和进度
│   ├── handover.md         # 会话桥梁
│   ├── reference/          # 可选：设计文档
│   └── scripts/            # 可选：工具脚本
└── skills/                 # AI 指导
```

## 状态生命周期

```
PLANNING → DOING → REVIEW → DONE
     ↓        ↓
  BLOCKED  BLOCKED
```

## Agent 指令

| 指令 | 动作 |
|------|------|
| `@change <name>` | 切换到变更 |
| `@resume` | 恢复活跃工作 |
| `@handover` | 编写会话交接 |
| `@sync` | 同步 .sspec/ 和代码 |

完整协议见 `AGENTS.md` 模板。

## 兼容性

适用于任何读取 Markdown 上下文文件的 AI 工具：
- Claude Code, Cursor, Windsurf, GitHub Copilot, VS Code Copilot

告诉你的 AI："先读取 `.sspec/AGENTS.md`"

## 何时不使用

- 快速 bug 修复
- 错别字和格式调整
- 简单配置更改

琐碎工作直接做，无需繁文缛节。

## 许可证

MIT
