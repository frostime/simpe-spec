# Handover: {{CHANGE_NAME}}

**Updated**: <!-- ISO timestamp (minute precision), e.g. 2026-03-06T20:39 -->

---

## Background
<!-- Write once on first session. What this change does and why (1-3 sentences).
Update only if scope fundamentally changes. Details belong in spec.md. -->

## Git Baseline (Immutable)
<!-- Captured during `sspec change new` before any change files are written.
This section records the change starting point in git and must not be edited or refreshed later. -->

{{GIT}}

## Working Memory (Stable)
<!-- Curated, long-lived context. Survives context compression and session boundaries.
If something becomes obsolete, mark it as obsolete with a timestamp instead of deleting silently. -->

### Key Files
<!-- Files critical to understanding/continuing this change.
- `path/file` - what it contains, why it matters -->

### Durable Memory (Typed, Timestamped)
<!-- Promote only facts still useful after the current batch ends.
Single/sub change preferred types: Alignment, Decision, VitalFinding, Constraint, Risk, VerificationShortcut.
Use a custom type only when none fit well; keep it short and clear.
- [2026-03-06T20:39] [Decision] Redis over Memcached because per-key TTL + persistence matter.
- [2026-03-06T20:39] [Constraint] Session Log stays append-only; real next action lives there.
Project-wide items -> ALSO append to project.md Notes. -->

## Session Log (Append-Only)
<!-- Newest entry first. Each entry is an atomic batch (one cohesive work record).

Header format:
### 2026-03-06T20:39 [work-log] <short title>

Tags are freeform but must be readable. Examples: work-log, user-feedback, argue, risk.
Any user interaction (feedback, @align, @argue) MUST start a new log entry. -->

### <ISO timestamp> [tag] <short title>

**Accomplished**
- ...

**Next**
- ...

**Notes** (optional)
- ...
