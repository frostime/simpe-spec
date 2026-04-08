# Handover: template-change-structure

**Updated**: 2026-04-08T18:09

---

## Background

重新设计 sspec 的 change 模板文件集：spec.md 精简（删除 dimension 引导）、design.md 作为一等公民新增、revision 机制引入（gate 后不可变 + 修订链）、handover.md 精简冗长注释。

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

## Working Memory (Stable)

### Key Files
- `src/sspec/templates/change/spec.md` — 重写后的 single-change spec 模板，删除了 Key Design/dimensions，新增 Design Reference 节
- `src/sspec/templates/change/design.md` — 新增模板，Quality Bar（半结构化表达 over 散文）+ 参考菜单，无固定章节
- `src/sspec/templates/change/revision.md` — 新增模板，frontmatter(revision/date/trigger) + Reason + Changes(Spec/Design/Task Impact)
- `src/sspec/templates/change/handover.md` — 精简后的 handover 模板，62→42 行
- `src/sspec/templates/change-root/spec.md` — 重写后的 root spec 模板，同步精简 + Design Reference 节
- `src/sspec/templates/change-root/handover.md` — 精简后的 root handover 模板

### Durable Memory
- [2026-04-08T18:00] [Decision] design.md Quality Bar 核心原则定为「半结构化、形式化表达 over 平铺直叙纯文本」，artifact 类型（code block/diagram/table 等）是常见手段而非穷举
- [2026-04-08T18:00] [Decision] design.md 无固定章节，只有 Quality Bar + anti-pattern + 按变更类型的参考组织方式
- [2026-04-08T18:00] [Decision] revision 模板使用编号命名 `001-xxx.md`，frontmatter 含 revision/date/trigger 字段
- [2026-04-08T18:00] [Constraint] spec.md/design.md 在 design gate 后基线不可变，变更通过 revisions/ 记录
- [2026-04-08T18:00] [VitalFinding] CLI 当前仍会创建 tasks.md（Phase 4 才改为 lazy creation），模板文件本身不受影响

## Session Log (Append-Only)

### 2026-04-08T18:09 [work-log] Phase 1 implementation complete

**Accomplished**
- 与用户经历三轮设计对齐：
  1. 初版 design.md 用固定 5 个 dimension 章节 → 用户指出不适用于非 feature 变更
  2. 改为 Quality Bar + 参考菜单 → 用户补充核心原则是「半结构化形式化表达」而非限定特定 artifact 格式
  3. 最终确认方向
- 实施 6 个模板文件（2 新增 + 4 修改）
- `uv pip install -e .` 重装通过
- 沙盒验证通过：`sspec project init` → `sspec change new` (single + root) 均正确渲染新模板

**Next**
- 用户 review 模板内容
- 确认后标记 Phase 1 DONE，推进 Phase 2: SKILL Slim-down
