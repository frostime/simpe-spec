# Handover: patch-tool-agent-hardening

**Updated**: 2026-03-17T16:22

---

## Background
<!-- Write once on first session. What this change does and why (1-3 sentences).
Update only if scope fundamentally changes. Details belong in spec.md. -->

Harden `sspec tool patch` so it behaves like a general-purpose agent tool rather than a mostly project-root-relative helper. The change focuses on agent-friendly input (`--stdin`), absolute/relative target path support, retry-aware failure classification, and reusable markdown failure bundles with better line-number diagnostics.

## Git Baseline (Immutable)
<!-- Captured during `sspec change new` before any change files are written.
This section records the change starting point in git and must not be edited or refreshed later. -->

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `feat/add-tools`
- HEAD: `a0bdb8dc56f05b7a785656fab4875bfb44060434`
- Worktree: `clean`
- Status Snapshot: raw `git status --short --branch` output

```text
## feat/add-tools
```

## Working Memory (Stable)
<!-- Curated, long-lived context. Survives context compression and session boundaries.
If something becomes obsolete, mark it as obsolete with a timestamp instead of deleting silently. -->

### Key Files
<!-- Files critical to understanding/continuing this change.
- `path/file` - what it contains, why it matters -->

- `src/sspec/builtin_tools/apply_patch.py` - patch parsing, matching, CLI input handling, and failed patch persistence all live here.
- `.sspec/spec-docs/builtin-tools.md` - product-facing builtin tool contract that must match shipped patch behavior.
- `tests/test_tool_command.py` - command-level coverage for builtin tools; likely home for new patch CLI smoke tests.
- `tests/test_apply_patch.py` - planned focused coverage for parser/result classification edge cases introduced by this change.

### Durable Memory (Typed, Timestamped)
<!-- Promote only facts still useful after the current batch ends.
Single/sub change preferred types: Alignment, Decision, VitalFinding, Constraint, Risk, VerificationShortcut.
Use a custom type only when none fit well; keep it short and clear.
- [2026-03-06T20:39] [Decision] Redis over Memcached because per-key TTL + persistence matter.
- [2026-03-06T20:39] [Constraint] Session Log stays append-only; real next action lives there.
Project-wide items -> ALSO append to project.md Notes. -->

- [2026-03-17T15:13] [Decision] Failed patch artifacts should be written as one markdown bundle with explanatory prose outside fenced `patch` blocks so the file stays directly reusable as later patch input.
- [2026-03-17T15:13] [Decision] `already_applied` should be detected by checking `REPLACE` after `SEARCH` misses, and should not count as a fatal batch failure.
- [2026-03-17T15:13] [Constraint] Non-`.sspec` runs must not create a synthetic `.sspec/` tree for failed patch output; use system temp when no project root exists.
- [2026-03-17T15:31] [VerificationShortcut] Focused verification for this change is `pytest tests/test_apply_patch.py tests/test_tool_command.py` plus `uv run sspec tool patch --prompt`.
- [2026-03-17T16:06] [Decision] Absolute patch targets outside the current workspace require explicit confirmation unless `--unsafe` is present; `--yes` alone must not bypass this safety gate.
- [2026-03-17T16:16] [Decision] Patch header paths now support spaces by treating an optional `:range` suffix as the final segment only; no quoting syntax was added in this change.

## Session Log (Append-Only)
<!-- Newest entry first. Each entry is an atomic batch (one cohesive work record).

Header format:
### 2026-03-06T20:39 [work-log] <short title>

Tags are freeform but must be readable. Examples: work-log, user-feedback, argue, risk.
Any user interaction (feedback, @align, @argue) MUST start a new log entry. -->

### 2026-03-17T15:13 [work-log] design and draft plan

**Accomplished**
- Created change `26-03-17T15-12_patch-tool-agent-hardening` for patch tool hardening.
- Wrote `spec.md` covering absolute/relative patch targets, `--stdin`, richer failure statuses, line-number diagnostics, and markdown failed-bundle output.
- Drafted `tasks.md` phases for parser/input work, apply/result classification work, and regression/doc updates.

**Next**
- Present the design and draft plan to the user for gate approval.
- If approved, implement in `src/sspec/builtin_tools/apply_patch.py`, add focused tests, then verify with focused pytest + lint.

**Notes**
- Bundle design intentionally keeps patch content inside fenced `patch` blocks so the markdown artifact can be reused as future patch input.

### 2026-03-17T15:31 [work-log] implementation complete

**Accomplished**
- Implemented patch header parsing that accepts absolute paths and open-ended line ranges, plus a new `--stdin` input mode.
- Added retry-aware result statuses (`already_applied`, ambiguity variants, no-change) and line-numbered failure diagnostics.
- Replaced per-file failed patch dumps with one markdown bundle, updated builtin tool docs, and added focused parser + command tests.

**Next**
- Wait for user review of the completed patch-tool hardening implementation.
- If feedback arrives, update `spec.md` / `tasks.md` first if scope or design changes, then continue from `REVIEW`.

**Notes**
- Non-`.sspec` failures now default to a system temp markdown bundle instead of creating a local `.sspec/` tree.
- Verified with `uv run ruff check src/sspec/builtin_tools/apply_patch.py tests/test_apply_patch.py tests/test_tool_command.py`, `uv run pytest tests/test_apply_patch.py tests/test_tool_command.py`, and `uv run sspec tool patch --prompt`.

### 2026-03-17T15:36 [user-feedback] prompt tone and stdin examples

**Accomplished**
- User accepted the implementation overall and requested a shorter `patch --prompt` plus balanced stdin examples for both bash and PowerShell.
- Updated the prompt text accordingly inside `src/sspec/builtin_tools/apply_patch.py`.

**Next**
- Re-run focused verification for the prompt output and return to user review.

**Notes**
- Feedback stays inside the same change; no design/scope split was required.

### 2026-03-17T15:43 [user-feedback] prompt structure refinement

**Accomplished**
- User requested a clearer prompt structure: tool identity, patch format, CLI apply methods, and important rules.
- Reorganized `PATCH_PROMPT` in `src/sspec/builtin_tools/apply_patch.py` to follow that sequence while keeping both bash and PowerShell stdin examples.

**Next**
- Re-run prompt verification and return to user review.

**Notes**
- This feedback changed presentation only; implementation behavior stayed the same.

### 2026-03-17T16:06 [user-feedback] outside-workspace absolute path safety

**Accomplished**
- Added a confirmation gate for absolute patch targets outside the current workspace and introduced `--unsafe` as the explicit automation bypass.
- Fixed the preview-table scope bug for open-ended ranges by switching preview rendering to `format_line_range(...)`.
- Added regression tests for confirmation behavior, `--unsafe` bypass, and canonical open-ended scope display.

**Next**
- Re-run prompt verification and return to user review.

**Notes**
- `--stdin` mode now refuses outside-workspace absolute paths unless `--unsafe` is provided, because piped stdin cannot safely carry an additional interactive confirmation.

### 2026-03-17T16:16 [user-feedback] follow-up review adjustments

**Accomplished**
- Kept outside-workspace warnings visible during `--dry-run` instead of returning early before safety information is shown.
- Moved `--unsafe` out of the prompt's input-method list into a dedicated safety note.
- Added support for patch header paths containing spaces and covered the behavior with parser + command tests.

**Next**
- Return to user review with the latest safety/prompt/parser refinements.

**Notes**
- Supporting spaces was implemented by loosening header parsing rather than inventing a new quoting syntax, so `:L...` range suffixes must remain the final path segment.

### 2026-03-17T16:22 [user-feedback] prompt example clarity

**Accomplished**
- Replaced the abstract "paths may contain spaces" parsing note in `PATCH_PROMPT` with a concrete absolute-path example that includes spaces and a range suffix.

**Next**
- Re-run prompt verification and return to user review.

**Notes**
- This change only affects prompt clarity; parsing behavior is unchanged.
