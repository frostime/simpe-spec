---
change: "portable-mode-agent-resources"
updated: "2026-05-09T21:20+08:00"
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Service + CLI ✅
- [x] Create `src/sspec/services/portable_service.py` — implement bootstrap rendering, skill index extraction, safe resource resolution, and read wrapper.
- [x] Create `src/sspec/commands/portable.py` — wire `sspec portable` and `sspec portable read <scope:slug>`.
- [x] Update `src/sspec/cli.py` — register portable command.
**Verification**: `uv run sspec portable` and representative `read` commands exit 0 outside an sspec project.

### Phase 2: Tests ✅
- [x] Add `tests/test_portable_service.py` — cover index shape, source metadata, rule rendering, safety errors.
- [x] Add `tests/test_portable_command.py` — cover CLI no-project behavior and read success/failure.
**Verification**: `uv run pytest tests/test_portable_service.py tests/test_portable_command.py` passes.

### Phase 3: Quality Gate ✅
- [x] Run focused CLI smoke checks in `tmp/`.
- [x] Run lint/format for changed source.
**Verification**: focused pytest passes; ruff check/format completes for changed files. Full `ruff check src/` currently reports pre-existing unrelated issues in `builtin_tools/context.py` and `builtin_tools/treesitter.py`.

---

## Progress

**Overall**: 100%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 100% | ✅ |
| Phase 2 | 100% | ✅ |
| Phase 3 | 100% | ✅ |

**Recent**:
- 2026-05-09T21:13+08:00 — Plan created after design approval.
- 2026-05-09T21:20+08:00 — Implemented portable command, resource reader, tests, focused lint/format, and CLI smoke checks.
- 2026-05-09T22:05+08:00 — Adjusted `read` source metadata to absolute local paths and re-ran focused tests.
