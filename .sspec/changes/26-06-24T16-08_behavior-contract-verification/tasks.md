---
change: "behavior-contract-verification"
updated: 2026-06-24T16:30+08:00
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Templates and Skills 🚧
- [ ] Update spec/task templates per `Behavior Contract`, `Implementation Changes`, `User Check`, and `Effort` design `src/sspec/templates/change/spec.md` `src/sspec/templates/change-root/spec.md` `src/sspec/templates/change/tasks.md`
- [ ] Update lifecycle skills to teach the new boundaries and final review recipe `src/sspec/templates/skills/sspec-design/SKILL.md` `src/sspec/templates/skills/sspec-plan/SKILL.md` `src/sspec/templates/skills/sspec-implement/SKILL.md` `src/sspec/templates/skills/sspec-review/SKILL.md`
**Verification**:
- Agent: `asq md-toc` shows the target headings in changed templates/skills.
- User Check: BC-1/BC-2/BC-3/BC-4/BC-5 are represented in generated template guidance.

### Phase 2: Examples and Tests ⏳
- [ ] Update design and plan examples from `Key Change` to behavior contract plus changelog-style implementation labels `src/sspec/templates/skills/sspec-design/examples-*.md` `src/sspec/templates/skills/sspec-plan/examples.md`
- [ ] Update template structure tests to assert `Behavior Contract`, `Implementation Changes`, and `File | Change | Effort` `tests/`
**Verification**:
- Agent: targeted tests for template/change creation pass.
- User Check: BC-1/BC-3 examples show behavior spec separated from verification steps.

### Phase 3: Sync and Final Verification ⏳
- [ ] Reinstall editable package and sync self-hosted generated copies `uv pip install -e .` `uv run sspec project update`
- [ ] Run focused lint/tests and sandbox CLI checks for template generation
**Verification**:
- Agent: `uv run ruff check src/` passes.
- Agent: focused pytest for changed template expectations passes.
- Agent: sandbox `sspec project init` / `sspec change new` output contains the new spec/task structure.
- User Check: BC-4 final response includes verification results and review recipe.

### Feedback Tasks (→ [NNN-description](./revisions/NNN-description.md))
Use this section for review/feedback tasks that still belong to the current change.

---

## Progress

**Overall**: 0%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 0% | 🚧 |
| Phase 2 | 0% | ⏳ |
| Phase 3 | 0% | ⏳ |

**Recent**:
- 2026-06-24T16:30+08: Plan approved by user direction; implementation started.
