---
change: improve-revision-activation
---

# Design: improve-revision-activation

## Fix A — sspec-review：强制显式 feedback 分类

### 当前结构（问题所在）

```markdown
## Assess Feedback Scope

| Class   | Signal                      | Action |
|---------|-----------------------------|--------|
| Minor fix | "This variable name" ...  | fix directly |
| Amend   | "still needs validation"    | scaffold revision... |
```

分类动作完全隐式，agent 直接进入 Action，用户无从感知。

### 修改后结构

在 `## Feedback Loop` 下方，`Assess Feedback Scope` 之前，插入：

```markdown
## Feedback Classification (Mandatory First Step)

Before touching any file, output the classification:

@feedback-class: <minor-fix | amend | follow-up | supersede>
Reason: <one sentence why>

**Rule**: The single test —
> Can the original spec/design still accurately predict the post-change code?
> YES → minor-fix | NO → amend → revision required
```

然后 Assess Feedback Scope 表格保留，但每行 Action 列改为指向分类结果（"if @feedback-class == amend → ..."），明确前置依赖。

---

## Fix B — 统一判定标准 + 收紧 minor-fix

### 插入位置（所有相关 SKILL / HOWTO 顶部或判定表前）

```markdown
**Revision trigger test** (apply before classifying feedback):
> Can the original spec/design still accurately predict the post-change code?
> YES → minor-fix | NO → amend → open revision
```

### minor-fix 收紧定义

| ✅ minor-fix | ❌ 不是 minor-fix（归 amend） |
|---|---|
| 变量 / 函数命名 | 新增验收条件 |
| typo / 文案 | 新增验证 / 日志 / 错误分支 |
| 明显 bug（无行为变更） | 新增用户可见行为 |
| 已有验收边界内的边界修复 | 修改范围边界 |
| | 让原 spec 无法完整预测最终代码的任何反馈 |

这个表格插入 `sspec-review` 和 `handle-review-scope-change` 的 minor-fix 定义旁。

---

## Fix C — tasks.md Feedback Tasks 冲突修正

### 当前（冲突）

```markdown
### Feedback Tasks
Use this section for review/feedback tasks that still belong to the current change.
If accepted feedback changes scope/design, update `spec.md` first, then add the execution work here.
```

问题：`update spec.md first` 与 design SKILL "post-gate baseline 不可变" 冲突。

### 修改后

```markdown
### Feedback Tasks
Use this section for review/feedback tasks that still belong to the current change.

If accepted feedback changes scope/design:
- **Pre-gate** (spec.md not yet approved): update `spec.md` / `design.md` directly, then add tasks here.
- **Post-gate** (design baseline locked): create `revisions/NNN-*.md` FIRST, then update `tasks.md`. Do NOT edit `spec.md` / `design.md`.

If the work belongs in a new follow-up or replacement change, the agent MUST NOT put it here
unless the user has first approved that direction via `@align`.
```

---

## Fix E — 双向引用：spec.md ↔ revision ↔ tasks.md

### spec.md frontmatter：扩展 `type: revision`

`spec.md` 的 `@RULE` 注释中，`reference:` 的 type 枚举目前为：
`request | root-change | sub-change | prev-change | doc`

扩展为加入 `revision`：

```yaml
# spec.md @RULE 注释新增：
#   - source: ".sspec/changes/<change>/revisions/001-xxx.md"
#     type: "revision"
#     note: "<one-line summary of what changed>"
```

**写入时机**：agent 执行 `sspec change scaffold revision` 后，立即在 spec.md frontmatter 的 `reference:` 数组中追加一条 `type: revision` 条目。这是协议层约定，不需要 CLI 自动写入。

**不可变原则兼容**：frontmatter reference 是元数据，不是设计内容，追加 revision 指针不违反"content baseline 不可变"。

---

### tasks.md Feedback Tasks：section header 引用格式

每个 Feedback Tasks block 的 header 格式固定为：

```markdown
### Feedback Tasks (→ [001-extra-validation](./revisions/001-extra-validation.md))
- [ ] ...
- [ ] ...
```

如果一次 review 产生多个 revision（少见），每个 revision 对应一个独立的 Feedback Tasks block：

```markdown
### Feedback Tasks (→ [001-audit-log](./revisions/001-audit-log.md))
- [ ] ...

### Feedback Tasks (→ [002-error-branch](./revisions/002-error-branch.md))
- [ ] ...
```

这个格式约定写入 `tasks.md` 模板注释、`sspec-review` SKILL、`handle-review-scope-change` HOWTO。

---

### handle-review-scope-change：amend 流程加入回写步骤

当前 amend 流程（Procedure 第 2 步）结束后新增：

```
5. Cross-reference:
   a. spec.md frontmatter reference: 追加 type: revision 条目
   b. tasks.md Feedback Tasks section header 包含 → [NNN-xxx](./revisions/NNN-xxx.md) 链接
```

---

## Fix D — sspec-implement：提升 revision 触发优先级

### 当前（低优先级条款）

```markdown
| Implementation reveals design issue | Re-enter Clarify posture...; create `revisions/NNN-*.md` if spec/design already gated, then update tasks.md; `@align` if scope changes |
```

### 修改后（提升为强制规则 + 加入 trigger test）

在 `## When to Pause` 表格后，新增独立段落：

```markdown
### Post-Gate Design Changes

If during implementation you discover the accepted design needs to change:

1. **Stop** — do not implement the deviation silently
2. Apply the revision trigger test: can original spec still predict the result?
   - YES → note in memory, continue
   - NO → `@align` user, then `sspec change scaffold revision <change> --title "..."`
3. Update `tasks.md` to reflect new work
4. Resume implementation

This applies regardless of whether the change was triggered by a user comment or a self-discovered issue.
```
