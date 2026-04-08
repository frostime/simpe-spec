---
name: sspec-vnext
status: PLANNING
type: ""
change-type: root
created: 2026-04-08 17:37:48
reference:
  - source: ".sspec/changes/26-04-08T17-47_template-change-structure"
    type: "sub-change"
    note: "Phase 1: Template & Change Structure"
  - source: ".sspec/changes/26-04-08T18-15_skill-slimdown"
    type: "sub-change"
    note: "Phase 2: SKILL Slim-down"
---

# sspec-vnext

## A. Problem Statement

sspec 的核心理念是 **Human-led, agent-accelerated** —— 人类在代码落地前就能预测结果，保持对项目的掌控。但当前实现与理念之间存在系统性摩擦：

1. **SKILL 过度规定**：当前 9 个 SKILL 总计 ~800 行，大量篇幅在教 Agent "怎么写"而非规定"必须交付什么"。Agent 自身能力被压扁，变成填表机器。
2. **Change 不支持演化**：现有 change 模型假定需求一开始就是 well-defined 的。实际中频繁出现实现后才发现路线偏差、范围变化的情况，处理方式丑陋（在 spec.md 里硬改/临时新建 change）且丢失因果链。
3. **spec.md 职责过重**：同时承担"规格/边界"和"技术设计"，语义混淆。复杂变更中技术设计淹没在 spec 里，用户难以独立审查架构决策。
4. **对齐机制不足**：`sspec-align` 定义了 report/gate 的机制调度，但未指导对齐过程本身——如何还原需求、消除不确定性、让用户在实现前建立正确预期。
5. **CLI 创建过多空壳文件**：`change new` 一次创建 spec/tasks/handover 三个文件，在 Design 阶段 tasks.md 和 handover.md 是纯噪音。

## B. Proposed Solution

### Overall Approach

分 5 个阶段（Phase）渐进交付，按依赖顺序执行。核心原则：

- **Constitution > Stage Contract > Optional Lens** —— 三层规则模型
- **Immutable baseline + revision chain** —— 设计文档 gate 后不可变，演化通过 revision 文件记录
- **Predictability-first** —— 可预测性是所有设计决策的裁判标准

### Phase Overview

Phase 1: Template & Change Structure
  ├── Phase 2: SKILL Slim-down (depends on Phase 1)
  ├── Phase 3: AGENTS.md Rewrite (depends on Phase 1, Phase 2)
  └── Phase 4: CLI Adaptation (depends on Phase 1)
Phase 5: Integration & Self-host (depends on all)

| Phase | Goal | Depends On | Scope |
|-------|------|-----------|-------|
| Phase 1: Template & Change Structure | 重新定义 change 文件结构：spec.md 精简、design.md 一等公民、revision 机制、handover 精简 | — | `src/sspec/templates/change/`, `templates/change-root/`, `core.py` |
| Phase 2: SKILL Slim-down | 所有 Phase SKILL 瘦身为输出契约 + anti-patterns + refs；align/handover 降级为精简 SKILL | Phase 1 | `src/sspec/templates/skills/sspec-*/` |
| Phase 3: AGENTS.md Rewrite | 重写 AGENTS.md 模板：嵌入 constitution、change evolution 协议、alignment 协议 | Phase 1, 2 | `src/sspec/templates/AGENTS.md` |
| Phase 4: CLI Adaptation | `change new` 最小创建（spec.md + handover.md）；design.md / tasks.md lazy creation；revision 相关 CLI 命令 | Phase 1 | `src/sspec/commands/`, `src/sspec/services/` |
| Phase 5: Integration & Self-host | 自举验证：用新模板更新本项目 `.sspec/`；端到端测试 | All | `.sspec/`, `tests/` |

Coordination Notes:
- Phase 1 是基石，定义了新文件结构，所有后续 Phase 依赖它
- Phase 2 和 Phase 4 可以并行开发（2 改模板内容，4 改 CLI 逻辑）
- Phase 3 必须等 1+2 完成，因为 AGENTS.md 引用 SKILL 和 change 结构
- Phase 5 是验收阶段，所有 Phase 完成后才能执行

### Key Design Decisions

**Decision 1: spec.md baseline immutability**
spec.md 和 design.md 在 Design gate 通过后，基线内容不再修改。所有后续的范围/设计变更通过 `revisions/NNN-description.md` 记录。这保证了因果链可追溯，防止 Agent 无声篡改已审批的设计。

**Decision 2: design.md 一等公民，按需创建**
不是所有 change 都需要 design.md。规则：当变更涉及新接口定义、数据模型变更、架构逻辑改动时，MUST 创建 design.md。简单 bugfix/文案修改可以只用 spec.md。design.md 在 Design 阶段由 Agent 判断是否创建，CLI 不预创建。

**Decision 3: CLI 最小创建 = spec.md + handover.md**
handover.md 保留预创建，因为它包含 Git Baseline 等需要 CLI 在创建时注入的模板变量。tasks.md 和 design.md 由 Agent 在对应阶段创建。

**Decision 4: SKILL 三层规则模型**
- Layer 1 (Constitution): AGENTS.md 正文 — 不可变原则（可预测性底线、gate 规则、revision 规则）
- Layer 2 (Stage Contract): Phase SKILL — 每阶段的输出契约 + anti-patterns
- Layer 3 (Optional Lens): HOWTO — 按需加载的详细指导（design dimensions, 写作指导等）

**Decision 5: Presentation Rules 保持为 Constitution**
typed code block、ASCII diagram、Scope Summary Table、labeled items 这四条规则是可预测性的底线保障，不降级到 HOWTO。在 AGENTS.md constitution 层和 Design SKILL 中同时强调。

**Decision 6: Change evolution 三种动作**
- amend: 当前 change 还成立，通过 revision 记录范围/设计修订
- follow-up: 当前 change 已独立成立，新增后续 change（`prev-change` 引用）
- supersede: 当前路线错误，旧 change → BLOCKED，新 change 接管
