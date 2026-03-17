---
change: "design-template"
updated: ""
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Howto Infrastructure ✅
- [x] Add `type: str | None = None` field to `HowtoInfo` dataclass in `src/sspec/services/howto_service.py`
- [x] Parse `type` from frontmatter in `collect_howtos()` in `src/sspec/services/howto_service.py`
- [x] Add `--type` filter option to `list_cmd` in `src/sspec/commands/howto.py`
- [x] Show type column in list output when typed howtos exist in `src/sspec/commands/howto.py`
**Verification**: ✅ `--type design-dimension` returns empty; `list` works as before

### Phase 2: Dimension Howto Cards ✅
- [x] Create `src/sspec/howto/write-dim-outcome-preview.md`
- [x] Create `src/sspec/howto/write-dim-interface-contract.md` (absorb old Rule 1 examples)
- [x] Create `src/sspec/howto/write-dim-structural-blueprint.md` (absorb old Rule 2 for structure)
- [x] Create `src/sspec/howto/write-dim-behavioral-spec.md` (absorb old Rule 2 for flow)
- [x] Create `src/sspec/howto/write-dim-data-architecture.md`
- [x] Create `src/sspec/howto/write-dim-content-outline.md`
- [x] Create `src/sspec/howto/write-dim-migration-path.md`
- [x] Create `src/sspec/howto/write-dim-impact-map.md` (absorb old Rule 3 Scope Summary as primary form)
**Verification**: ✅ `sspec howto list --type design-dimension` shows all 8; `sspec howto write-dim-interface-contract` prints card body

### Phase 3: SKILL Rewrite ✅
- [x] Rewrite Step 3A in `src/sspec/templates/skills/sspec-design/SKILL.md`: replace fixed sub-sections with predictability dimensions menu + meta-thinking guidance
- [x] Elevate Scope Summary + Item Labeling as universal rules at Key Design level in SKILL.md
- [x] Remove old Presentation Rules section (Rule 1-4 block) from SKILL.md; reference dimension howtos instead
- [x] Update References table at end of SKILL.md to point to new example files
**Verification**: ✅ Step 3A presents dimension menu, universal rules, howto references; no fixed Interface Design/Data Flow/Key Logic

### Phase 4: Examples Reorganization ✅
- [x] Create `src/sspec/templates/skills/sspec-design/examples-feature.md` (Feature/Bugfix scenario)
- [x] Create `src/sspec/templates/skills/sspec-design/examples-docs.md` (Protocol/Template/Docs scenario)
- [x] Create `src/sspec/templates/skills/sspec-design/examples-refactor.md` (Refactor/Migration scenario)
- [x] Delete `src/sspec/templates/skills/sspec-design/examples-single.md`
**Verification**: ✅ Three new files created; old file deleted; SKILL References table links to new files

### Phase 5: Template Comment Update ✅
- [x] Update `### Key Design` comment in `src/sspec/templates/change/spec.md` per spec.md Change F
**Verification**: ✅ Comment references dimension menu + universal rules

### Phase 6: Sync & Smoke Test ✅
- [x] `uv pip install -e .` to refresh template cache
- [x] `uv run sspec project update` to sync self-hosted copies
- [x] `uv run ruff check src/` + `uv run ruff format src/`
- [x] Smoke test in `tmp/`: `uv run sspec project init` → verify generated spec.md has new comment
- [x] `uv run sspec howto list --type design-dimension` → verify 8 cards listed
**Verification**: ✅ Clean lint, init produces updated template, howto filter works

### Feedback Tasks
- [x] Tighten the simple-change threshold to `<=3 files` and make `### Key Design` guidance scale-aware in `src/sspec/templates/skills/sspec-design/SKILL.md` and `src/sspec/templates/change/spec.md`
- [x] Align example reference paths with the `.sspec/...` convention and add an explicit large-change `reference/design.md` example in `src/sspec/templates/skills/sspec-design/examples-*.md`
- [x] Move research-stage ambiguity cleanup into `src/sspec/templates/skills/sspec-research/SKILL.md` Exit Criteria and remove aggressive `Grill User` wording
- [x] Expand `tests/test_howto_command.py` to cover builtin typed HOWTOs and rich output for `howto list --type`

---

## Progress
<!-- @REPLACE -->

**Overall**: 100%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1: Howto Infrastructure | 100% | ✅ |
| Phase 2: Dimension Howto Cards | 100% | ✅ |
| Phase 3: SKILL Rewrite | 100% | ✅ |
| Phase 4: Examples Reorganization | 100% | ✅ |
| Phase 5: Template Comment Update | 100% | ✅ |
| Phase 6: Sync & Smoke Test | 100% | ✅ |

**Recent**:
- Completed: All 6 phases implemented and verified
- Completed: Audit-driven follow-up polish for scale guidance, examples, research exit criteria, and HOWTO filter coverage
