# Handover: meta-update-hardening

**Updated**: 2026-03-03

---

## Background

Hardening pass after the meta schema v2 work: fix review findings around meta schema strictness, `project update` correctness under `unknown`/missing hashes, and path normalization/validation issues.

## This Session

### Accomplished

- Created new change and wrote spec/tasks/handover to capture review findings and intended fixes.
- Linked full audit notes in `reference/last-audit-report.md` and referenced it from `spec.md`.

### Next Steps

- Implement schema strictness rules in `src/sspec/services/meta_service.py`.
- Fix the duplicate return bug in `src/sspec/services/skill_service.py`.
- Adjust `project update` messaging + hash backfill behavior in `src/sspec/commands/project.py`.
- Normalize `skill_locations` path separators to POSIX and validate user-provided locations/names.

Implementation entry point:
- Resume via: `.sspec/changes/26-03-03T22-19_meta-update-hardening/spec.md`
- Use audit notes: `.sspec/changes/26-03-03T22-19_meta-update-hardening/reference/last-audit-report.md`

## Working Memory
<!-- Agent's external memory. Survives context compression and session boundaries.
Update PROACTIVELY: important decision, key file found, non-obvious insight.
Test: "Would I struggle to reconstruct this after losing context?" → Write NOW. -->

### Key Files

- `.sspec/changes/26-03-03T22-19_meta-update-hardening/spec.md` — problem statement + proposed solution
- `.sspec/changes/26-03-03T22-19_meta-update-hardening/tasks.md` — task breakdown + verification steps
- `src/sspec/services/meta_service.py` — meta schema parsing + migrations
- `src/sspec/commands/project.py` — project update behavior + meta persistence
- `src/sspec/services/project_update_service.py` — `prepare_meta_for_project_update()` stage
- `src/sspec/commands/skill.py` / `src/sspec/services/skill_service.py` — dominate/new skill behaviors

### Decisions

- **Strict schema policy**: declared-but-unparseable schema markers must error (do not treat as `0.0`).
  **Why**: prevents accidental destructive migrations on unknown schema strings.
- **Update truthfulness**: do not claim "up to date" if update is blocked by `unknown`/missing hashes.
  **Why**: avoids misleading users and keeps update pipeline actionable.

### Notes

- Review found a definite bug: duplicate/unreachable `return` in `create_skill_in_hub()`.
- `skill_locations` currently mixes Windows `\\` and POSIX `/` separators; normalize to POSIX in meta.
- `skill dominate` currently resolves relative paths from CWD; should resolve relative to project root.
- `project update` can print "All files are up to date" while being blocked by `unknown` candidates when hashes are missing.
- Meta schema parsing currently treats declared-but-unparseable versions as `0.0`; should error instead.
