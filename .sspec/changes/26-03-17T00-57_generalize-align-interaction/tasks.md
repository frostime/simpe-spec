---
change: "generalize-align-interaction"
updated: ""
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Rewrite AGENTS.md §3 Alignment + cleanup ⏳
- [ ] Rewrite §3 Alignment: two-level report/gate, remove channel selection matrix, remove sspec ask references `src/sspec/templates/AGENTS.md`
- [ ] Remove `@force-end-align` paragraph from §3 `src/sspec/templates/AGENTS.md`
- [ ] Remove `sspec ask` from CLI Quick Reference table `src/sspec/templates/AGENTS.md`
- [ ] Strengthen Micro path description in §1 `src/sspec/templates/AGENTS.md`
- [ ] Update lifecycle diagram in §2: Design/Implement = gate, Plan = report `src/sspec/templates/AGENTS.md`
**Verification**: Read the full AGENTS.md template; no mention of sspec ask, @force-end-align, or channel selection matrix; @align clearly documented as report/gate two-level

### Phase 2: Rewrite sspec-align SKILL ⏳
- [ ] Rewrite §1 (When To Align) with report/gate classification `src/sspec/templates/skills/sspec-align/SKILL.md`
- [ ] Delete §2 (Choose the Channel) entirely `src/sspec/templates/skills/sspec-align/SKILL.md`
- [ ] Rewrite §3 (After Align) to remove sspec ask references `src/sspec/templates/skills/sspec-align/SKILL.md`
- [ ] Delete §4 (Use of sspec ask) entirely `src/sspec/templates/skills/sspec-align/SKILL.md`
- [ ] Delete §5 (@force-end-align) entirely `src/sspec/templates/skills/sspec-align/SKILL.md`
**Verification**: sspec-align SKILL is self-consistent with two-level model; no sspec ask, no force-end-align

### Phase 3: Update phase SKILLs ⏳
- [ ] `sspec-design`: keep exit as gate (hard stop for user confirmation), remove sspec ask references `src/sspec/templates/skills/sspec-design/SKILL.md`
- [ ] `sspec-plan`: change exit from mandatory gate to report `src/sspec/templates/skills/sspec-plan/SKILL.md`
- [ ] `sspec-implement`: keep exit as gate (hard stop for user review), remove sspec ask references `src/sspec/templates/skills/sspec-implement/SKILL.md`
- [ ] `sspec-review`: remove sspec ask references `src/sspec/templates/skills/sspec-review/SKILL.md`
- [ ] `sspec-research`: remove sspec ask references `src/sspec/templates/skills/sspec-research/SKILL.md`
- [ ] `sspec-handover`: remove sspec ask references `src/sspec/templates/skills/sspec-handover/SKILL.md`
**Verification**: grep all SKILL files for "sspec ask" — zero hits; Design/Implement exit = gate; Plan exit = report

### Phase 4: Delete HOWTO files ⏳
- [ ] Delete `force-end-align` HOWTO
- [ ] Delete `use-sspec-ask` HOWTO
- [ ] Delete `write-sspec-ask` HOWTO
**Verification**: `sspec howto list` no longer shows these three entries

### Phase 5: Sync and verify ⏳
- [ ] Run `uv pip install -e .` to reinstall
- [ ] Run `uv run sspec project update` to sync generated copies
- [ ] Verify generated AGENTS.md in project root matches template
- [ ] Verify generated SKILL files in `.sspec/skills/` match templates
**Verification**: `git diff` shows only expected changes; `sspec howto list` clean; no broken references

---

## Progress
<!-- @REPLACE -->

**Overall**: 0%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1: AGENTS.md | 0% | ⏳ |
| Phase 2: sspec-align SKILL | 0% | ⏳ |
| Phase 3: Phase SKILLs | 0% | ⏳ |
| Phase 4: Delete HOWTOs | 0% | ⏳ |
| Phase 5: Sync & verify | 0% | ⏳ |

**Recent**:
- (none yet)
