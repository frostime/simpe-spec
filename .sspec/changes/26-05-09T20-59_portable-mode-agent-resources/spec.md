---
name: portable-mode-agent-resources
status: REVIEW
change-type: single
created: 2026-05-09T20:59:30
reference: null
---

# portable-mode-agent-resources

## Problem Statement

sspec 的核心资产（Agent protocol + 内置 SKILL）目前主要通过 `project init` 安装到项目后被 Agent 发现，导致一次性、轻量、非项目化场景无法稳定复用 sspec 的规范。用户如果只是想让第三方 Agent “参考 sspec-design 风格出方案”，现状容易出现三类失败：Agent 不知道 sspec 是什么、误以为必须初始化 `.sspec/` 或创建 change、或者一次性暴露大量 SKILL 原文造成上下文成本上升。

## Proposed Solution

### Approach

新增 portable mode CLI：`sspec portable` 与 `sspec portable read <scope:slug>`。该模式不依赖当前目录存在 `.sspec/`，也不写入任何项目状态；它向零 sspec 上下文的 Agent 输出一份 portable bootstrap：先简要解释 sspec 是一套面向 AI coding agent 的规则、SKILL 与模板规范，再说明当前是“只借用规范、不进入完整项目工作流”的 portable 使用模式。

`sspec portable` 是启动说明与索引，不输出完整 AGENTS.md，也不输出全部 SKILL 原文。它采用渐进披露：引导 Agent 先读取 `rule:sspec`，再根据任务按需读取匹配的 SKILL、HOWTO 或模板。`sspec portable read ...` 是按需读取入口。

选择 `portable` 而不是 `resource/guide`：`resource` 过于像资源浏览器，`guide` 过于像正常 sspec 工作流指南；`portable` 明确表达“脱离项目安装，只借用 sspec 核心规范”。

### Key Change

**Feat A: Portable Bootstrap Command**

新增顶层命令 `sspec portable`，输出 portable-mode Agent bootstrap，包括：
- sspec 零上下文简介：rules / skills / templates 分别是什么；
- portable mode 定义：遵循 sspec 规范，但不初始化、不管理当前项目的 sspec 状态；
- do / do_not 约束；
- 渐进披露步骤：先 `read rule:sspec`，再按需读取 SKILL/HOWTO/template；
- 标准 `<available_skills>` SKILL 索引；
- project-to-portable behavior mapping：当原始规则/SKILL 提到 sspec 项目文件或命令时，在 portable mode 下如何改写行为。

**Feat B: Scoped Builtin Resource Reader**

新增 `sspec portable read <scope:slug>`，支持按需读取内置资源，并在输出 wrapper 中暴露当前安装环境中的绝对 source path，方便 Agent 直接读取源文件：
- `rule:sspec` — 渲染后的内置 AGENTS/project protocol rule；
- `skill:<name>` — 内置 SKILL.md；
- `skill:<name>/<relative-path>` — SKILL 附属文件；
- `howto:<name>` — 内置 HOWTO 文档；
- `template:<path>` — 内置模板文件。

不提供 `rule:portable`：portable overlay 已经直接包含在 `sspec portable` bootstrap 中，重复暴露会制造概念噪音。

**Guard C: No-Project / No-State Safety**

portable command 不调用 `get_sspec_root()`，不要求当前目录已初始化 sspec，不创建 `.sspec/`、`AGENTS.md`、change、request、doc 或 skill link。输出必须明确：除非用户显式要求正式初始化或管理 sspec 项目，否则 Agent 不应运行项目写入命令。

**Guard D: Safe Resource Resolution**

资源读取使用 package resource API，而不是源码路径假设；拒绝绝对路径、`..` path traversal、未知 scope、未知 skill、目录读取等不安全或不明确输入。

### Scope Summary

| File | Change |
|---|---|
| `src/sspec/cli.py` | 注册新的 `portable` 顶层命令 |
| `src/sspec/commands/portable.py` | 新增 CLI wiring：`sspec portable` / `sspec portable read` |
| `src/sspec/services/portable_service.py` | 新增 portable bootstrap 渲染、resource 解析与读取逻辑 |
| `tests/test_portable_command.py` | 覆盖 CLI 行为、非 sspec 项目运行、输出结构、read 成功/失败路径 |
| `tests/test_portable_service.py` | 覆盖资源解析、安全校验、skill index 构建、rule 渲染 |

What stays unchanged:
- 不改变 `project init/update` 行为。
- 不改变 `.sspec/skills` hub-spoke 安装模型。
- 不改变现有 `skill list/new/dominate` 项目内 skill 管理语义。
- 不自动把 portable resources 安装到任何 Agent 目录。
- 不默认输出完整 AGENTS.md 或所有 SKILL 正文。

### Design Reference

→ See [design.md](./design.md)
