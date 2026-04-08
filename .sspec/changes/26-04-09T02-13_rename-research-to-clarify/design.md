---
change: "rename-research-to-clarify"
created: 2026-04-09T02:13:25
---

# Design: rename-research-to-clarify

## 1. Conceptual Model

```
Clarify = 正反合的认知同步

  正题（主观）          反题（客观）
  用户的真实意图        代码/系统的真实状态
  苏格拉底式对话提取    调查获取
        \                /
         \              /
          合题（综合）
          Problem Statement + 方向
              ↓
          流入 Design（形式化）
```

Clarify 是 posture（姿态），不是 phase（阶段）：
- 新工作入口：完整 Clarify → Design
- Review 后 revision：mini-Clarify → revision.md
- Implement 中矛盾：暂停 → Clarify 姿态 → 回来

## 2. Clarify vs Align 边界

```
sspec-clarify                    sspec-align
─────────────                    ───────────
认知模式                          通信协议
"怎么建立理解"                    "怎么和用户交互"
                                 
正题：用户意图                    Levels: report vs gate
反题：代码现实                    How to Gate: 工具选择
合题：Problem + 方向              Records: 决策去哪
                                 Message Shape: 格式
        │                               │
        │    Clarify 使用 @align         │
        │    作为通信工具                 │
        └───────────────────────────────┘
```

迁移项：sspec-align §1 "Requirement Restoration" → sspec-clarify

## 3. sspec-clarify SKILL 结构

```
# SSPEC Clarify
  开场：正反合认知同步，posture 非 phase

## Stance
  - Socratic：苏格拉底式提取用户意图
  - Grounded：基于代码现实验证
  - Synthesizing：综合两者形成问题定义
  - No implementation：不写代码

## Workflow
  1. Subjective — 用户意图（苏格拉底式对话）
  2. Objective — 代码/系统现实（调查）
  3. Synthesis — 合题 → Problem Statement + 方向
  (1 和 2 自然交错，不强制顺序)

## Reusable Posture
  - 说明可从任何阶段重新进入
  - Review revision、Implement 矛盾等场景

## Memory Management
  - 短 Clarify（≤5 轮）：产出直接流入 spec.md
  - 长 Clarify（>10 轮/涉及调研）：
    - 调研材料 → `.sspec/tmp/clarify_<YY-MM-DDTHH-MM>_<topic>.md`
    - 命名遵循 change 时间戳格式，可排序、可 grep
    - change 创建后，将相关材料 mv 到 `reference/`
    - 关键决策 → Design 阶段写入 handover.md Durable Memory
    - 不要等到 Design 才落笔

## Exit Criteria
  双方都能说清：
  1. 问题是什么（第一性原理）
  2. 边界在哪（做什么/不做什么）
  3. 方向往哪走（不需要完整设计，够进入 Design 即可）
  4. 哪些不确定性已解决 vs 仍开放

## When to Ask
  这个 phase 本身就是对话，asking 是默认姿态
```

## 4. sspec-align SKILL 变化

```
Before                           After
──────                           ─────
§1 Requirement Restoration       (移除 → sspec-clarify)
§2 Levels                        §1 Levels        (不变)
§3 How To Gate                   §2 How To Gate   (不变)
§4 After Align — Update Records  §3 After Align   (不变)
§5 Message Shape                 §4 Message Shape (不变)
```

## 5. AGENTS.md Lifecycle 变化

```markdown
Before:
  Research → sspec-research
    output: aligned understanding, reference/ notes
    exit: alignment checkpoint

After:
  Clarify → sspec-clarify
    posture, not phase — reusable when understanding drifts
    output: Problem Statement + direction sketch, reference/ notes
    exit: ready to formalize into spec.md
```

## 6. sspec-design Step 2 入口调整

```
Before (Step 2: Explore Solutions):
  - If user has clear approach → adopt
  - If approach is open → present 1-2 candidates
  - If underlying goal unclear → probe goal first

After (Step 2: Converge Solution):
  - Clarify 已产出 Problem Statement + 方向
  - 如果有：采纳方向，形式化入 spec.md
  - 如果无（用户直接跳到 Design）：
    简短 Clarify 姿态确认方向后继续
```

## 7. 下游 SKILL 引用

| SKILL | 变化 |
|-------|------|
| sspec-implement | "发现矛盾 → step back to Clarify posture" 措辞 |
| sspec-review | Amend 路径 "re-enter Clarify posture before revision" |
| sspec-handover | 无变化（不引用 research） |
| sspec-plan | 无变化（不引用 research） |
