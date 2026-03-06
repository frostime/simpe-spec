# Handover: rename-ask

**Updated**: 2026-03-06T22:50

---

## Background
`@ask` → `@align` 全局重命名。将协议指令和 SKILL 名称从 `@ask`/`sspec-ask` 更新为 `@align`/`sspec-align`，以消除与 `sspec ask` CLI 命令的歧义，并更准确表达该操作的目标：Agent 与用户对齐。

## Working Memory (Stable)
<!-- Curated, long-lived context. Survives context compression and session boundaries.
If something becomes obsolete, mark it as obsolete with a timestamp instead of deleting silently. -->

### Key Files
- `src/sspec/templates/AGENTS.md` - 主协议模板，包含 Section 3 "Alignment (@align)"
- `src/sspec/templates/skills/sspec-align/SKILL.md` - 新升级的 sspec-align SKILL（原 sspec-ask）
- `.github/skills/sspec-ask/SKILL.md` - 开发时 SKILL，内容已更新但目录未重命名

### Decisions (Timestamped)
- [2026-03-06T16:30] **保持 `sspec ask` CLI 命令不变** — 只是协议指令和 SKILL 名称变化， CLI 不冨
- [2026-03-06T16:30] **`.github/skills/sspec-ask/` 目录保持不重命名** — dev 目录用户跳过了重命名步骤；内容已更新为 sspec-align

### Notes (Timestamped)
- [2026-03-06T16:35] `sspec project update` 的孤儿检测已验证正常工作——运行时自动删除 `sspec-ask` 并安装 `sspec-align`
- [2026-03-06T18:40] `src/sspec/templates/AGENTS.md` 经过无损压缩后长度为 7960 chars；核心协议层信息保持不变。
- [2026-03-06T19:00] `src/sspec/templates/skills/sspec-align/SKILL.md` 压缩至 5038 chars / 140 lines；保留触发条件、通道选择、记录落点、`@force-end-align` 与原子 `sspec ask` 工作流。

## Session Log (Append-Only)
<!-- Newest entry first. Each entry is an atomic batch (one cohesive work record).

Header format:
### 2026-03-06T20:39 [work-log] <short title>

Tags are freeform but must be readable. Examples: work-log, user-feedback, argue, risk.
Any user interaction (feedback, @align, @argue) MUST start a new log entry. -->

### 2026-03-06T22:50 [work-log] Mark rename-ask done and prepare commit

**Accomplished**
- Marked the request and change as DONE after user acceptance
- Prepared commit scope for the rename + align-rule update
- Kept `.env` out of the intended commit because it is an environment file

**Next**
- Create final git commit with repository commit style

### 2026-03-06T19:00 [work-log] Compress sspec-align without losing core semantics

**Accomplished**
- Replaced bulky per-phase YAML examples with one shared `sspec ask` skeleton + per-phase inclusion bullets
- Clarified phase patterns are guides, not literal presets for built-in `question` tools
- Tightened `@force-end-align`: when the agent believes work is done and would otherwise stop, ask one last user-facing question; prefer built-in `question`
- Reduced template `sspec-align` from about 6771 chars / 216 lines to 5038 chars / 140 lines
- Re-ran `sspec project update` in repo root and `tmp/quicktest_sspec` to sync the compressed skill

**Next**
- User decides whether the compressed `sspec-align` is the right balance of brevity vs guidance

### 2026-03-06T18:40 [work-log] Clarify template usage + atomic ask workflow

**Accomplished**
- Clarified `sspec-align` phase-gate examples are structure guides for `sspec ask`, not literal presets for built-in question tools
- Added explicit atomic workflow guidance: agents should usually do `sspec ask create` → edit file → `sspec ask prompt` in one work unit
- Shortened `src/sspec/templates/AGENTS.md` from 8245 to 7960 chars without dropping protocol meaning
- Re-ran `sspec project update` in repo root and `tmp/quicktest_sspec` to sync template changes
- `uv pip install -e .` hit a transient network timeout fetching build requirements, but existing editable environment still allowed update verification to complete

**Next**
- User reviews the current staged+unstaged doc wording and decides whether to restage for commit

### 2026-03-06T18:15 [work-log] Finish verification after align-rule adjustments

**Accomplished**
- Reinstalled editable package with `uv pip install -e .`
- Ran focused test suite: `uv run pytest tests/test_project_update_service.py` → 13 passed
- Ran `uv run sspec project update` in repo root and `tmp/quicktest_sspec`; both updated `sspec-align` + root `AGENTS.md` cleanly
- Confirmed stale self-hosted `.sspec/skills/sspec-ask/` directory is removed

**Next**
- User review / decide whether to restage files for a clean commit diff

### 2026-03-06T18:05 [work-log] Reconcile Plan gate + promote force-end-align

**Accomplished**
- Kept `Plan` as lightweight align in protocol semantics; updated `sspec-align` SKILL to escalate only when plan decisions need durable trace
- Promoted `@force-end-align` from optional footnote to a strong credit-host directive in template + dev protocol
- Removed weak rename regression test and stale self-hosted `.sspec/skills/sspec-ask/SKILL.md` residue

**Next**
- Reinstall editable package, run `sspec project update`, and verify updated self-hosted skill/docs
- Run focused verification for rename-ask change

### 2026-03-06T17:10 [user-feedback] Feedback round: validation, regression test, SKILL rewrite

**Accomplished**
- Verified: `tmp/quicktest_sspec` (had stale `sspec-ask`) ran clean `project update` — orphan removed, `sspec-align` created, meta updated
- Added regression test `test_skill_rename_full_cycle` in `tests/test_project_update_service.py`
- Fixed remaining `sspec-ask` in dev AGENTS.md directory structure comment
- Rewrote `sspec-align` SKILL v9 with trigger-first structure (Mandatory/Optional/Channel/Records/Templates)
- Reframed End-of-turn behavior into `@force-end-align` directive
- 276 tests pass

**Next**
- User reviews and approves → archive change
- Optional: rename `.github/skills/sspec-ask/` dir to `sspec-align/` + update VS Code agent config skill name reference
