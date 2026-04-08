---
name: rename-research-to-clarify
status: PLANNING
change-type: single
created: 2026-04-09T02:13:25
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

# rename-research-to-clarify

## Problem Statement

"Research" 作为第一阶段名称引导 Agent 默认行为是单方面代码调研（rg、read、翻代码），而非与用户双向对话建立共识。调研了 Superpowers (brainstorm)、OpenSpec (explore)、BMAD (discovery)、Spec Kit、Shrimp 等主流框架后确认：没有框架把第一步叫 "Research"——它们要么是对话式（brainstorm/explore/discovery）要么是产出式（直接生成 spec）。

当前 sspec-research SKILL 已在 v3.0 中加入了 "Understand & Align" 前置步骤，但 phase 名称仍为 Research，Agent 倾向跳过对话直接进入代码调查。

## Proposed Solution

### Approach

将 `Research` phase 重命名为 `Clarify`，同时厘清 Clarify 与 Align 的边界。

Clarify 的本质是正反合的认知同步过程：
- 正题（主观）：用户的真实意图——通过苏格拉底式对话提取
- 反题（客观）：代码/系统的真实状态——通过调查获取
- 合题：综合两者孕育 Problem Statement + 方向 → 流入 Design

Clarify 不是刚性阶段而是可复用的认知姿态（posture）：
- 推荐入口：新工作的第一步
- 可复用：Review 后 revision、Implement 中发现矛盾时均可重新进入

Clarify 与 Align 的关系：
- sspec-clarify = 认知模式（怎么建立理解）
- sspec-align = 通信协议（怎么和用户交互：gate/report/record）
- Clarify 使用 @align 作为工具；@align 不负责建立理解
- 当前 sspec-align §1 "Requirement Restoration" 移入 sspec-clarify

### Key Change

**Rename A: Phase 名称** — AGENTS.md lifecycle 中 `Research → sspec-research` 改为 `Clarify → sspec-clarify`，标注为 posture 而非 phase

**Rename B: SKILL 目录** — `templates/skills/sspec-research/` → `templates/skills/sspec-clarify/`

**Rewrite C: sspec-clarify SKILL** — 正反合结构（主观→客观→合题），可复用 posture，长讨论记忆管理

**Refactor D: sspec-align SKILL** — 移除 §1 Requirement Restoration（移入 Clarify），回归纯通信协议

**Update E: 引用修复** — AGENTS.md、sspec-design SKILL、requests.md 中所有 `sspec-research` 引用更新

**Update F: sspec-design Step 2** — 入口调整，承接 Clarify 产出

### Scope Summary

| File | Change |
|------|--------|
| `templates/skills/sspec-research/SKILL.md` | 重命名目录为 `sspec-clarify/`，重写内容 |
| `templates/AGENTS.md` | lifecycle: `Research` → `Clarify` (posture)，output 调整 |
| `templates/skills/sspec-align/SKILL.md` | 移除 §1 Requirement Restoration，回归纯通信协议 |
| `templates/skills/sspec-design/SKILL.md` | 引用更新 + Step 2 入口调整 |
| `templates/requests/requests.md` | 引用 `sspec-research` → `sspec-clarify` |
| `services/change_service.py` | `status-research.md` 保留（文件名，非 phase 名） |
| `builtin_tools/ask.py` | "research content" 保留（通用英语，非 phase 名） |

### Design Reference

→ 详细技术设计见 [design.md](./design.md)
