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

### Phase 3: SKILL Rewrite ⏳
- [ ] Rewrite Step 3A in `src/sspec/templates/skills/sspec-design/SKILL.md`: replace fixed sub-sections with predictability dimensions menu + meta-thinking guidance
- [ ] Elevate Scope Summary + Item Labeling as universal rules at Key Design level in SKILL.md
- [ ] Remove old Presentation Rules section (Rule 1-4 block) from SKILL.md; reference dimension howtos instead
- [ ] Update References table at end of SKILL.md to point to new example files
**Verification**: Read SKILL.md; Step 3A should present dimension menu, universal rules, and howto references; no mention of fixed Interface Design/Data Flow/Key Logic sub-sections

### Phase 4: Examples Reorganization ⏳
- [ ] Create `src/sspec/templates/skills/sspec-design/examples-feature.md` (Feature/Bugfix scenario)
- [ ] Create `src/sspec/templates/skills/sspec-design/examples-docs.md` (Protocol/Template/Docs scenario)
- [ ] Create `src/sspec/templates/skills/sspec-design/examples-refactor.md` (Refactor/Migration scenario)
- [ ] Delete `src/sspec/templates/skills/sspec-design/examples-single.md`
**Verification**: SKILL.md References table links to three new files + examples-root.md; old examples-single.md gone

### Phase 5: Template Comment Update ⏳
- [ ] Update `### Key Design` comment in `src/sspec/templates/change/spec.md` per spec.md Change F
**Verification**: Read spec.md template; comment references dimension menu + universal rules

### Phase 6: Sync & Smoke Test ⏳
- [ ] `uv pip install -e .` to refresh template cache
- [ ] `uv run sspec project update` to sync self-hosted copies
- [ ] `uv run ruff check src/` + `uv run ruff format src/`
- [ ] Smoke test in `tmp/`: `uv run sspec project init` → verify generated spec.md has new comment
- [ ] `uv run sspec howto list --type design-dimension` → verify 8 cards listed
**Verification**: Clean lint, init produces updated template, howto filter works

### Feedback Tasks

---

## Progress
<!-- @REPLACE -->

**Overall**: 0%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1: Howto Infrastructure | 0% | ⏳ |
| Phase 2: Dimension Howto Cards | 0% | ⏳ |
| Phase 3: SKILL Rewrite | 0% | ⏳ |
| Phase 4: Examples Reorganization | 0% | ⏳ |
| Phase 5: Template Comment Update | 0% | ⏳ |
| Phase 6: Sync & Smoke Test | 0% | ⏳ |

**Recent**:
- (none yet)
