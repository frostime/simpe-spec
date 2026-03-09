# Handover: add-howto-cli

**Updated**: 2026-03-10T01:29

---

## Background
<!-- Write once on first session. What this change does and why (1-3 sentences).
Update only if scope fundamentally changes. Details belong in spec.md. -->

Add a lightweight HOWTO documentation channel to sspec so narrowly scoped operational guidance can be disclosed independently from `AGENTS.md` and SKILLs. The first deliverable is a read-only CLI lookup flow backed by builtin package docs plus project-local `.sspec/howto/` documents.

## Git Baseline (Immutable)
<!-- Captured during `sspec change new` before any change files are written.
This section records the change starting point in git and must not be edited or refreshed later. -->

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `feat/howto`
- HEAD: `37642d802a3ce3263ed419239571f78b1be045f7`
- Worktree: `dirty`
- Status Snapshot: raw `git status --short --branch` output

```text
## feat/howto
A  .sspec/requests/26-03-09T23-23_add-howto-cli.md
```

## Working Memory (Stable)
<!-- Curated, long-lived context. Survives context compression and session boundaries.
If something becomes obsolete, mark it as obsolete with a timestamp instead of deleting silently. -->

### Key Files
<!-- Files critical to understanding/continuing this change.
- `path/file` - what it contains, why it matters -->
- `src/sspec/commands/skill.py` - closest existing pattern for CLI-to-service split around user-managed markdown-backed artifacts.
- `src/sspec/services/skill_service.py` - reusable precedent for metadata parsing, directory scanning, and structured list results.
- `src/sspec/commands/doc.py` - closest precedent for listing markdown documents and creating readable terminal tables.
- `.sspec/requests/26-03-09T23-23_add-howto-cli.md` - source request and product intent for HOWTO behavior.
- `.sspec/changes/26-03-09T23-41_add-howto-cli/spec.md` - active design record; current proposal uses package docs + duplicate warning/skip behavior.
- `src/sspec/services/howto_service.py` - HOWTO registry, duplicate detection, body loading, and scaffold creation.
- `src/sspec/commands/howto.py` - CLI entrypoint for implicit read, explicit list/read/new, and warning rendering.
- `tests/test_howto_command.py` - verification coverage for list, implicit read, duplicates, and scaffolding.

### Decisions (Timestamped)
<!-- Timestamp every entry (minute precision).
- [2026-03-06T20:39] **Decision** - Redis over Memcached
  **Why**: Need per-key TTL + persistence -->
- [2026-03-09T23:43] **Decision (superseded at 2026-03-09T23:57)** - Implement HOWTO as a single root command (`sspec howto`) instead of a subgroup.
  **Why**: Initial design favored the shortest possible surface before user feedback introduced `howto new` and reserved-subcommand concerns.
- [2026-03-09T23:43] **Decision** - Store official HOWTOs in `src/sspec/howto/` and merge them with `.sspec/howto/` at runtime.
  **Why**: Official HOWTOs are package resources, while project HOWTOs are local customizations; merging both through one service avoids template/update complexity.
- [2026-03-09T23:43] **Decision (superseded at 2026-03-09T23:57)** - Project HOWTOs override builtin HOWTOs on the same normalized name.
  **Why**: Initial design prioritized local customization, but the user later rejected silent override as too dangerous.
- [2026-03-09T23:57] **Decision** - Switch from silent override to duplicate warning + skip.
  **Why**: The user explicitly called override behavior dangerous; collision handling must be visible and non-destructive.
- [2026-03-09T23:57] **Decision** - Evolve `sspec howto` into an extensible group with implicit read fallback.
  **Why**: This preserves the short `sspec howto <name>` syntax while still making room for `new` and explicit `list/read` subcommands.
- [2026-03-09T23:57] **Decision** - Rename internal `slug` terminology to `lookup_key` in the design.
  **Why**: The user flagged `slug` as unclear; `lookup_key` is more explicit about its role.
- [2026-03-10T00:28] **Decision** - Scan builtin HOWTOs before project HOWTOs and skip later duplicates with a warning.
  **Why**: This matches the user's request to avoid dangerous override behavior while keeping duplicate handling deterministic.
- [2026-03-10T00:48] **Decision** - Default HOWTO `list` and `read` output to plain text, with `--format rich` as the human-friendly opt-in.
  **Why**: The user wants HOWTO to be agent-first by default, so pretty rendering must be optional rather than the baseline.
- [2026-03-10T01:24] **Decision** - Plain `list` output uses YAML-like records and `read` can accept multiple HOWTO names.
  **Why**: The user wants agent-friendly structure plus batch retrieval without requiring repeated CLI calls.
- [2026-03-10T01:29] **Decision** - Plain read mode prints only lightweight separators plus rendered body, with no metadata block.
  **Why**: The user wants agent-facing output to avoid frontmatter-like noise while still keeping multi-document boundaries obvious.

### Notes (Timestamped)
<!-- Gotchas, edge cases, risks, verification shortcuts. Timestamp every entry.
Project-wide items -> ALSO append to project.md Notes. -->
- [2026-03-09T23:43] Reuse existing frontmatter parsing patterns, but accept both `desc` and `description` to reduce friction between HOWTO and existing spec/skill wording.
- [2026-03-09T23:43] Keep first version read-only; adding authoring/sync commands now would expand scope before the basic disclosure path is proven.
- [2026-03-09T23:57] The user is open to `howto new`, so first-version scope can include project HOWTO scaffolding without needing a full lifecycle manager.
- [2026-03-09T23:57] Before implementation starts, align on the first builtin HOWTO batch so package content scope is explicit.
- [2026-03-10T00:28] Implemented builtin HOWTO seed files, later narrowed to the user-preferred batch.
- [2026-03-10T00:28] Validation passed with `uv run ruff check src tests/test_howto_command.py tests/test_project_init_service.py` and `uv run pytest tests/test_howto_command.py tests/test_project_init_service.py`.
- [2026-03-10T00:48] Updated HOWTO tests to rely on project-local sample files rather than the exact body text of builtin HOWTO documents.
- [2026-03-10T00:48] Smoke check passed for `uv run sspec howto --help` and `uv run sspec howto --list` after the plain-text output change.
- [2026-03-10T00:48] Final builtin HOWTO batch is `write-howto`, `use-sspec-ask`, and `read-long-mdfile`.
- [2026-03-10T01:24] Final validation passed with `uv run ruff check src tests/test_howto_command.py tests/test_project_init_service.py` and `uv run pytest tests/test_howto_command.py tests/test_project_init_service.py` after the second review round.
- [2026-03-10T01:24] Manual smoke checks passed for `sspec howto list --format rich`, `sspec howto write-howto --format rich`, and multi-read plain output.
- [2026-03-10T01:29] Final validation re-passed after removing plain read metadata output.

## Session Log (Append-Only)
<!-- Newest entry first. Each entry is an atomic batch (one cohesive work record).

Header format:
### 2026-03-06T20:39 [work-log] <short title>

Tags are freeform but must be readable. Examples: work-log, user-feedback, argue, risk.
Any user interaction (feedback, @align, @argue) MUST start a new log entry. -->

### 2026-03-09T23:43 [work-log] research and design draft

**Accomplished**
- Read project context plus `sspec-research`, `sspec-design`, and `sspec-align` skills.
- Created linked change `.sspec/changes/26-03-09T23-41_add-howto-cli/` from the request.
- Investigated existing markdown-backed command patterns in `skill.py`, `skill_service.py`, and `doc.py`.
- Drafted the initial design in `spec.md`, including source precedence, CLI contract, and candidate implementation files.

**Next**
- Align the HOWTO design with the user before entering planning.
- After approval, convert the design into `tasks.md` and start implementation.

**Notes** (optional)
- The proposed design intentionally keeps HOWTO separate from template sync and skill installation logic.

### 2026-03-09T23:57 [user-feedback] design feedback round 1

**Accomplished**
- Prompted the user through `sspec ask` for design approval.
- Received concrete feedback on collision policy, command shape, authoring support, and builtin seed content.
- Revised the design direction accordingly in `spec.md`.

**Next**
- Re-align the revised design with the user before entering planning.
- If approved, turn the updated design into implementation tasks.

**Notes** (optional)
- Key feedback: no silent override; explain internal terminology; support `howto new`; keep room to discuss initial builtin HOWTO topics.

### 2026-03-10T00:28 [work-log] implement howto cli and validate

**Accomplished**
- Added shared HOWTO path helpers and project-init support for `.sspec/howto/`.
- Implemented `howto_service.py` plus `sspec howto` CLI commands with implicit read fallback.
- Added four builtin HOWTO markdown files under `src/sspec/howto/`.
- Added targeted tests and validated them with ruff and pytest.
- Moved the change to `REVIEW` and updated task progress to 100%.

**Next**
- Ask the user to review the implementation.
- Confirm whether the initial builtin HOWTO batch should be kept as-is or adjusted.

**Notes** (optional)
- `sspec howto` currently requires being inside an sspec project so project-local HOWTOs and scaffolding have a consistent root.

### 2026-03-10T00:48 [user-feedback] review round 1 fixes

**Accomplished**
- Switched `howto list` and `howto read` to plain-text default output.
- Added `--format rich` for human-friendly rendering.
- Updated HOWTO help text to document implicit `sspec howto <name>` reads.
- Reworked tests so they no longer depend on specific builtin HOWTO document bodies.
- Re-ran ruff, pytest, and a manual CLI smoke check.

**Next**
- Ask the user to review this second round.
- Confirm whether the current builtin HOWTO batch should be kept or adjusted.

**Notes** (optional)
- Plain-text list output is tab-separated logically; terminal tab expansion may display it as aligned columns.

### 2026-03-10T01:24 [user-feedback] review round 2 fixes

**Accomplished**
- Added `--format` handling after `list` and `read` subcommands.
- Switched plain `list` output from tabular text to YAML-like records without `file`.
- Removed top-level headings from builtin HOWTO source docs and new HOWTO scaffolds.
- Added multi-name `howto read` support and kept auto-added display headers at render time.
- Re-ran lint, tests, and manual smoke checks.

**Next**
- Ask the user to review the third round.

**Notes** (optional)
- `sspec howto write-howto --format rich` now works as requested because `read` accepts local `--format` overrides.

### 2026-03-10T01:29 [user-feedback] review round 3 fixes

**Accomplished**
- Removed plain read metadata blocks.
- Switched plain read output to `=== name ===` separators.
- Kept auto-added display headers and widened multi-doc separation.
- Re-ran lint, tests, and multi-read smoke checks.

**Next**
- Ask the user for final review.

**Notes** (optional)
- Plain read output now shows only separators plus rendered markdown body, which is closer to the intended agent-facing UX.
