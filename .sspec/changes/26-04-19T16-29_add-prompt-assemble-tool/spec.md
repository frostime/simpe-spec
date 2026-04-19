---
name: add-prompt-assemble-tool
status: REVIEW
change-type: single
created: 2026-04-19 16:29:13
reference:
- source: .sspec/requests/26-04-19T16-14_add-prompt-assemble-tool.md
  type: request
  note: Linked from request
---
<!-- @RULE: Frontmatter
status: PLANNING | DOING | REVIEW | DONE | BLOCKED
change-type: single | sub
reference?: Array<{source, type: 'request'|'root-change'|'sub-change'|'prev-change'|'doc'|'revision', note?}>

Sub-change MUST link root:
reference:
  - source: ".sspec/changes/<root-change-dir>"
    type: "root-change"
    note: "Phase <n>: <phase-name>"

Single-change common reference:
reference:
  - source: ".sspec/requests/<request-file>.md"
    type: "request"
  - source: ".sspec/changes/<change-dir>"
    type: "prev-change"
    note: "Follow-up to <change-name>."
-->

# add-prompt-assemble-tool

## Problem Statement
当前 `sspec tool` 缺少一个可由 Agent 直接在单条命令里拼装 prompt 的 builtin tool，导致“引用代码 / 截取代码片段 / 拼接 shell 输出 / 提供目录树”这类上下文整理仍然依赖手工复制和临时排版，降低了和 Web Agent、网页 LLM、外部聊天界面的协作效率。

用户需要两条同样重要的使用路径：一条是 inline generate，Agent 能直接通过 `--add-*` 系列参数当场组装 prompt；另一条是把这次组装结果作为 preset 导出并复用。preset 是复用层，inline generate 是运行主路径。输出结果应写入 `.sspec/tmp/` 并自动打开，方便用户继续编辑或直接转交给外部 Agent。

## Proposed Solution

### Approach
新增内建工具 `sspec tool prompt`，采用“单命令 + flags + 无参交互式入口”的形式，统一承载三类能力：1) 通过 `--add-*` flags 直接构造 source 集合并立刻生成 prompt；2) 通过 `--from-preset` 载入已有定义；3) 通过 `--to-preset` 把本次实际执行的 source 集合保存为 `.sspec/prompts/<name>.yml`。这样 Agent 可以在一次调用里完成临时拼装和规则沉淀，用户也能继续通过无参交互式入口手工组装。

V1 source 范围先覆盖 `file`、`file-chunk`、`shell`、`file-tree`、`glob` 五类。工具运行时动态读取源内容，渲染为适合 Agent 引用的 hybrid-headers 文本格式：每个 section 使用 `BEGIN/END` 哨兵块包裹，块内先放 YAML frontmatter 作为 meta，再用 fence 包裹正文内容，从结构上明确分隔 metadata 与 content。默认结果写入 `.sspec/tmp/*.prompt.txt` 并尝试调用现有 editor 集成打开。

### Key Change
**Feat A: Inline-first prompt assembly CLI**  
新增 `sspec tool prompt`，支持重复使用 `--add-file`、`--add-chunk`、`--add-shell`、`--add-tree`、`--add-glob` 等参数，在单条命令中直接定义 source 集合并生成 prompt。

**Feat B: Preset import/export on top of runtime sources**  
支持 `--from-preset` 读取 `.sspec/prompts/<name>.yml`，并支持 `--to-preset` 将本次实际使用的 source 集合导出为 preset；inline sources 与 preset sources 可在同次执行中合并。

**Feat C: Interactive authoring flow**  
无参运行进入交互流程，支持类型选择、路径补全、逐项添加 source、可选导出 preset，覆盖手工 prompt 组装场景。

**Feat D: Agent-friendly output contract**  
输出采用 hybrid-headers 文本格式，使用 `BEGIN/END` 哨兵块 + YAML frontmatter meta + fenced content 的分层结构，并默认写入 `.sspec/tmp/*.prompt.txt` 后自动打开；shell source 在非交互运行时需要显式 `--allow-shell`，交互运行时逐项确认。

### Scope Summary
| File | Change |
|------|--------|
| `src/sspec/builtin_tools/prompt.py` | 新增 prompt tool CLI、inline `--add-*` 参数解析、交互入口、输出渲染与运行编排 |
| `src/sspec/commands/tool.py` | 注册 builtin `prompt` 子命令 |
| `src/sspec/services/prompt_service.py` | 实现 source 归一化、preset 解析/导出、source 执行、输出文件命名与安全策略 |
| `.sspec/spec-docs/builtin-tools.md` | 记录 `prompt` 工具接口、inline flags、preset 目录与输出契约 |
| `tests/test_tool_command.py` | 覆盖 CLI 入口、`--prompt`、inline 运行、preset import/export 与 dry-run 行为 |
| `tests/test_prompt_service.py` | 覆盖 source schema、inline 归一化、frontmatter + fenced-content 渲染格式、shell 安全门与输出落盘逻辑 |

### Design Reference
→ 详细技术设计见 [design.md](./design.md)
