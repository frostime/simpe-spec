---
name: review-git-baseline
desc: Use the git baseline in memory.md as the review anchor for a change.
---

When `memory.md` has a `Git Baseline (Immutable)` section, prefer git-level review over surface-level file inspection.

## Procedure

1. Find `Git Baseline (Immutable)` in `memory.md` — note the recorded branch, HEAD commit, and dirty-file snapshot.
2. Compare current state against that origin point:
   - `git diff <recorded-HEAD> HEAD` — shows all commits introduced since baseline
   - `git diff <recorded-HEAD>` — includes uncommitted changes
   - `git log <recorded-HEAD>..HEAD --oneline` — commit list
3. If the baseline shows pre-existing dirty files, distinguish those from work introduced by this change before giving feedback.

## Hard rule

Never rewrite or "fix" the `Git Baseline (Immutable)` section during later memorys. It is a read-only origin snapshot created when the change was first started.
