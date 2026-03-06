---
change: "handover-template-v2"
updated: ""
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks
### Phase 1: Redesign Handover Templates ⏳
- [x] Update `src/sspec/templates/change/handover.md` - replace "This Session" with append-only Session Log (timestamp + tag + short title)
- [x] Update `src/sspec/templates/change/handover.md` - make Decisions/Notes timestamped and clarify stable vs volatile
- [x] Update `src/sspec/templates/change-root/handover.md` - same structure + keep a volatile Sub-Change Status snapshot table
- [x] Update `src/sspec/templates/skills/sspec-handover/SKILL.md` - enforce atomic log entries + user-feedback/argue entries
- [x] (Optional) Update `src/sspec/templates/AGENTS.md` - add a short note: resume via Session Log
**Verification**: Generate a fresh change and confirm resume from the latest log entry is <30s and append-only works.

### Phase 2: Reinstall + Sandbox Smoke Test ⏳
- [x] Run `uv pip install -e .` to refresh template cache
- [x] In `tmp/`, create a clean test project and run:
      - `uv run sspec project init`
      - `uv run sspec change new demo`
      - `uv run sspec change new demo-root --root`
    Verify the generated handover templates match the new structure.
**Verification**: New handover has Session Log format + timestamped Decisions/Notes + root snapshot table.

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
**Overall**: 100%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 100% | ✅ |
| Phase 2 | 100% | ✅ |

**Recent**:
- Updated handover templates + `sspec-handover` SKILL
- Reinstalled and validated templates in `tmp/test_handover_template_v2`
