# Handover: generalize-align-interaction

**Updated**: 2026-03-17T01:40

---

## Background

将 SSPEC 的交互层从 Copilot-specific 改为 platform-agnostic。核心改动：@align 简化为 report/gate 两级、删除 @force-end-align、`sspec ask` 退出模板主流程。

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
- `src/sspec/templates/skills/sspec-design/SKILL.md` - 设计阶段保持 hard gate，并明确 gate 的执行方式
- `src/sspec/templates/skills/sspec-implement/SKILL.md` - 实现完成后保持 hard gate，等待用户 review
- `src/sspec/templates/skills/sspec-plan/SKILL.md` - 计划阶段改成 report，不再是 hard gate

### Durable Memory (Typed, Timestamped)
- [2026-03-17T01:00] [Decision] @align 从单一 mandatory 改为 report/gate 两级。report = 输出摘要继续执行；gate = 停下来等用户回复。
- [2026-03-17T01:00] [Decision] 删除 @force-end-align 概念，仅服务于 Copilot 按次计费场景。
- [2026-03-17T01:00] [Decision] sspec ask 从主交互通道降级为可选归档工具。日常交互走平台原生 question 工具或对话。
- [2026-03-17T01:00] [Alignment] 用户明确指出：不必按 SKILL 中面向 feature code 的 spec 写法来写本次 spec，按合适的方式填写即可。
- [2026-03-17T01:00] [VitalFinding] gate 的实现只有两种可能：用 question 工具（同步不结束 turn）或结束 turn 等用户回复。没有"短暂等待自动继续"的中间态。
- [2026-03-17T01:10] [Alignment] 用户反馈：Design 和 Implement exit 必须是 hard gate；sspec ask 可以降级到 sspec tool 里而非完全删除；无关 HOWTO 直接删除不保留。
- [2026-03-17T01:10] [Decision] Design/Implement exit = gate (hard stop)；Plan exit = report (继续执行)。
- [2026-03-17T01:10] [Decision] `sspec ask` 不再出现在模板主流程中；是否正式迁移到 `sspec tool ask` 留作后续兼容性 change。
- [2026-03-17T01:10] [Decision] 删除 HOWTO: force-end-align, use-sspec-ask, write-sspec-ask。
- [2026-03-17T01:26] [VerificationShortcut] 运行 `uv run sspec project update && uv run sspec howto list` 可快速验证模板同步和 HOWTO 删除结果。
- [2026-03-17T01:38] [Alignment] 用户 review 反馈：`question`-like 工具应只承载短问题，复杂上下文先走普通输出；并要求恢复 `sspec tool ask` fallback，说明参考 `sspec tool ask --prompt`。
- [2026-03-17T01:38] [Decision] 当前 change 继续进行，不新开 change；先完成 align 规则修正并单独提交，再实现 `sspec tool ask`。
- [2026-03-17T01:40] [Decision] `question`-like 工具使用规则明确为：摘要/参考信息先走普通输出，工具 payload 只保留最终短问句。

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

### 2026-03-17T01:26 [work-log] Implemented template and HOWTO cleanup

**Accomplished**
- 重写 `src/sspec/templates/AGENTS.md` 的 Alignment 部分：改为 report/gate 两级，移除 `sspec ask` 与 `@force-end-align`
- 重写 `src/sspec/templates/skills/sspec-align/SKILL.md`，并同步更新 `sspec-design`、`sspec-implement`、`sspec-plan`、`sspec-research`
- 删除 `src/sspec/howto/force-end-align.md`、`src/sspec/howto/use-sspec-ask.md`、`src/sspec/howto/write-sspec-ask.md`
- 更新 `src/sspec/howto/use-sspec-cli.md` 与 `src/sspec/commands/change.py` 的旧提示文案
- 运行 `uv pip install -e .`、`uv run sspec project update`、`uv run sspec howto list` 完成同步验证

**Next**
- 等待用户 review 本轮变更
- 如果用户仍希望把 `sspec ask` CLI 正式迁移到 `sspec tool ask`，再拆分后续 change 处理兼容迁移

### 2026-03-17T01:38 [user-feedback] Review amendments accepted into current change

**Accomplished**
- 用户确认模板层方向，但要求补充 question-tool 使用规则：长上下文先用普通输出，再用短 question
- 用户要求不要把 ask 只停留在“退出主流程”，而是恢复为 `sspec tool ask` fallback，并在 `--prompt` 用法中说明
- 用户明确执行顺序：先完成第 1 项并提交，再继续做 tool ask

**Next**
- 先修改 `AGENTS.md` 与 `sspec-align`，把 question-like 工具的上下文/提问边界写清楚
- 完成后按用户要求做一次 git commit，再进入 `sspec tool ask` 实现

### 2026-03-17T01:40 [work-log] Tightened question-tool guidance

**Accomplished**
- 更新 `src/sspec/templates/AGENTS.md`：要求先在普通输出里提供汇总/上下文/参考，再用 `question`-like 工具承载短问题
- 更新 `src/sspec/templates/skills/sspec-align/SKILL.md`：明确 question-tool payload 只放 concise ask，不塞长上下文
- 运行 `uv pip install -e . && uv run sspec project update`，同步 root `AGENTS.md` 与 `.sspec/skills/sspec-align/SKILL.md`

**Next**
- 按用户要求先提交这一小轮对齐规则改动
- 提交后继续实现 `sspec tool ask` 与相关文档
