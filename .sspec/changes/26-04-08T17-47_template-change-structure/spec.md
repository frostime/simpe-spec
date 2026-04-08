---
name: template-change-structure
status: DONE
type: ""
change-type: sub
created: 2026-04-08 17:47:00
reference:
  - source: ".sspec/changes/26-04-08T17-37_sspec-vnext"
    type: "root-change"
    note: "Phase 1: Template & Change Structure"
---

# template-change-structure

## A. Problem Statement

当前 change 模板存在三个结构性问题：

1. **spec.md 职责过重**：同时承载规格定义和技术设计细节，`### Key Design` 下的 dimension 引导占据大量篇幅，实际效果是 Agent 在 spec 里堆砌技术设计而非精炼变更定义
2. **缺少独立的 design artifact**：技术设计（接口、数据模型、架构）没有专属容器，淹没在 spec.md 的 `### Key Design` 里，用户难以独立审查
3. **缺少 revision 机制**：design gate 后的范围/设计变更无处记录，只能在 spec.md 里硬改（丢失历史）或新建 change（断开上下文）
4. **handover.md 模板过重**：大量 `@RULE` 注释占据空间，对 Agent 是噪音（SKILL 已覆盖这些规则）

## B. Proposed Solution

### Approach

重新设计 `src/sspec/templates/change/` 下的模板文件集，建立清晰的职责分离：

- **spec.md** = 变更契约（what + why + 概要 how）
- **design.md** = 技术设计详情（接口、数据模型、架构、行为规范）—— 新增模板
- **revision template** = 演化记录（gate 后的所有变更）—— 新增模板
- **handover.md** = 会话状态 —— 精简 @RULE 注释
- **tasks.md** = 保持现有格式不变（仅在 Phase 4 改为 lazy creation）

同步更新 `change-root/` 下的对应模板。

### Key Design

#### spec.md 新结构

```markdown
---
name: {{CHANGE_NAME}}
status: PLANNING
change-type: single
created: {{TIME}}
reference: null
---

# {{CHANGE_NAME}}

## Problem Statement
<!-- 量化影响。格式："[指标] 导致 [影响]"。
     简单：单段。复杂：拆分"现状" + "用户需求"。 -->

## Proposed Solution

### Approach
<!-- 核心方案 (1-3 段) + 为什么选这个方案 -->

### Key Change
<!-- REQUIRED. 每个独立变更项用 **Type Label: Title** 格式标注。
     例：**Fix A: 请求链接** / **Feat B: 缓存 TTL 抖动**
     tasks.md 引用这些标签，不复制设计描述。 -->

### Scope Summary
<!-- REQUIRED. File | Change 表。 -->

## Design Reference
<!-- 技术设计复杂时（新接口/数据模型/架构变更），
     MUST 创建 design.md 并在此处标注：
     → 详细技术设计见 [design.md](./design.md)
     简单变更可省略此节，在 Approach 中直接说明。 -->
```

**与旧版对比**：
- 删除 `### Key Design` 及其内部的 dimension 引导 —— 技术设计移到 design.md
- 删除 `type` frontmatter 字段（未使用）
- 新增 `## Design Reference` 节作为到 design.md 的桥接
- `@RULE` 注释大幅精简，只保留格式约束

#### design.md 新模板

```markdown
---
change: "{{CHANGE_NAME}}"
created: {{TIME}}
---

# Design: {{CHANGE_NAME}}

<!-- 本文件记录技术设计详情。创建条件：
     变更涉及新接口定义、数据模型变更、或架构逻辑改动。
     简单 bugfix/文案修改不需要此文件。 -->

<!-- QUALITY BAR (不可违反):
  用半结构化、形式化的表达替代平铺直叙的纯文本。
  核心目标：提高信息密度，降低不确定性，提高用户理解效率。
  一句话：能展示的不要叙述 (show, don't describe)。

  常见手段 (非穷举):
  - typed code block: 接口、类型、Schema、配置、prompt...
  - ASCII diagram: 调用链、状态机、模块树、内容大纲...
  - table: before/after 对比、选项权衡、scope 映射...
  - labeled items: 多项变更标注 (Fix A / Feat B / Step 1...)
  - 伪代码、决策树、约束列表等同样有效

  Anti-pattern:
    ❌ "我们将添加一个接受 X 返回 Y 的函数"
    ✅ `def process(x: Input) -> Output: ...`
-->

<!-- 按变更性质组织本文档。没有固定章节要求。
  以下是不同类型变更的参考组织方式 (选用，不强制):

  Feature/Bugfix  → 接口签名 + 行为流程 + 数据模型
  Refactor        → Before/After 结构对比 + 迁移步骤
  文档/模板       → 内容大纲 + 章节层级
  Prompt/规则     → Before/After 示例 + 决策逻辑
  配置/Schema     → Schema 定义 + 迁移路径 + 兼容性策略
-->
```

**设计意图**：
- 无固定章节，只有 Quality Bar + 参考菜单
- Quality Bar 的核心是「半结构化、形式化表达 over 散文」，artifact 类型是常见手段而非穷举
- 笨 Agent 看到 anti-pattern 知道底线，聪明 Agent 理解原则自由发挥

#### revision 模板

```markdown
---
revision: {{N}}
date: {{TIME}}
trigger: ""  # review-feedback | discovery | scope-expansion | correction
---

# <描述性标题>

## Reason
<!-- 为什么需要这次变更？因果链的 "因"。
     说明触发来源、发现了什么问题或新需求。 -->

## Changes

### Spec Impact
<!-- spec.md 的哪些部分在逻辑上发生了变化？
     不修改 spec.md 原文件，在此记录。 -->

### Design Impact
<!-- design.md 的哪些部分变化？如无 design.md 则删除此节。 -->

### Task Impact
<!-- 对 tasks.md 的影响：新增/修改/删除了哪些任务。
     tasks.md 本身是 living document，直接更新。 -->
```

**文件命名**：`revisions/001-add-batch.md`，编号递增，描述性后缀。

**核心规则**：spec.md 和 design.md 在 Design gate 后基线不可变。所有后续变化 MUST 先创建 revision 文件，THEN 更新 tasks.md。

#### handover.md 精简

保持现有结构（Background / Git Baseline / Working Memory / Session Log），但：
- 删除所有冗长的 `@RULE` 和 `<!-- ... -->` 教学注释
- 只保留最小的格式提示（字段名 + 一行说明）
- 详细写作规则由 sspec-handover SKILL 和 HOWTO 覆盖

#### change-root 模板同步更新

- `change-root/spec.md`：同步 spec.md 的结构简化 + Design Reference 节
- `change-root/handover.md`：同步精简
- `change-root/tasks.md`：保持不变（milestone 格式不受影响）
- 不创建 `change-root/design.md`：root change 不做文件级设计，设计在 sub-change 中

### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/templates/change/spec.md` | 重写：精简结构，删除 dimension 引导，新增 Design Reference 节 |
| `src/sspec/templates/change/design.md` | **新增**：技术设计模板 |
| `src/sspec/templates/change/revision.md` | **新增**：revision 模板 |
| `src/sspec/templates/change/handover.md` | 精简：删除冗长 @RULE 注释 |
| `src/sspec/templates/change-root/spec.md` | 同步精简 + Design Reference 节 |
| `src/sspec/templates/change-root/handover.md` | 同步精简 |
| `src/sspec/templates/change/tasks.md` | 不变 |
| `src/sspec/templates/change-root/tasks.md` | 不变 |
