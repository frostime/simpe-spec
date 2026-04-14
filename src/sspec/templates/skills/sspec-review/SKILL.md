---
name: sspec-review
description: "User acceptance and feedback loop. Handle argue-improve cycles until user is satisfied."
metadata:
  author: frostime
  version: 4.0.0
---

# SSPEC Review

Collect user feedback, iterate improvements, close the loop.

---

## Feedback Loop

```
User feedback ─→ Classify (@feedback-class) ─→ Act ─→ @align "Fixed. Check again?"
                                                 ↑                    │
                                                 └────────────────────┘
                                           (repeat until user satisfied)
```

## Step 1: Classify First (Mandatory)

**Before touching any file**, output the classification:

```
@feedback-class: <minor-fix | amend | follow-up | supersede>
Reason: <one sentence>
```

**The single test to apply**:
> Can the original spec/design still accurately predict the post-change code?
> **YES → minor-fix** | **NO → amend → revision required**

### minor-fix vs amend

| ✅ minor-fix | ❌ amend (revision required) |
|---|---|
| 变量 / 函数命名调整 | 新增验收条件 |
| typo / 文案修正 | 新增验证 / 日志 / 错误分支 |
| 明显 bug（无行为变更） | 新增用户可见行为 |
| 已有验收边界内的边界修复 | 修改范围边界 |
| | 任何让原 spec 无法完整预测最终代码的反馈 |

## Step 2: Act by Class

| Class | Action |
|-------|--------|
| **minor-fix** | Fix directly or add `Feedback Tasks` if non-trivial |
| **amend** | See amend protocol below |
| **follow-up** | `@align` user before opening a new change with `prev-change` reference |
| **supersede** | `@align` user before marking current change `BLOCKED` and opening a replacement |

📚 `sspec howto handle-review-scope-change`

### Amend Protocol (post-gate)

1. Re-enter Clarify posture to understand the gap
2. `sspec change scaffold revision <change> --title "..."` — create revision file first
3. Fill revision: Reason / Spec Impact / Design Impact / Task Impact
4. **Cross-reference** (Fix E):
   - Append to `spec.md` frontmatter `reference:`:
     ```yaml
     - source: ".sspec/changes/<change>/revisions/NNN-xxx.md"
       type: "revision"
       note: "<one-line summary>"
     ```
   - Add `Feedback Tasks` block in `tasks.md` with header linking the revision:
     ```markdown
     ### Feedback Tasks (→ [NNN-xxx](./revisions/NNN-xxx.md))
     - [ ] ...
     ```
5. Update tasks.md; return to DOING

### Feedback Tasks

Use `Feedback Tasks` only for work that still belongs to the current change. Do **not** use it as a dumping ground for follow-up or replacement work.

### Rejection Protocol (@argue)

1. **Stop immediately** — do not continue current work
2. **Classify** using Step 1 above
3. **Acknowledge** the disagreement explicitly
4. **Act** based on classification

### Git-Aware Review

When `memory.md` has a Git Baseline section, use it as the review anchor.

📚 `sspec howto review-git-baseline`

For independent review, consider subagent audits to avoid context blind spots.

📚 `sspec howto make-subagent-audit` | Directive: `@subagent-audits`

## Close Loop

When user is satisfied:
1. Ensure all tasks marked `[x]`; update status: `REVIEW → DONE`
2. If change produced architectural knowledge → `@align` user about creating/updating a spec-doc
3. Suggest archive or `@memory`

## Status Flow

```
DOING (implement complete) → REVIEW (user reviewing)
  → DONE (user satisfied)
  → DOING (needs more work → implement feedback tasks → REVIEW again)
  → PLANNING (accepted redesign → back to design/plan)
  → BLOCKED (user chooses replacement or external blocker)
```

**FORBIDDEN**: PLANNING→DONE, DOING→DONE — never skip REVIEW.
