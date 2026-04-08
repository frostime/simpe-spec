# Handover: sspec-vnext

**Updated**: 2026-04-08T19:02

---

## Background

sspec vNext 重构：重新设计 change 文件结构（revision 机制、design.md 一等公民），瘦身全部 SKILL 到输出契约模式，重写 AGENTS.md 嵌入 constitution/alignment/evolution 协议，CLI 适配最小创建，最终自举验证。

## Git Baseline (Immutable)

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `refactor/sspec-vnext`
- HEAD: `5ddb74b6f622460d142b5d43fd35f1ca8ba4ddc4`
- Worktree: `clean`
- Status Snapshot: raw `git status --short --branch` output

```text
## refactor/sspec-vnext
```

## Sub-Change Status (Volatile Snapshot)

| Phase | Sub-Change | Status | Notes |
|-------|------------|--------|-------|
| Phase 1: Template & Change Structure | `26-04-08T17-47_template-change-structure` | DONE | 6 个模板文件已完成 |
| Phase 2: SKILL Slim-down | `26-04-08T18-15_skill-slimdown` | REVIEW | 7 SKILL + 2 HOWTO 已实施 |
| Phase 3: AGENTS.md Rewrite | (not created) | ⏳ | 依赖 Phase 1 + 2 |
| Phase 4: CLI Adaptation | (not created) | ⏳ | 依赖 Phase 1 |
| Phase 5: Integration & Self-host | (not created) | ⏳ | 依赖全部 |

## Working Memory (Stable)

### Key Sub-Changes
- `changes/26-04-08T17-47_template-change-structure/` — Phase 1 DONE: 模板文件重构
- `changes/26-04-08T18-15_skill-slimdown/` — Phase 2 REVIEW: SKILL 瘦身

### Key Files
- `src/sspec/templates/change/` — single-change 模板目录，Phase 1 主要修改区
- `src/sspec/templates/change-root/` — root-change 模板目录，Phase 1 同步修改
- `src/sspec/templates/skills/sspec-design/SKILL.md` — Phase 2 主要目标，当前 ~200 行
- `src/sspec/templates/AGENTS.md` — Phase 3 主要目标
- `src/sspec/core.py` — Phase 4 需更新 CHANGE_TEMPLATE_FILES 常量

### Durable Memory

- [2026-04-08T17:37] [Alignment] User confirmed: spec.md 保留命名，内涵重新定义为"变更定义"（what+why+how）
- [2026-04-08T17:37] [Alignment] User confirmed: design.md 按需创建（涉及接口/架构变更时 MUST 创建）
- [2026-04-08T17:37] [Alignment] User confirmed: revision 文件用编号命名 `001-xxx.md`，带 date/trigger/reason 结构
- [2026-04-08T17:37] [Alignment] User confirmed: CLI 最小创建 = spec.md + handover.md（handover 需要 Git Baseline 注入）
- [2026-04-08T17:37] [Alignment] User confirmed: align/handover 保留为独立 SKILL（精简），详细内容渐进披露
- [2026-04-08T17:37] [CoordinationDecision] Presentation Rules 保持 constitution 层级，不降级
- [2026-04-08T17:37] [CoordinationDecision] Change evolution 三种动作 (amend/follow-up/supersede) 提升为 AGENTS.md 一等公民
- [2026-04-08T17:37] [Constraint] spec.md/design.md 在 design gate 后基线不可变，所有变更通过 revisions/ 记录
- [2026-04-08T17:37] [Constraint] 可预测性是所有设计决策的裁判标准
- [2026-04-08T18:09] [CoordinationDecision] design.md Quality Bar 核心原则：「半结构化、形式化表达 over 平铺直叙纯文本」，artifact 类型是手段非穷举（用户修订）
- [2026-04-08T18:09] [CrossChangeFinding] Phase 1 模板不包含 CLI 行为变更（tasks.md lazy creation），该变更属于 Phase 4

- [2026-04-08T19:02] [CoordinationDecision] Examples 文件更新延后到 Phase 5 或 follow-up，不在 Phase 2 处理
- [2026-04-08T19:02] [CrossChangeFinding] SKILL 修改后模板注释中引用的 SKILL 内容已变更，Phase 3 AGENTS.md 重写时需确保一致

## Session Log (Append-Only)

### 2026-04-08T19:02 [coordination] Phase 1 DONE + Phase 2 complete, pending review

**Accomplished**
- Phase 1 confirmed DONE by user
- Created Phase 2 sub-change `skill-slimdown`, bidirectional references established
- First implementation attempt rejected: must analyze each SKILL's strengths before rewriting
- Completed per-SKILL analysis (shine points / problems / keep-cut-add plan)
- User provided 3 critical corrections: Research alignment at beginning, Design solution discovery early, Handover preserves causality
- Implemented all 7 SKILLs + 2 HOWTOs. Total: 819→571 lines (-30%)
- Reinstall + sandbox verification passed

**Next**
- User reviews Phase 2 SKILL content
- After confirmation, create Phase 3 sub-change (AGENTS.md Rewrite)

### 2026-04-08T18:09 [coordination] Phase 1 implementation complete, pending review

**Accomplished**
- 创建 Phase 1 sub-change `template-change-structure`，双向引用已建立
- Phase 1 经历三轮设计对齐后实施完毕：
  - spec.md: 删除 Key Design/dimensions，新增 Design Reference 节
  - design.md: 新增，Quality Bar（半结构化表达原则）+ 参考菜单，无固定章节
  - revision.md: 新增，frontmatter(revision/date/trigger) + Reason + Changes 结构
  - handover.md: 精简冗长 @RULE 注释
  - change-root/: 同步更新 spec.md + handover.md
- 沙盒验证通过（init + change new single + change new root）

**Next**
- 等用户 review Phase 1 模板
- 确认后标记 Phase 1 DONE，创建 Phase 2 sub-change (SKILL Slim-down)

### 2026-04-08T17:37 [coordination] Root change created + design alignment

**Accomplished**
- 与用户深度讨论 sspec 定位、SKILL 繁琐问题、change 演化、spec vs design 分离、CLI 创建策略
- 参考了 GPT 分析意见，形成综合判断
- 用户确认 5 个关键设计决策（见 Durable Memory）
- 创建 root change `sspec-vnext`，分支 `refactor/sspec-vnext`
- 填写 root spec.md（5 Phase 分解）和 tasks.md

**Next**
- 创建 Phase 1 sub-change 并开始实施
