# Handover: sspec-vnext

**Updated**: 2026-04-08T17:37

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
| Phase 1: Template & Change Structure | (not created) | ⏳ | First priority |
| Phase 2: SKILL Slim-down | (not created) | ⏳ | Depends on Phase 1 |
| Phase 3: AGENTS.md Rewrite | (not created) | ⏳ | Depends on Phase 1+2 |
| Phase 4: CLI Adaptation | (not created) | ⏳ | Depends on Phase 1 |
| Phase 5: Integration & Self-host | (not created) | ⏳ | Depends on all |

## Working Memory (Stable)

### Key Sub-Changes
(none created yet)

### Key Files
- `src/sspec/templates/change/spec.md` — current change spec template, will be redesigned in Phase 1
- `src/sspec/templates/change/handover.md` — current handover template, will be simplified
- `src/sspec/templates/skills/sspec-design/SKILL.md` — heaviest SKILL (~200 lines), primary target for Phase 2
- `src/sspec/templates/AGENTS.md` — protocol template, will be rewritten in Phase 3
- `src/sspec/core.py` — CHANGE_TEMPLATE_FILES constant, needs update in Phase 1/4
- `src/sspec/services/` — change creation services, needs update in Phase 4

### Durable Memory (Typed, Timestamped)

- [2026-04-08T17:37] [Alignment] User confirmed: spec.md 保留命名，内涵重新定义为"变更定义"（what+why+how）
- [2026-04-08T17:37] [Alignment] User confirmed: design.md 按需创建（涉及接口/架构变更时 MUST 创建）
- [2026-04-08T17:37] [Alignment] User confirmed: revision 文件用编号命名 `001-xxx.md`，带 date/trigger/reason 结构
- [2026-04-08T17:37] [Alignment] User confirmed: CLI 最小创建 = spec.md + handover.md（handover 需要 Git Baseline 注入）
- [2026-04-08T17:37] [Alignment] User confirmed: align/handover 保留为独立 SKILL（精简），详细内容渐进披露
- [2026-04-08T17:37] [CoordinationDecision] Presentation Rules (code block / ASCII diagram / scope table / labeled items) 保持 constitution 层级，不降级
- [2026-04-08T17:37] [CoordinationDecision] Change evolution 三种动作 (amend/follow-up/supersede) 提升为 AGENTS.md 一等公民
- [2026-04-08T17:37] [Constraint] spec.md/design.md 在 design gate 后基线不可变，所有变更通过 revisions/ 记录
- [2026-04-08T17:37] [Constraint] 可预测性是所有设计决策的裁判标准——用户在实现前必须能预测代码变化

## Session Log (Append-Only)

### 2026-04-08T17:37 [coordination] Root change created + design alignment

**Accomplished**
- 与用户进行了深度讨论：sspec 定位、SKILL 繁琐问题、change 演化、spec vs design 分离、CLI 创建策略
- 参考了 GPT 的分析意见，形成综合判断
- 用户确认了 5 个关键设计决策（见 Durable Memory）
- 创建了 root change `sspec-vnext`，分支 `refactor/sspec-vnext`
- 填写了 root spec.md（5 Phase 分解）和 tasks.md

**Next**
- 用户确认 root spec 后，创建 Phase 1 sub-change 并开始实施
- Phase 1 需要先设计：新的 spec.md 模板、design.md 模板、revision 模板、精简后的 handover.md 模板

**Notes**
- 归档的 `better-spec-design` change 记录了 Presentation Rules 的由来，Phase 2 瘦身时需要参考
- 当前 `core.py` 中 `CHANGE_TEMPLATE_FILES = ['spec.md', 'tasks.md', 'handover.md']`，Phase 4 需要更新
