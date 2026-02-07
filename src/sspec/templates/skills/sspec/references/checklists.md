# Checklists

Quick verification at key checkpoints. Load at the relevant moment.

---

## Starting New Work

- [ ] Assessed scale: Micro / Single / Multi?
- [ ] If micro (≤3 files, ≤30min): skip change, do directly or track in request
- [ ] If multi: root change created first (`--root`)?
- [ ] spec.md A: problem quantified?
- [ ] spec.md B: approach + rationale?
- [ ] spec.md C: file-level tasks (single/sub) or phases (root)?
- [ ] tasks.md: each task <2h with pass criteria?
- [ ] Reference field: linked to originating request?
- [ ] If sub-change: linked to root via `type: "root-change"`?

## Before REVIEW

- [ ] All tasks `[x]` in tasks.md?
- [ ] Verification criteria met?
- [ ] handover.md reflects completion?
- [ ] spec.md D: no undocumented blockers?
- [ ] Code tested and passing?
- [ ] Architecture change? → spec-doc updated?

## Before @handover

- [ ] handover.md "Accomplished" updated?
- [ ] handover.md "Next Steps" clear (1-3 specific actions)?
- [ ] handover.md "Key Files" — all critical files listed?
- [ ] handover.md "Decisions & Rationale" — non-obvious choices captured with reasoning?
- [ ] handover.md "Gotchas & Context" — edge cases, risks, implicit knowledge recorded?
- [ ] tasks.md progress percentage updated?
- [ ] spec.md status accurate?
- [ ] Project-level learnings → appended to project.md Notes?

## Mid-Session Memory Check

Trigger: session getting long (>50 exchanges), complex multi-file work, or extensive discussion/design.

- [ ] Any important decision in recent messages not yet in handover?
- [ ] Any key file paths discussed but not recorded in Key Files?
- [ ] Any design rationale that would be hard to reconstruct from compressed context?
- [ ] Any gotcha, risk, or edge case discovered but not written down?

→ If yes to any: update handover.md "References & Memory" now. Quick append, no ceremony.

## Before Archiving Root

- [ ] All sub-changes archived?
- [ ] Root tasks.md: all milestones `[x]`?
- [ ] Valuable coordination notes preserved in reference/?
- [ ] Linked spec-docs up to date?
