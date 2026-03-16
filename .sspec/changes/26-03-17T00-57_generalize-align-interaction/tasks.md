---
change: "generalize-align-interaction"
updated: "2026-03-17T02:02"
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Rewrite AGENTS.md §3 Alignment + cleanup ✅
- [x] Rewrite §3 Alignment: two-level report/gate, remove channel selection matrix, remove sspec ask references `src/sspec/templates/AGENTS.md`
- [x] Remove `@force-end-align` paragraph from §3 `src/sspec/templates/AGENTS.md`
- [x] Remove `sspec ask` from CLI Quick Reference table `src/sspec/templates/AGENTS.md`
- [x] Strengthen Micro path description in §1 `src/sspec/templates/AGENTS.md`
- [x] Update lifecycle diagram in §2: Design/Implement = gate, Plan = report `src/sspec/templates/AGENTS.md`
**Verification**: Read the full AGENTS.md template; no mention of sspec ask, @force-end-align, or channel selection matrix; @align clearly documented as report/gate two-level

### Phase 2: Rewrite sspec-align SKILL ✅
- [x] Rewrite §1 (When To Align) with report/gate classification `src/sspec/templates/skills/sspec-align/SKILL.md`
- [x] Delete §2 (Choose the Channel) entirely `src/sspec/templates/skills/sspec-align/SKILL.md`
- [x] Rewrite §3 (After Align) to remove sspec ask references `src/sspec/templates/skills/sspec-align/SKILL.md`
- [x] Delete §4 (Use of sspec ask) entirely `src/sspec/templates/skills/sspec-align/SKILL.md`
- [x] Delete §5 (@force-end-align) entirely `src/sspec/templates/skills/sspec-align/SKILL.md`
**Verification**: sspec-align SKILL is self-consistent with two-level model; no sspec ask, no force-end-align

### Phase 3: Update phase SKILLs ✅
- [x] `sspec-design`: keep exit as gate (hard stop for user confirmation), remove sspec ask references `src/sspec/templates/skills/sspec-design/SKILL.md`
- [x] `sspec-plan`: change exit from mandatory gate to report `src/sspec/templates/skills/sspec-plan/SKILL.md`
- [x] `sspec-implement`: keep exit as gate (hard stop for user review), remove sspec ask references `src/sspec/templates/skills/sspec-implement/SKILL.md`
- [x] `sspec-review`: remove sspec ask references `src/sspec/templates/skills/sspec-review/SKILL.md`
- [x] `sspec-research`: remove sspec ask references `src/sspec/templates/skills/sspec-research/SKILL.md`
- [x] `sspec-handover`: remove sspec ask references `src/sspec/templates/skills/sspec-handover/SKILL.md`
**Verification**: grep all SKILL files for "sspec ask" — zero hits; Design/Implement exit = gate; Plan exit = report

### Phase 4: Delete HOWTO files ✅
- [x] Delete `force-end-align` HOWTO
- [x] Delete `use-sspec-ask` HOWTO
- [x] Delete `write-sspec-ask` HOWTO
**Verification**: `sspec howto list` no longer shows these three entries

### Phase 5: Sync and verify ✅
- [x] Run `uv pip install -e .` to reinstall
- [x] Run `uv run sspec project update` to sync generated copies
- [x] Verify generated AGENTS.md in project root matches template
- [x] Verify generated SKILL files in `.sspec/skills/` match templates
**Verification**: `git diff` shows only expected changes; `sspec howto list` clean; no broken references

### Feedback Tasks ✅
- [x] Adjust align rules so complex context is emitted in normal output before using a `question`-like tool `src/sspec/templates/AGENTS.md`
- [x] Update `src/sspec/templates/skills/sspec-align/SKILL.md` to state that `question`-like tools should carry only the concise ask, not the full context
- [x] Commit the alignment-rule changes as an isolated checkpoint commit
- [x] Implement `sspec tool ask` and document `--prompt` usage in the CLI/help text
- [x] Update alignment docs to say: if no `question`-like tool exists, use `sspec tool ask`; detailed usage: `sspec tool ask --prompt`
- [x] Reinstall, sync templates, and verify generated copies after the tool-ask change
**Verification**: alignment docs are concise and consistent; `sspec tool ask --prompt` prints fallback usage; generated files stay in sync

---

## Progress
<!-- @REPLACE -->

**Overall**: 100%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1: AGENTS.md | 100% | ✅ |
| Phase 2: sspec-align SKILL | 100% | ✅ |
| Phase 3: Phase SKILLs | 100% | ✅ |
| Phase 4: Delete HOWTOs | 100% | ✅ |
| Phase 5: Sync & verify | 100% | ✅ |
| Feedback Tasks | 100% | ✅ |

**Recent**:
- Completed: Rewrite alignment model in `src/sspec/templates/AGENTS.md`
- Completed: Rewrite `src/sspec/templates/skills/sspec-align/SKILL.md`
- Completed: Remove ask/force-end-align HOWTOs under `src/sspec/howto/`
- Completed: Reinstall package and sync generated `AGENTS.md` / `.sspec/skills/`
- Completed: tighten question-tool guidance for `question`-like tools
- Completed: add `sspec tool ask` fallback and `--prompt` usage
- Verified: `uv run pytest tests/test_ask_command.py tests/test_ask_service.py` passed (29 passed)
- Completed: align `.sspec/spec-docs/interaction-records.md` with fallback/compat ask semantics
