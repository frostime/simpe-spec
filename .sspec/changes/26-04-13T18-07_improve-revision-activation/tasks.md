---
change: "improve-revision-activation"
updated: ""
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: 模板修改 ⏳

- [x] `src/sspec/templates/skills/sspec-review/SKILL.md` — Fix A + Fix B + Fix E: 插入强制 @feedback-class 分类步骤；加 revision trigger test + 收紧 minor-fix 定义（含对照表）；amend 路径末尾加回写引用步骤
- [x] `src/sspec/templates/skills/sspec-implement/SKILL.md` — Fix B + Fix D: 加 revision trigger test；新增 `### Post-Gate Design Changes` 独立段落
- [x] `src/sspec/templates/change/tasks.md` — Fix C + Fix E: 修正 Feedback Tasks 注释区分 pre/post-gate；Feedback Tasks header 改为含 revision 相对链接的固定格式
- [x] `src/sspec/howto/handle-review-scope-change.md` — Fix B + Fix E: 在 Quick Classifier 表格前加 revision trigger test；Procedure 末尾加回写引用步骤
- [x] `src/sspec/templates/change/spec.md` — Fix E: `@RULE` 注释 reference type 枚举增加 `revision`

**Verification**: 读每个改后的文件，确认无语义冲突，minor-fix 收紧定义在 review + HOWTO 一致。

### Phase 2: 同步 ⏳

- [ ] `uv pip install -e .` — 重装，确保模板缓存更新
- [ ] `uv run sspec project update` — 同步 self-hosted copies（`.github/`, `.claude/`, `.sspec/`）

**Verification**: diff `.sspec/skills/sspec-review/SKILL.md` 与 `src/sspec/templates/skills/sspec-review/SKILL.md` 一致。

---

## Progress
<!-- @REPLACE -->

**Overall**: 0%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1: 模板修改 (5 files) | 0% | ⏳ |
| Phase 2: 同步 | 0% | ⏳ |

**Recent**:
- (none yet)
