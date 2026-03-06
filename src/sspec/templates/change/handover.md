# Handover: {{CHANGE_NAME}}

**Updated**: <!-- ISO timestamp (minute precision), e.g. 2026-03-06T20:39 -->

---

## Background
<!-- Write once on first session. What this change does and why (1-3 sentences).
Update only if scope fundamentally changes. Details belong in spec.md. -->

## Working Memory (Stable)
<!-- Curated, long-lived context. Survives context compression and session boundaries.
If something becomes obsolete, mark it as obsolete with a timestamp instead of deleting silently. -->

### Key Files
<!-- Files critical to understanding/continuing this change.
- `path/file` - what it contains, why it matters -->

### Decisions (Timestamped)
<!-- Timestamp every entry (minute precision).
- [2026-03-06T20:39] **Decision** - Redis over Memcached
  **Why**: Need per-key TTL + persistence -->

### Notes (Timestamped)
<!-- Gotchas, edge cases, risks, verification shortcuts. Timestamp every entry.
Project-wide items -> ALSO append to project.md Notes. -->

## Session Log (Append-Only)
<!-- Newest entry first. Each entry is an atomic batch (one cohesive work record).

Header format:
### 2026-03-06T20:39 [work-log] <short title>

Tags are freeform but must be readable. Examples: work-log, user-feedback, argue, risk.
Any user interaction (feedback, @ask, @argue) MUST start a new log entry. -->

### <ISO timestamp> [tag] <short title>

**Accomplished**
- ...

**Next**
- ...

**Notes** (optional)
- ...
