# Handover: skill-slimdown

**Updated**: 2026-04-08T19:02

---

## Background

Phase 2 of sspec-vnext: 将所有 workflow SKILL 瘦身为输出契约模式，同时保留经过多轮迭代验证的核心规则和闪光点。新增 Research 阶段的理解对齐、Design 阶段的方案探索、全流程的 revision 机制引用。

## Git Baseline (Immutable)

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `refactor/sspec-vnext`
- HEAD: `0fbb7124a245d67357a955a5730e0fbe1a9079a4`
- Worktree: `dirty`

## Working Memory (Stable)

### Key Files
- `src/sspec/templates/skills/sspec-research/SKILL.md` — v3.0.0, 82 lines. Added alignment checkpoint at beginning
- `src/sspec/templates/skills/sspec-design/SKILL.md` — v5.0.0, 116 lines. Biggest change: deleted dimensions, added solution discovery + design.md workflow + revision mechanism
- `src/sspec/templates/skills/sspec-plan/SKILL.md` — v3.0.0, 63 lines. Output contract model
- `src/sspec/templates/skills/sspec-implement/SKILL.md` — v3.0.0, 59 lines. Preserved "When to Pause" table
- `src/sspec/templates/skills/sspec-review/SKILL.md` — v3.0.0, 73 lines. Merged rejection protocol into scope table
- `src/sspec/templates/skills/sspec-align/SKILL.md` — v10.0.0, 87 lines. Added Requirement Restoration section
- `src/sspec/templates/skills/sspec-handover/SKILL.md` — v4.0.0, 91 lines. Emphasized causal/temporal preservation
- `src/sspec/howto/handle-review-scope-change.md` — added revision protocol for post-gate amends
- `src/sspec/howto/resume-change.md` — added revisions/ and design.md to read order

### Durable Memory
- [2026-04-08T19:00] [Decision] Research alignment is the BEGINNING of the phase, not an exit checkpoint — the whole point of Research is understanding + confirming understanding with user
- [2026-04-08T19:00] [Decision] Design solution discovery happens BEFORE filling spec.md — lightweight discussion to avoid writing a full spec only to discover wrong direction
- [2026-04-08T19:00] [Decision] Handover must preserve causal/temporal relationships — the reader must understand not just current state but how/why we got here
- [2026-04-08T19:00] [Decision] write-dim-* HOWTOs (7 个) 保留不变 — 从"SKILL 流程中的必选步骤"降级为"Agent 按需查阅的写作参考"
- [2026-04-08T19:00] [Constraint] SKILL 改动必须逐个分析闪光点，保留经过多轮迭代验证的核心规则，不能随意全部重写
- [2026-04-08T19:00] [VitalFinding] examples 文件（4 个 design examples + 1 个 plan examples）未在本 phase 更新，需后续处理

## Session Log (Append-Only)

### 2026-04-08T19:02 [work-log] All 7 SKILLs + 2 HOWTOs implemented

**Accomplished**
- 第一次尝试被用户打回：不能随意重写，必须逐个分析闪光点、构思具体改动
- 完成逐个 SKILL 分析：列出每个 SKILL 的闪光点、问题、保留/删除/新增方案
- 用户反馈三个关键修正：Research 对齐放开头、Design solution discovery 放前面、Handover 强调因果时间
- 实施全部 7 个 SKILL + 2 个 HOWTO 更新
- 安装验证通过，沙盒测试通过

**Next**
- 用户 review SKILL 内容
- 确认后标记 Phase 2 DONE
- Examples 文件更新延后处理（可在 Phase 5 或 follow-up 中）
- 推进 Phase 3: AGENTS.md Rewrite
