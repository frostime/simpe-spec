# Memory: patch-create-overwrite

**Updated**: 2026-04-18T21:23:12+08:00

## Git Baseline (Immutable)
<!-- Captured during `sspec change new` before any change files are written.
This section records the change starting point in git and MUST NOT be edited or refreshed later. -->

- Captured: before change file creation
- Repository: `H:/SrcCode/playground/sspec`
- Branch: `main`
- HEAD: `e6a038d070f67dd59eaf9ca9f939990df2dd5727`
- Worktree: `clean`
- Status Snapshot: raw `git status --short --branch` output

```text
## main...origin/main
```

## State
- Implementation complete, including revisions 001 and 002.
- Next step: user review of final patch behavior and prompt UX; ready for DONE if accepted.

## Key Files
- `src/sspec/builtin_tools/apply_patch.py` — patch parser, apply logic, prompt text, preview output, and CLI command all live here.
- `tests/test_apply_patch.py` — focused behavior coverage for parser/application edge cases.
- `.sspec/spec-docs/builtin-tools.md` — shipped builtin tool contract that must match patch behavior.
- `src/sspec/templates/skills/write-patch/SKILL.md` — product guidance for agents using patch workflows.

## Knowledge
- [2026-04-18T15:49+08:00] [Decision] Add explicit `CREATE` and `OVERWRITE` patch markers instead of overloading empty SEARCH for missing-file creation.
- [2026-04-18T15:49+08:00] [Decision] `CREATE` is idempotent for identical existing content and must fail on different existing content to preserve safe-create semantics.
- [2026-04-18T15:49+08:00] [Decision] `OVERWRITE` applies only to existing files and treats identical content as `no_change_patch`.
- [2026-04-18T15:49+08:00] [Decision] `CREATE` and `OVERWRITE` are file-level operations: line ranges are invalid, upper block body must be whitespace-only, and empty REPLACE content is allowed.
- [2026-04-18T15:49+08:00] [Decision] `CREATE` auto-creates missing parent directories; no extra CLI flag is planned for this feature.
- [2026-04-18T15:55+08:00] [Decision] Extend the existing LRR parser with one shared opener role plus an opener-to-operation decoder; avoid introducing a new parser architecture for CREATE/OVERWRITE.
- [2026-04-18T19:56+08:00] [VerificationShortcut] Use `rtk uv run python - <<'PY' ... apply_patches(...) ... PY` for fast manual smoke checks of patch semantics in `tmp/test_patch_create_overwrite`.
- [2026-04-18T19:56+08:00] [Decision] `OVERWRITE` missing-file handling is enforced in apply-time dispatch so parse-time validation can continue accepting the block and return the existing `missing_file` result shape.
- [2026-04-18T19:56+08:00] [Decision] Pylance requires `PATCH_OPEN_MARKERS` to be annotated as `dict[str, PatchOperation]` so `parse_patch_operation()` preserves the `Literal` return type.
- [2026-04-18T20:41+08:00] [Decision] `PATCH_PROMPT` now prioritizes authoring brevity: three block forms, core rules, and multi-block bundle guidance stay in the short prompt; deeper semantics remain in the skill/spec-doc.
- [2026-04-18T20:41+08:00] [Decision] `--prompt` dynamically resolves `write-patch` from the installed `sspec` package via `importlib.resources`, keeping the local reference aligned with the active package version.
- [2026-04-18T21:23+08:00] [Decision] `CREATE` idempotence compares normalized `\n` text so newline-style differences still count as identical content.
- [2026-04-18T21:23+08:00] [Decision] Remove `invalid_operation_body` from declared statuses because parse-time CREATE/OVERWRITE body validation remains aggregated under `parse_error`.
- [2026-04-18T21:23+08:00] [Decision] Use shared `OPERATION_TO_MARKER` for preview and failed bundle rendering to avoid duplicated reverse mappings.

## Milestones
- [2026-04-18T15:49:27+08:00] Created change `26-04-18T15-46_patch-create-overwrite` and wrote spec.md + design.md for explicit CREATE/OVERWRITE patch operations.
- [2026-04-18T15:55:18+08:00] Refined design.md/spec.md to explicitly preserve the existing LRR parsing pipeline and constrain the change to opener decoding plus file-level validation/apply branches.
- [2026-04-18T19:56:22+08:00] Implemented CREATE/OVERWRITE support, updated prompt/spec-doc/skill text, reinstalled and synced templates, and manually verified create/overwrite scenarios in `tmp/test_patch_create_overwrite`.
- [2026-04-18T20:41:21+08:00] Applied revision 001: shortened `PATCH_PROMPT`, switched examples to ````patch, added multi-block bundle guidance, and appended the installed `write-patch` skill path to `--prompt` output.
- [2026-04-18T21:23:12+08:00] Applied revision 002: removed the unused status, normalized CREATE idempotence across CRLF/LF, extracted `OPERATION_TO_MARKER`, and manually verified CRLF reapply returns `already_applied`.
