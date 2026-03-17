---
change: "patch-tool-agent-hardening"
updated: "2026-03-17T16:22:23+08:00"
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Patch Input and Header Parsing ✅
- [x] Modify `src/sspec/builtin_tools/apply_patch.py` — add mutually exclusive `--stdin` input mode alongside existing file/interactive inputs per spec.md B
- [x] Refactor patch header parsing in `src/sspec/builtin_tools/apply_patch.py` — support absolute paths plus canonical/open-ended line ranges per spec.md B
- [x] Add parser-focused tests in `tests/test_apply_patch.py` — cover absolute paths, Windows-style paths, `L10-L20`, `L10-`, and `-L20`
**Verification**: `pytest tests/test_apply_patch.py -k "parse or range"` passes; manual smoke check confirms `sspec tool patch --stdin` accepts piped markdown patch content

### Phase 2: Retry-Aware Apply Classification and Output ✅
- [x] Modify `src/sspec/builtin_tools/apply_patch.py` — classify `already_applied`, ambiguity, and not-found outcomes with related line numbers per spec.md B
- [x] Update failure reporting in `src/sspec/builtin_tools/apply_patch.py` — print patch source line, target line(s), reason, and truncated patch previews
- [x] Replace per-file failed patch dumps with one markdown bundle writer in `src/sspec/builtin_tools/apply_patch.py` — `.sspec/tmp/...` in project mode and system temp output otherwise
**Verification**: targeted tests prove repeated apply becomes `already_applied`; manual run of a mixed success/failure batch shows line-numbered summaries plus one reusable markdown bundle

### Phase 3: Regression Coverage and Docs ✅
- [x] Extend `tests/test_tool_command.py` — cover `patch --stdin`, non-`.sspec` execution, and summary output shape
- [x] Extend `tests/test_apply_patch.py` — cover markdown failure bundles being reusable as later patch input
- [x] Update `.sspec/spec-docs/builtin-tools.md` — document patch input modes, path handling, line-range syntax, and failure bundle behavior
**Verification**: focused patch-tool tests pass; `uv run sspec tool patch --prompt` reflects the new contract; spec-doc matches shipped behavior

### Feedback Tasks ✅
- [x] Refine `src/sspec/builtin_tools/apply_patch.py` prompt text — reduce verbosity and document both bash and PowerShell `--stdin` examples
- [x] Reorganize `src/sspec/builtin_tools/apply_patch.py` prompt text — clarify tool identity, single/multi patch format, CLI apply methods, and important failure rules
- [x] Tighten `src/sspec/builtin_tools/apply_patch.py` outside-workspace absolute path behavior — require confirmation by default and `--unsafe` for automated bypass
- [x] Fix preview scope rendering for open-ended line ranges and add regression coverage in `tests/test_tool_command.py`
- [x] Expand `src/sspec/builtin_tools/apply_patch.py` header parsing — support paths with spaces and keep outside-workspace warnings visible during `--dry-run`
- [x] Refine `src/sspec/builtin_tools/apply_patch.py` prompt wording — replace the abstract path-with-spaces note with a concrete absolute-path example

<!-- @RULE: Organize by phases. Each task <2h, independently testable.
Phase emoji: ⏳ pending | 🚧 in progress | ✅ done

### Phase 1: <name> ⏳
- [ ] Task description `path/file.py`
- [ ] Task description `path/file.py`
**Verification**: <how to verify this phase>

### Feedback Tasks
Use this section for review/feedback tasks that still belong to the current change.
If accepted feedback changes scope/design, update `spec.md` first, then add the execution work here.
If the work should become a new follow-up or replacement change, do not put it here unless the user has first approved that direction via `@align`.
-->

---

## Progress

**Overall**: 100%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 100% | ✅ |
| Phase 2 | 100% | ✅ |
| Phase 3 | 100% | ✅ |

**Recent**:
- 2026-03-17: Implemented `--stdin`, absolute/open-ended path parsing, and focused parser tests for patch tool hardening.
- 2026-03-17: Added retry-aware statuses, line-numbered failure output, markdown bundle output, and command-level regression coverage.
- 2026-03-17: Shortened the patch prompt and expanded `--stdin` examples to cover both bash and PowerShell.
- 2026-03-17: Reorganized the patch prompt around tool identity, patch format, CLI usage, and important rules.
- 2026-03-17: Added outside-workspace absolute path confirmation plus `--unsafe`, and fixed open-ended range preview output.
- 2026-03-17: Added support for space-containing patch paths and moved outside-workspace warnings ahead of `--dry-run` exit.
- 2026-03-17: Replaced the ambiguous path-with-spaces wording in `patch --prompt` with a concrete full-path example.
