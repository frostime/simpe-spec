---
change: "add-howto-cli"
updated: ""
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks
### Phase 1: Finalize design records and HOWTO paths 🚧
- [x] Normalize `### Key Logic` wording in `.sspec/changes/26-03-09T23-41_add-howto-cli/spec.md`
- [x] Add HOWTO path support in `src/sspec/core.py` and project init plumbing in `src/sspec/services/project_init_service.py`
**Verification**: `spec.md` matches the approved design language; new project initialization creates `.sspec/howto/`.

### Phase 2: Implement HOWTO discovery and CLI ⏳
- [x] Add HOWTO discovery/scaffolding service in `src/sspec/services/howto_service.py`
- [x] Add `sspec howto` command flow in `src/sspec/commands/howto.py` and register it in `src/sspec/cli.py`
- [x] Add builtin HOWTO markdown files under `src/sspec/howto/`
**Verification**: `sspec howto list`, `sspec howto <name>`, and `sspec howto new <name>` work against builtin and project HOWTOs.

### Phase 3: Test and validate end-to-end ⏳
- [x] Add coverage in `tests/test_howto_command.py`
- [x] Extend `tests/test_project_init_service.py` for `.sspec/howto/`
- [x] Run targeted pytest for HOWTO-related tests and fix any regressions
**Verification**: target pytest suite passes without new failures.

### Feedback Tasks 🚧
- [x] Switch `src/sspec/commands/howto.py` to plain-text default output with optional rich formatting
- [x] Update HOWTO help text in `src/sspec/commands/howto.py` to document implicit `sspec howto <name>` reads
- [x] Rewrite `tests/test_howto_command.py` so it does not rely on specific builtin HOWTO content
- [x] Accept `--format` after `list` and `read` subcommands in `src/sspec/commands/howto.py`
- [x] Change plain `list` output in `src/sspec/commands/howto.py` to YAML-like records without `file`
- [x] Remove top-level headings from HOWTO source docs and scaffolds in `src/sspec/howto/*.md` and `src/sspec/services/howto_service.py`
- [x] Allow `src/sspec/commands/howto.py` to read multiple HOWTO names in one invocation
- [x] Remove plain read metadata output in `src/sspec/commands/howto.py` and replace it with lightweight separators between documents
**Verification**: `sspec howto --help` documents the shorthand, default output is plain text, and targeted tests still pass.

<!-- @RULE: Organize by phases. Each task <2h, independently testable.
Phase emoji: ⏳ pending | 🚧 in progress | ✅ done

### Phase 1: <name> ⏳
- [ ] Task description `path/file.py`
- [ ] Task description `path/file.py`
**Verification**: <how to verify this phase>

### Feedback Tasks
Use this section for tasks added during review/feedback loop.
-->

---

## Progress
<!-- @REPLACE -->

**Overall**: 100%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 100% | ✅ |
| Phase 2 | 100% | ✅ |
| Phase 3 | 100% | ✅ |
| Feedback | 100% | ✅ |

**Recent**:
- Completed: Normalize `### Key Logic` wording in `spec.md`
- Completed: Add HOWTO path helpers in `src/sspec/core.py` and create `.sspec/howto/` during project init
- Completed: Add HOWTO service, command registration, and builtin HOWTO documents
- Completed: Add HOWTO command tests and project init coverage for `.sspec/howto/`
- Completed: Run targeted ruff/pytest validation for the HOWTO feature
- Added: review feedback tasks for plain-text default output, help text, and less brittle tests
- Completed: Switch HOWTO list/read defaults to plain text and document rich formatting opt-in
- Completed: Remove brittle test dependence on specific builtin HOWTO documents
- Added: second-round feedback tasks for YAML-like plain output, post-subcommand `--format`, headerless HOWTO docs, and multi-read support
- Completed: Support `--format` after subcommands, YAML-like plain output, headerless source docs, and multi-read
- Added: final read-output cleanup task to drop plain frontmatter-style metadata
- Completed: Switch plain read output to `=== name ===` separators with larger gaps between multiple docs
