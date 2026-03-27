# Handover: {{CHANGE_NAME}}

**Updated**: <!-- ISO timestamp (minute precision), e.g. 2026-03-06T20:39 -->

---

## Background
<!-- Write once. What this root change coordinates (1-3 sentences). -->

## Git Baseline (Immutable)
<!-- Captured during `sspec change new` before any change files are written.
This section records the root change starting point in git and MUST NOT be edited or refreshed later. -->

{{GIT}}

## Sub-Change Status (Volatile Snapshot)

<!-- Snapshot of current coordination state. Update when it changes.-->
| Phase | Sub-Change | Status | Notes |
|-------|------------|--------|------|
| Phase 1 | `changes/<sub-name>/` | DOING | ... |


## Working Memory (Stable)
<!-- Curated, long-lived coordination context.
If something becomes obsolete, mark it as obsolete with a timestamp instead of deleting silently. -->

### Key Sub-Changes
<!-- Critical sub-change locations.
- `changes/<sub-name>/` - what this sub-change covers -->

### Key Files
<!-- Cross-phase files/docs that matter for coordination.
- `path/file` - what it contains, why it matters -->

### Durable Memory (Typed, Timestamped)
<!-- Promote only facts still useful across coordination sessions.
Root change preferred types: Alignment, CoordinationDecision, Dependency, CrossChangeFinding, Constraint, Risk, VerificationShortcut.
Use a custom type only when none fit well; keep it short and clear.
- [2026-03-06T20:39] [Alignment] User approved the current phase split.
- [2026-03-06T20:39] [CoordinationDecision] Phase 2 depends on Phase 1 stabilization.
- [2026-03-06T20:39] [CrossChangeFinding] Both sub-changes depend on the same config migration rule.
- [2026-03-06T20:39] [Constraint] Sub-Change Status remains the volatile coordination snapshot.
Project-wide items -> ALSO append to project.md Notes. -->

## Session Log (Append-Only)
<!-- Newest entry first. Each entry is an atomic batch (one cohesive work record).

Header format:
### 2026-03-06T20:39 [coordination] <short title>

Tags are freeform but SHOULD be readable. Examples: coordination, user-feedback, argue, risk.
Any user interaction (feedback, @align, @argue) MUST start a new log entry. -->

### <ISO timestamp> [tag] <short title>

**Accomplished**
- ...

**Next**
- ...

**Notes** (optional)
- ...
