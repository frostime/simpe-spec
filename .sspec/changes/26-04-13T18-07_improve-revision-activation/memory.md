# Memory: improve-revision-activation

**Updated**: 2026-04-13T18:11

## Git Baseline (Immutable)

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `main`
- HEAD: `77dc90b09be3dc806893847385a32661b769f341`
- Worktree: clean

```text
## main...origin/main [ahead 2]
```

## State

REVIEW — 所有任务完成，同步验证通过，等待用户验收。

## Key Files

- `src/sspec/templates/skills/sspec-review/SKILL.md` — 主战场，Fix A + B
- `src/sspec/templates/skills/sspec-implement/SKILL.md` — Fix B + D
- `src/sspec/templates/change/tasks.md` — Fix C（冲突修正）
- `src/sspec/howto/handle-review-scope-change.md` — Fix B

## Knowledge

- [2026-04-13T18:07] Decision: 变更范围仅限模板文件，不改 Python 代码
- [2026-04-13T18:07] Decision: 主战场在 sspec-review（Fix A），其他文件是配套收紧
- [2026-04-13T18:07] Gotcha: tasks.md 模板的冲突（Fix C）是 P0 bug，pre/post gate 路径必须分开写
- [2026-04-13T18:07] Decision: revision trigger test 用统一一句话注入所有相关位置，而不是多套不同规则
- [2026-04-13T18:11] Rejected: design-baseline: locked frontmatter 字段 — status + revisions/ 目录是否非空已足够判断 gate 状态，行为问题用数据字段解决不了
- [2026-04-13T18:11] Rejected: amend tasks 内聚到 revision 文件 — 架构价值有限但需要改 Python（parse_change 聚合逻辑），留作 follow-up
- [2026-04-13T18:11] Decision: Fix E 双向引用（spec.md frontmatter type:revision + tasks.md header 相对链接），纯模板/协议层，不改 Python，折入本 change

## Milestones

- [2026-04-13T18:11] 创建 change，填写 spec + design + tasks，等待用户 design gate
