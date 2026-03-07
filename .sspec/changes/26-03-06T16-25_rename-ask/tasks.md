---
change: "rename-ask"
updated: "2026-03-06T22:50"
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Template & SKILL Changes ✅
- [x] Rename `src/sspec/templates/skills/sspec-ask/` → `sspec-align/`
- [x] Update SKILL.md frontmatter `name: sspec-ask` → `name: sspec-align`
- [x] Update `src/sspec/templates/AGENTS.md` — `@ask` → `@align`, section rename, SKILL ref
- [x] Update `src/sspec/templates/skills/sspec-design/SKILL.md`
- [x] Update `src/sspec/templates/skills/sspec-plan/SKILL.md`
- [x] Update `src/sspec/templates/skills/sspec-implement/SKILL.md`
- [x] Update `src/sspec/templates/skills/sspec-review/SKILL.md`
- [x] Update `src/sspec/templates/skills/sspec-handover/SKILL.md`
- [x] Update `src/sspec/templates/skills/sspec-research/SKILL.md`
- [x] Update `src/sspec/templates/change/handover.md` and `change-root/handover.md`
**Verification**: No stray `@ask` directives in templates ✓

### Phase 2: Dev-time Skills ✅
- [x] Update `.github/skills/sspec-ask/SKILL.md` content (name, description, title)
**Verification**: Dev-time SKILL content updated ✓

### Phase 3: Reinstall & Update ✅
- [x] Run `uv pip install -e .`
- [x] Run `sspec project update` — orphaned `sspec-ask` removed, `sspec-align` created, root AGENTS.md updated
- [x] Update dev section of root `AGENTS.md` (Section 4 “sspec-ask for Development”)
**Verification**: Root AGENTS.md updated with `@align` ✓

---

## Progress

**Overall**: 100%

| Phase | Progress | Status |
|-------|----------|---------|
| Phase 1: Template & SKILL | 100% | ✅ |
| Phase 2: Dev-time Skills | 100% | ✅ |
| Phase 3: Reinstall & Update | 100% | ✅ |
| Feedback Tasks | 100% | ✅ |

**Recent**:
- 2026-03-06: Compressed `sspec-align` from ~6.8k/216 lines to ~5.0k/140 lines, refined `@force-end-align` semantics, and re-synced root + sandbox projects.
- 2026-03-06: User accepted the change, marked request/spec DONE, and prepared commit scope excluding `.env`.
