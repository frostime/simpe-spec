---
change: "patch-create-overwrite"
updated: "2026-04-18T19:56:22+08:00"
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Extend LRR Parsing for File-Level Operations ✅
- [x] Modify `src/sspec/builtin_tools/apply_patch.py` — extend opener recognition to support `SEARCH`, `CREATE`, and `OVERWRITE` while preserving the existing LRR schema/pattern shape per spec Feat A
- [x] Modify `src/sspec/builtin_tools/apply_patch.py` — add operation decoding plus parse-time validation for line-range rejection, whitespace-only upper body, and operation-specific existence checks per spec Feat A / Feat D
- [x] Manual verification in `tmp/test_patch_create_overwrite` — validate parsing/validation behavior for `CREATE` / `OVERWRITE`, including invalid line ranges and missing/existing target rules
**Verification**: `rtk uv run python -m py_compile src/sspec/builtin_tools/apply_patch.py`, `rtk uv run ruff check src/sspec/builtin_tools/apply_patch.py`, and targeted manual `apply_patches()` smoke checks confirm LRR parsing and validation behavior

### Phase 2: Implement CREATE / OVERWRITE Apply Semantics ✅
- [x] Modify `src/sspec/builtin_tools/apply_patch.py` — dispatch apply flow by operation and implement safe-create plus existing-file overwrite semantics per spec Feat B / Feat C
- [x] Modify `src/sspec/builtin_tools/apply_patch.py` — preserve operation markers in preview, failed bundle output, and result formatting while reusing existing reporting infrastructure per spec Feat D
- [x] Manual verification in `tmp/test_patch_create_overwrite` — cover idempotent create, conflicting create, overwrite no-change, overwrite missing-file failure, empty-content behavior, and parent-directory auto-create
**Verification**: targeted manual `apply_patches()` smoke checks return `applied`, `already_applied`, `file_exists`, `no_change_patch`, and `missing_file` in the expected scenarios

### Phase 3: Sync Prompt and Product Docs ✅
- [x] Update `src/sspec/builtin_tools/apply_patch.py` — revise `PATCH_PROMPT` to document `CREATE` / `OVERWRITE`, line-range limits, parent creation, and empty-SEARCH non-goals per spec Docs E
- [x] Update `.sspec/spec-docs/builtin-tools.md` — publish shipped CREATE/OVERWRITE behavior and safety rules
- [x] Update `src/sspec/templates/skills/write-patch/SKILL.md` — add agent-facing guidance and examples for SEARCH vs CREATE vs OVERWRITE
**Verification**: `rtk uv pip install -e .`, `rtk uv run sspec project update`, and `rtk uv run sspec tool patch --prompt` completed successfully; the shipped prompt/spec-doc/skill now describe the same CREATE/OVERWRITE contract

### Feedback Tasks (→ [001-shorten-patch-prompt-and-add-installed-skill-reference](./revisions/001-shorten-patch-prompt-and-add-installed-skill-reference.md))
- [x] Refine `src/sspec/builtin_tools/apply_patch.py` — shorten `PATCH_PROMPT`, switch examples to ````patch, add a dedicated multi-block bundle section, and use CLI-centered wording per revision 001
- [x] Extend `src/sspec/builtin_tools/apply_patch.py` — resolve the installed-package `write-patch` skill path and append it as a local reference in prompt output per revision 001
- [x] Verify `src/sspec/builtin_tools/apply_patch.py` — run `rtk uv run sspec tool patch --prompt` and confirm the new short form, installed-path reference, and multi-block wording

### Feedback Tasks (→ [002-fix-create-idempotence-and-clean-unused-patch-status](./revisions/002-fix-create-idempotence-and-clean-unused-patch-status.md))
- [x] Refine `src/sspec/builtin_tools/apply_patch.py` — remove the unused `invalid_operation_body` status and keep declared statuses aligned with shipped behavior per revision 002
- [x] Refine `src/sspec/builtin_tools/apply_patch.py` — normalize existing file content to `\n` in the `CREATE` idempotence check so newline-style differences still return `already_applied` per revision 002
- [x] Refine `src/sspec/builtin_tools/apply_patch.py` — extract a shared `OPERATION_TO_MARKER` mapping for preview and failed bundle rendering per revision 002
- [x] Verify `src/sspec/builtin_tools/apply_patch.py` — run `rtk uv run python -m py_compile`, `rtk uv run ruff check`, and a manual CRLF create-idempotence smoke check

---

## Progress

**Overall**: 100%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 100% | ✅ |
| Phase 2 | 100% | ✅ |
| Phase 3 | 100% | ✅ |

**Recent**:
- 2026-04-18: Implemented LRR-preserving CREATE/OVERWRITE parsing, operation dispatch, and operation-aware preview/bundle formatting in `apply_patch.py`.
- 2026-04-18: Fixed the `PatchOperation` typing issue by annotating `PATCH_OPEN_MARKERS` as `dict[str, PatchOperation]`.
- 2026-04-18: Updated the built-in patch prompt, builtin-tools spec-doc, and write-patch skill to document CREATE/OVERWRITE semantics.
- 2026-04-18: Reinstalled the package, synced generated skill copies, and manually smoke-tested create/overwrite scenarios in `tmp/test_patch_create_overwrite`.
- 2026-04-18: Applied revision 001 by shortening `PATCH_PROMPT`, adding bundle-focused wording, and appending the installed `write-patch` skill path to `--prompt` output.
- 2026-04-18: Applied revision 002 by normalizing CREATE idempotence across newline styles, removing the unused `invalid_operation_body` status, and extracting `OPERATION_TO_MARKER`.
