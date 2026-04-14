---
name: handle-review-scope-change
desc: Decide whether review feedback stays in the current change, becomes a follow-up change, or supersedes the current change.
---

When review feedback adds work, do not default to `memory.md` and do not open a new change automatically.

## Revision Trigger Test

Apply this before classifying any feedback:

> **Can the original spec/design still accurately predict the post-change code?**
> YES → `minor-fix` | NO → `amend` → revision required

## Quick Classifier

| If the feedback... | Class | What to do |
|---|---|---|
| tweaks implementation details without changing accepted scope | `minor-fix` | keep the current change; fix directly or add `Feedback Tasks` |
| adds acceptance work that still belongs to the current change | `current-change-amend` | if post-gate: create `revisions/NNN-*.md` first, then update `tasks.md`; if pre-gate: update `spec.md` directly |
| asks for an additional next-step after the current change can already stand on its own | `follow-up-change` | `@align` user first; if approved, create a new change with `prev-change` reference |
| shows the current change is fundamentally wrong and should stop | `supersede-change` | `@align` user first; if approved, mark the current change `BLOCKED` and create a replacement change |

## Procedure

1. Decide whether the current change still stands on its own.
2. If the answer is yes and the feedback is still part of the same acceptance target:
   - If `spec.md` / `design.md` have already passed the design gate, create `revisions/NNN-description.md` first to record what changed and why, then update `tasks.md`.
   - If still in PLANNING, update `spec.md` / `design.md` directly.
3. If the answer is yes but the feedback is really "what to do next", stop and `@align` before opening a follow-up change.
4. If the answer is no because the current direction is wrong, stop and `@align` before any `BLOCKED` + replacement-change action.
5. Cross-reference (post-gate amend only):
   - Append to `spec.md` frontmatter `reference:`:
     ```yaml
     - source: ".sspec/changes/<change>/revisions/NNN-xxx.md"
       type: "revision"
       note: "<one-line summary of what changed>"
     ```
   - Use this header format for the Feedback Tasks block in `tasks.md`:
     ```markdown
     ### Feedback Tasks (→ [NNN-xxx](./revisions/NNN-xxx.md))
     ```
6. Record the outcome:
   - current-change amend -> `revisions/NNN-*.md` (if post-gate) + `tasks.md` + `spec.md` reference + `memory.md`
   - follow-up / supersede -> `memory.md` plus the new change's `spec.md` reference chain

## Hard Rules

- Accepted scope/design changes must not live only in `memory.md`.
- `Feedback Tasks` is only for work that still belongs to the current change.
- Opening a follow-up or replacement change is a direction decision and must be user-approved through `@align`.
- Do not use `BLOCKED` for ordinary follow-up work.

## Examples

| Feedback | Class | Result |
|---|---|---|
| "Rename this helper and fix the null edge case." | `minor-fix` | keep current change; add `Feedback Tasks` only if the work is non-trivial |
| "This feature still needs an audit log before I can accept it." | `current-change-amend` | update the current change's design/tasks, then keep implementing |
| "Looks good. Next, add CSV export too." | `follow-up-change` | `@align`, then open a new linked change if the user agrees |
| "This whole approach is wrong. Restart around SQLite instead." | `supersede-change` | `@align`, then `BLOCKED` + replacement change if the user agrees |
