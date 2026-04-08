---
name: skill-slimdown
status: DONE
change-type: sub
created: 2026-04-08 18:15:00
reference:
  - source: ".sspec/changes/26-04-08T17-37_sspec-vnext"
    type: "root-change"
    note: "Phase 2: SKILL Slim-down"
---

# skill-slimdown

## Problem Statement

当前 7 个 workflow SKILL 总计 ~903 行。大量篇幅教 Agent "怎么做"（选维度、写格式、填表步骤）而非规定"必须交付什么"。Agent 自身能力被压扁为填表机器，且内容与 Phase 1 的新模板结构不匹配（spec.md 已无 Key Design 节，design.md 是独立文件）。

## Proposed Solution

### Approach

将每个 SKILL 瘦身为三部分：**Output Contract** + **Anti-patterns** + **References**。方法论性质的内容（如 dimension 选择、写作指导）保留在 HOWTO 中按需加载。同时更新 sspec-design 的 examples 文件以匹配新 spec.md + design.md 结构。

### Key Change

**Refactor A: 5 个 Phase SKILL 瘦身** — research / design / plan / implement / review 每个压缩到 ~40-60 行，只保留输出契约、gate 条件、anti-patterns、references。

**Refactor B: sspec-design examples 更新** — 现有 4 个 examples 文件引用旧的 spec.md `Key Design` 结构，需更新为新的 spec.md + design.md 分离结构。

**Refactor C: align / handover SKILL 精简** — 保留为独立 SKILL，但精简冗余内容，作为渐进披露的详细参考。

### Scope Summary

| File | Change |
|------|--------|
| `templates/skills/sspec-research/SKILL.md` | 瘦身 95→~40 行 |
| `templates/skills/sspec-design/SKILL.md` | 瘦身 205→~60 行 |
| `templates/skills/sspec-design/examples-feature.md` | 更新为新 spec+design 结构 |
| `templates/skills/sspec-design/examples-refactor.md` | 更新为新结构 |
| `templates/skills/sspec-design/examples-docs.md` | 更新为新结构 |
| `templates/skills/sspec-design/examples-root.md` | 更新为新结构 |
| `templates/skills/sspec-plan/SKILL.md` | 瘦身 116→~40 行 |
| `templates/skills/sspec-implement/SKILL.md` | 瘦身 96→~40 行 |
| `templates/skills/sspec-review/SKILL.md` | 瘦身 113→~50 行 |
| `templates/skills/sspec-align/SKILL.md` | 精简 75→~50 行 |
| `templates/skills/sspec-handover/SKILL.md` | 精简 119→~60 行 |
