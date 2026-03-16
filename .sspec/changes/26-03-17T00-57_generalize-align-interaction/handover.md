# Handover: generalize-align-interaction

**Updated**: 2026-03-17T01:05

---

## Background

将 SSPEC 的交互层从 Copilot-specific 改为 platform-agnostic。核心改动：@align 简化为 report/gate 两级、删除 @force-end-align、sspec ask 降级为可选归档工具。

## Git Baseline (Immutable)
<!-- Captured during `sspec change new` before any change files are written.
This section records the change starting point in git and must not be edited or refreshed later. -->

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `main`
- HEAD: `6347f5cdd59dd224728f4f698e1ea87a9373c39c`
- Worktree: `clean`
- Status Snapshot: raw `git status --short --branch` output

```text
## main...origin/main
```

## Working Memory (Stable)
<!-- Curated, long-lived context. Survives context compression and session boundaries.
If something becomes obsolete, mark it as obsolete with a timestamp instead of deleting silently. -->

### Key Files
- `src/sspec/templates/AGENTS.md` - 主模板，§3 Alignment 是改动核心
- `src/sspec/templates/skills/sspec-align/SKILL.md` - @align 的完整规则，需要重写
- `src/sspec/templates/skills/sspec-design/SKILL.md` - exit 段需从 mandatory gate 改为 report
- `src/sspec/templates/skills/sspec-implement/SKILL.md` - 同上
- `src/sspec/templates/skills/sspec-plan/SKILL.md` - 同上

### Durable Memory (Typed, Timestamped)
- [2026-03-17T01:00] [Decision] @align 从单一 mandatory 改为 report/gate 两级。report = 输出摘要继续执行；gate = 停下来等用户回复。
- [2026-03-17T01:00] [Decision] 删除 @force-end-align 概念，仅服务于 Copilot 按次计费场景。
- [2026-03-17T01:00] [Decision] sspec ask 从主交互通道降级为可选归档工具。日常交互走平台原生 question 工具或对话。
- [2026-03-17T01:00] [Alignment] 用户明确指出：不必按 SKILL 中面向 feature code 的 spec 写法来写本次 spec，按合适的方式填写即可。
- [2026-03-17T01:00] [VitalFinding] gate 的实现只有两种可能：用 question 工具（同步不结束 turn）或结束 turn 等用户回复。没有"短暂等待自动继续"的中间态。
- [2026-03-17T01:10] [Alignment] 用户反馈：Design 和 Implement exit 必须是 hard gate；sspec ask 可以降级到 sspec tool 里而非完全删除；无关 HOWTO 直接删除不保留。
- [2026-03-17T01:10] [Decision] Design/Implement exit = gate (hard stop)；Plan exit = report (继续执行)。
- [2026-03-17T01:10] [Decision] sspec ask 降级为 builtin tool (`sspec tool ask`)，不在模板主流程中出现。
- [2026-03-17T01:10] [Decision] 删除 HOWTO: force-end-align, use-sspec-ask, write-sspec-ask。

## Session Log (Append-Only)
<!-- Newest entry first. Each entry is an atomic batch (one cohesive work record).

Header format:
### 2026-03-06T20:39 [work-log] <short title>

Tags are freeform but must be readable. Examples: work-log, user-feedback, argue, risk.
Any user interaction (feedback, @align, @argue) MUST start a new log entry. -->

### 2026-03-17T01:05 [work-log] Design spec.md filled, awaiting alignment

**Accomplished**
- 全面扫描了 SSPEC 项目：AGENTS.md 模板、全部 7 个 phase SKILL、18 个 HOWTO、sspec ask CLI 实现
- 识别出 8 个 Copilot-specific 设计模式并按适配度评级
- 与用户讨论通用化方案，经过两轮迭代确定最终设计方向
- 创建 change，填写 spec.md（5 个 Change Item: A-E）

**Next**
- 等待用户对 spec.md 设计的确认/反馈
- 确认后进入 Plan 阶段，拆分 tasks.md
