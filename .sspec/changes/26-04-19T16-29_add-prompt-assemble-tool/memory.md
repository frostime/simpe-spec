# Memory: add-prompt-assemble-tool

**Updated**: 2026-04-19T19:16+08:00

## Git Baseline (Immutable)
<!-- Captured during `sspec change new` before any change files are written.
This section records the change starting point in git and MUST NOT be edited or refreshed later. -->

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `main`
- HEAD: `f2c5095b79c213a87d4e3badb858dd6f18364204`
- Worktree: `dirty`
- Status Snapshot: raw `git status --short --branch` output

```text
## main...origin/main
A  .sspec/requests/26-04-19T16-14_add-prompt-assemble-tool.md
```

## State
Implementation is complete. Next step is user review.

## Key Files
- `.sspec/changes/26-04-19T16-29_add-prompt-assemble-tool/spec.md` — approved problem/scope for the prompt assembly tool
- `.sspec/changes/26-04-19T16-29_add-prompt-assemble-tool/design.md` — technical contract for CLI flags, preset schema, source behavior, and output format
- `.sspec/changes/26-04-19T16-29_add-prompt-assemble-tool/tasks.md` — implementation checklist
- `src/sspec/services/prompt_service.py` — source normalization, preset I/O, source execution, rendering, and tmp output logic
- `tests/test_prompt_service.py` — service-level coverage for prompt source behavior and rendering contract
- `src/sspec/builtin_tools/prompt.py` — builtin CLI for inline flags, preset import/export, dry-run, and interactive flow
- `tests/test_tool_command.py` — command-level prompt coverage
- `.sspec/spec-docs/builtin-tools.md` — builtin tool contract updated with prompt tool behavior
- `src/sspec/builtin_tools/pack_zip.py` — shared gitignore parser now uses safe directory walking on Python 3.10
- `tests/test_gitignore_parser.py` — regression coverage for broken-link traversal during gitignore discovery
- `.sspec/tmp/26-04-19T16-12_prompt拼接起来的demo.md` — user-provided target-style example

## Knowledge
- [2026-04-19T17:15+08:00] [Decision] User chose a single command with flags over subcommands.
- [2026-04-19T17:35+08:00] [Correction] Inline generation is the main path: `sspec tool prompt --add-file ... --add-shell ...`. Presets are reusable exports/imports layered on runtime source lists.
- [2026-04-19T17:15+08:00] [Decision] Presets live under `.sspec/prompts/<name>.yml` and no-args command enters interactive assembly.
- [2026-04-19T18:32+08:00] [Decision] Default output keeps hybrid headers, and now uses YAML frontmatter for meta plus four-backtick fenced content for a hard meta/content boundary, written as `.prompt.txt`.
- [2026-04-19T19:16+08:00] [Gotcha] Python 3.10 `pathlib.rglob()` can still surface filesystem scan errors on broken Windows links; shared gitignore discovery now uses `os.walk(..., followlinks=False, onerror=...)`.
- [2026-04-19T17:15+08:00] [Rejected] Markdown section output was rejected because embedded Markdown content can blur boundaries.

## Milestones
- [2026-04-19T17:15+08:00] Created change, aligned key design choices with user, drafted spec/design/tasks.
- [2026-04-19T17:35+08:00] Updated spec/design/tasks pre-implementation to make inline `--add-*` generation primary and preset export/import secondary.
- [2026-04-19T18:32+08:00] Updated output contract pre-implementation to use YAML frontmatter plus four-backtick fenced content.
- [2026-04-19T18:45+08:00] Implemented prompt service layer and passed `tests/test_prompt_service.py`.
- [2026-04-19T18:55+08:00] Implemented prompt builtin CLI and passed prompt-focused command tests.
- [2026-04-19T19:02+08:00] Updated spec-doc, ran targeted lint/format/tests, and manually verified inline + preset flows in `tmp/test_prompt_tool`.
- [2026-04-19T19:16+08:00] Fixed broken-link crash path in shared gitignore discovery and passed regression + prompt test suites.
