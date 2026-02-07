# Document Standards

Quality criteria for the three change documents. Load when filling or reviewing them.

---

## spec.md

| Section | Must have | ❌ Fail | ✅ Pass |
|---------|-----------|---------|---------|
| A. Problem | Quantified impact | "Need to refactor" | "Auth takes 5s → 12% conversion drop" |
| B. Solution | Approach + rationale | "Use caching" | "JWT + Redis: DB→memory, <100ms target" |
| C. Implementation | File-level tasks | "Modify auth files" | "`src/auth/jwt.py` — create refresh_token()" |
| D. Blockers | Dated, actionable | "Waiting on DevOps" | "Blocker (01-27): Need Redis host:port" |

**Root change spec.md**: Section C lists phases/sub-changes, not file-level tasks.

## tasks.md

| Criterion | Standard |
|-----------|----------|
| Granularity | Each task <2h, independently testable (single/sub); milestone-level (root) |
| Verification | Each task/phase has explicit pass criteria |
| Progress | Update after completing EACH task, not in batches |

## handover.md

| Field | Purpose | Bad | Good |
|-------|---------|-----|------|
| Background | One-sentence overview | "Doing auth" | "JWT+Redis cache: 5s→<1s auth" |
| Accomplished | This session's work | "Made progress" | "redis pool + middleware done" |
| Next Steps | 1-3 specific actions | "Continue" | "1. Code jwt.py:refresh_token()" |
| Conventions | Patterns discovered | (empty) | "Cache key: `auth:{user_id}`, TTL: 900s" |

**Quality test**: Can a new Agent resume in <30 seconds?

---

## Optional Directories

### reference/ (Design Iteration)

For complex changes needing exploration before implementation.

**Use for**: Architecture drafts, API comparisons, research notes.
**Workflow**: Draft → Iterate via `@ask` → Finalize into spec.md → Keep for record.
**Skip for**: Bug fixes, well-understood features.

### script/ (One-Off Tools)

Migrations, test data generators, analysis tools. Created during DOING. Promote to project-level if reusable, otherwise archive with change.

---

## Anti-Patterns

| Bad Practice | Correct Approach |
|--------------|------------------|
| Skip `@handover` | **ALWAYS** handover before ending |
| Mark `[x]` without testing | Done = coded **AND** verified |
| No file paths in spec.md C | List specific `path:function()` per task |
| Stay DOING when blocked | BLOCKED immediately + document in D |
| Skip REVIEW status | DOING → REVIEW → DONE, no shortcuts |
| Batch progress updates | Update tasks.md after **each** task |
| Create change for trivial fix | Micro: do directly or track in request |
| Put architecture in project.md | project.md ≤10s scan; use spec-docs |
| Forget Notes in @handover | Append project-level learnings to project.md |
