---
change: "rename-research-to-clarify"
updated: ""
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Rename + Rewrite sspec-clarify SKILL ✅
- [x] Rename `templates/skills/sspec-research/` → `templates/skills/sspec-clarify/`
- [x] Rewrite `sspec-clarify/SKILL.md` — 正反合结构 + posture + memory management
**Verification**: frontmatter name = `sspec-clarify`, content has Subjective/Objective/Synthesis workflow

### Phase 2: Refactor sspec-align SKILL ✅
- [x] Remove §1 Requirement Restoration from `sspec-align/SKILL.md`
- [x] Renumber remaining sections (§2→§1, §3→§2, etc.)
**Verification**: sspec-align has no "Requirement Restoration" section, sections start from §1 Levels

### Phase 3: Update AGENTS.md lifecycle ✅
- [x] `Research → sspec-research` → `Clarify → sspec-clarify` (posture annotation + output change)
**Verification**: `rg Research src/sspec/templates/AGENTS.md` returns 0 phase-related hits

### Phase 4: Update all references ✅
- [x] `templates/skills/sspec-design/SKILL.md` — ref + Step 2 入口调整
- [x] `templates/requests/requests.md` — `sspec-research` → `sspec-clarify`
- [x] `templates/skills/sspec-implement/SKILL.md` — add "Clarify posture" mention
- [x] `templates/skills/sspec-review/SKILL.md` — Amend path: "re-enter Clarify posture"
**Verification**: `rg sspec-research src/sspec/templates/` returns 0 results

### Phase 5: Reinstall + Verify ✅
- [x] `uv pip install -e .` + `uv run ruff check src/`
- [x] Sandbox test: `sspec project init` → verify installed skills include `sspec-clarify`
**Verification**: No lint errors, no `sspec-research` in generated output

---

## Progress
<!-- @REPLACE -->

**Overall**: 100%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 100% | ✅ |
| Phase 2 | 100% | ✅ |
| Phase 3 | 100% | ✅ |
| Phase 4 | 100% | ✅ |
| Phase 5 | 100% | ✅ |

**Recent**:
- Completed: All 5 phases
