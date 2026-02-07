# SSPEC Checklists Reference

Quick-reference checklists for key checkpoints. Load this at the relevant moment rather than reading the full SKILL.

---

## Starting New Change

- [ ] Assessed: Single vs multi-change? (≤15 files & ≤20 tasks → single)
- [ ] If multi-change: Created root change first (`--root`)?
- [ ] Spec.md Section A: Problem quantified with metrics?
- [ ] Spec.md Section B: Solution approach + rationale stated?
- [ ] Spec.md Section C: File-level task breakdown (single/sub) or phase breakdown (root)?
- [ ] Tasks.md: Each task <2h with verification criteria (single/sub)?
- [ ] Handover.md: Initial context documented?
- [ ] Reference field: Linked to originating request (if applicable)?
- [ ] If sub-change: Linked to root via `type: "root-change"` reference?

## Before Transitioning to REVIEW

- [ ] All tasks marked `[x]` in tasks.md?
- [ ] All phase verification criteria met?
- [ ] Handover.md reflects completion?
- [ ] Spec.md Section D: No undocumented blockers?
- [ ] Code tested and passing?
- [ ] If this change modifies architecture: corresponding spec-doc updated?

## Before @handover (End of Session)

- [ ] Handover.md: "Accomplished" updated?
- [ ] Handover.md: "Next Steps" clear (1-3 specific actions)?
- [ ] Handover.md: "Conventions" updated if new patterns found?
- [ ] Tasks.md: Progress percentage updated?
- [ ] Spec.md: Status accurate?

## Before Archiving Root Change

- [ ] All sub-changes archived?
- [ ] Root tasks.md: All milestones marked `[x]`?
- [ ] Coordination notes captured in reference/ (if valuable for future)?
- [ ] Linked spec-docs up to date?
