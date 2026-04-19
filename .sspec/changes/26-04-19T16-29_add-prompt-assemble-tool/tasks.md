---
change: "add-prompt-assemble-tool"
updated: ""
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Prompt service and source model ✅
- [x] Create source schema, inline source normalization, preset import/export, source resolution, and hybrid-header rendering with YAML frontmatter + fenced content in `src/sspec/services/prompt_service.py`
- [x] Implement tmp output path generation and prompt result write logic in `src/sspec/services/prompt_service.py`
- [x] Add focused service tests for file, file-chunk, glob, file-tree, shell gating, preset export, YAML frontmatter + fenced content rendering, and output writing in `tests/test_prompt_service.py`
**Verification**: `uv run pytest tests/test_prompt_service.py`

### Phase 2: Builtin CLI and interactive flow ✅
- [x] Add `src/sspec/builtin_tools/prompt.py` with inline `--add-*` flags, `--from-preset`, `--to-preset`, `--output`, `--dry-run`, `--allow-shell`, `--prompt`, and no-args interactive flow
- [x] Register the builtin in `src/sspec/commands/tool.py`
- [x] Extend CLI coverage for prompt registration, `--prompt`, inline run, preset import/export, and dry-run behavior in `tests/test_tool_command.py`
**Verification**: `uv run pytest tests/test_tool_command.py -k prompt`

### Phase 3: Spec-doc sync and end-to-end verification ✅
- [x] Update `.sspec/spec-docs/builtin-tools.md` with prompt tool contract, inline flags, preset path, source types, and output format
- [x] Run editable reinstall plus targeted lint/format for touched Python files
- [x] Verify the tool manually in `tmp/` with one inline run and one preset export/import run
**Verification**: `uv pip install -e . && uv run ruff check src/sspec/builtin_tools/prompt.py src/sspec/services/prompt_service.py src/sspec/services/tmp_service.py tests/test_prompt_service.py tests/test_tool_command.py && uv run ruff format src/sspec/builtin_tools/prompt.py src/sspec/services/prompt_service.py src/sspec/services/tmp_service.py tests/test_prompt_service.py tests/test_tool_command.py && uv run pytest tests/test_prompt_service.py tests/test_tool_command.py -k "prompt"`

---

## Progress

**Overall**: 100%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 100% | ✅ |
| Phase 2 | 100% | ✅ |
| Phase 3 | 100% | ✅ |

**Recent**:
- [2026-04-19T17:35+08:00] Corrected design direction: inline `--add-*` generation is the primary runtime path; preset import/export is layered on top.
- [2026-04-19T18:45+08:00] Implemented `prompt_service.py` and passing service tests for source normalization, rendering, shell gating, preset export, and tmp output.
- [2026-04-19T18:55+08:00] Implemented builtin `prompt` CLI and passing prompt-focused command tests.
- [2026-04-19T19:02+08:00] Updated builtin-tools spec-doc and completed targeted manual verification in `tmp/test_prompt_tool`.
- [2026-04-19T19:16+08:00] Hardened gitignore scanning with `os.walk(..., followlinks=False, onerror=...)` and added regression coverage for broken-link traversal.
