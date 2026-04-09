---
name: {{CHANGE_NAME}}
status: PLANNING
change-type: single
created: {{TIME}}
reference: null
---

<!-- @RULE: Frontmatter
status: PLANNING | DOING | REVIEW | DONE | BLOCKED
change-type: single | sub
reference?: Array<{source, type: 'request'|'root-change'|'sub-change'|'prev-change'|'doc', note?}>

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

# {{CHANGE_NAME}}

## Problem Statement
<!-- @REPLACE -->

<!-- 量化影响。格式："[指标] 导致 [影响]"。
简单：单段。复杂：拆分 "现状" + "用户需求"。 -->

## Proposed Solution
<!-- @REPLACE -->

### Approach
<!-- 核心方案 (1-3 段) + 为什么选这个方案 -->

### Key Change
<!-- REQUIRED. 每个独立变更项用 **Type Label: Title** 格式标注核心决策与约束。
例：**Fix A: 请求链接** / **Feat B: 缓存 TTL 抖动**
tasks.md 引用这些标签 — 不复制设计描述。
如果范围边界不明显，在 Scope Summary 后加 "What Stays Unchanged" 块。 -->

### Scope Summary
<!-- REQUIRED. File | Change 表 — 每个 spec 都必须以此结尾。 -->

### Design Reference
<!-- 技术设计复杂时（新接口/数据模型/架构变更），MUST 创建 design.md。
在此标注：→ 详细技术设计见 [design.md](./design.md)
简单变更可删除此节，在 Approach 中直接说明技术方案。 -->
