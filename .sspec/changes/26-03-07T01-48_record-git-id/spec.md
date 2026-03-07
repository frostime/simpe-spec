---
name: record-git-id
status: DONE
type: ''
change-type: single
created: 2026-03-07 01:48:15
reference:
- source: .sspec/requests/26-03-07T01-04_record-git-id.md
  type: request
  note: Linked from request
---
<!-- @RULE: Frontmatter
status: PLANNING | DOING | REVIEW | DONE | BLOCKED
change-type: single | sub
reference?: Array<{source, type: 'request'|'root-change'|'sub-change'|'prev-change' |'doc', note?}>

Sub-change MUST link root:
reference:
  - source: ".sspec/changes/<root-change-dir>"
    type: "root-change"
    note: "Phase <n>: <phase-name>"

Single-change common reference:
reference:
  - source: ".sspec/requests/<request-file>.md"
    type: "request"
  - source: ".sspec/changes/<change-dir>"
    type: "prev-change"
    note: "This change is a follow-up to <change-name> which introduced <feature/bug>. This change addresses <issue> with that feature/bug."
-->

# record-git-id

## A. Problem Statement
当前 change 模板在创建时不会记录任何 git 基线，导致 Agent 只能从后续可变的工作区状态反推 change 起点；而 change 一旦创建就会立刻污染 `git status`，使 branch、HEAD、dirty worktree 这些关键信息失真，进而影响后续 `git diff`、`git log`、审查和分阶段提交判断。

用户需要一个“创建前快照”：它必须在 change 目录写入前采集，默认出现在 change 模板中，能稳定表达当前是否处于 git 仓库、所在 branch/HEAD、以及工作区是否已存在 staged/modified/untracked 变更，并且后续流程不应再自动刷新这份记录。

## B. Proposed Solution
### Approach
把 git 基线放进 `handover.md`，而不是 `spec.md`。`spec.md` 负责描述问题和方案，`handover.md` 本来就承载“给后续 Agent 看的稳定上下文”；将这份信息固定成独立的 immutable section，能让 Agent 在 `@resume` 时第一眼就看到 change 起点，同时避免把执行态元数据混进设计正文。

实现上，在 `create_change()` 里先于目录创建执行一次 git 快照采集，再把渲染后的 Markdown 文本通过 `{{GIT}}` 传给 handover 模板。这样可以保证“创建 change 之前”的仓库状态被捕获，并且不依赖后续 Agent 再运行 git 命令复原现场。对于非 git 仓库或 git 命令不可用的环境，模板写入明确的降级说明，而不是报错中断 change 创建。

### Key Design
### Interface Design

```python
def create_change(sspec_root: Path, change_name: str, *, is_root: bool = False) -> Path:
    """Create a change after capturing pre-creation git baseline."""


def _render_git_snapshot(project_root: Path) -> str:
    """Return the Markdown snippet that fills the {{GIT}} placeholder."""
```

`_render_git_snapshot()` returns ready-to-insert Markdown instead of a raw dict so template rendering stays simple and `copy_template()` remains unchanged. The helper should always succeed with a human-readable fallback block even when `git` is unavailable or `project_root` is not inside a repository.

### Data Flow

```text
sspec change new
  │
  ├── resolve request / derive change name
  ├── create_change()
  │     ├── _render_git_snapshot(project_root)   -> capture branch/HEAD/status before writes
  │     ├── build replacements                   -> CHANGE_NAME / TIME / GIT
  │     ├── mkdir change directory               -> first filesystem mutation
  │     └── copy templates                       -> spec/tasks/handover with immutable git section
  └── link request to change                     -> existing request/change reference flow
```

关键点是把 git 采集放在任何 change 文件写入之前；否则新建的 `.sspec/changes/<dir>/` 会进入 `git status`，导致 snapshot 不再代表真实起点。

### Key Logic

**Design A: Placement in `handover.md`** — Add a dedicated `## Git Baseline (Immutable)` section to both single-change and root-change handover templates. This keeps the snapshot in the resume path and separates it from editable design prose.

**Design B: Snapshot content policy** — Record repository availability, repo root, branch or detached HEAD state, full HEAD commit hash, short subject line, and the pre-creation `git status --short --branch` output. Dirty worktrees are preserved verbatim instead of being normalized away, because those staged/unstaged files are part of the baseline the agent needs to understand.

**Design C: Failure-tolerant capture** — If git is missing, commands fail, or the project is outside a repo, render an explicit fallback message such as `- Repository: unavailable` or a fenced text block stating `Not a git repository.` Change creation must still succeed.

### Scope Summary
| File | Change |
|------|--------|
| `src/sspec/services/change_service.py` | Capture pre-creation git snapshot and inject `GIT` replacement into template rendering |
| `src/sspec/templates/change/handover.md` | Add immutable git baseline section with `{{GIT}}` placeholder |
| `src/sspec/templates/change-root/handover.md` | Mirror the git baseline section for root changes |
| `tests/test_change_service.py` | Add coverage for clean repo, dirty repo, and non-repo change creation |
| `.sspec/spec-docs/change-lifecycle.md` | Document the new change creation contract and immutable git snapshot behavior |
