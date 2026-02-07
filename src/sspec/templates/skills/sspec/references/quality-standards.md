# Quality Standards Reference

Document quality standards and anti-patterns. Load when filling or reviewing spec.md, tasks.md, or handover.md.

---

## spec.md

| Section | Requirement | ❌ Fail | ✅ Pass |
|---------|-------------|---------|---------|
| A. Problem | Quantified impact | "Need to refactor" | "Auth takes 5s → 12% conversion drop" |
| B. Solution | Approach + rationale | "Use caching" | "JWT + Redis: DB→memory, <100ms target" |
| C. Implementation | File-level tasks | "Modify auth files" | "`src/auth/jwt.py` — create refresh_token()" |
| D. Blockers | Dated, actionable | "Waiting on DevOps" | "Blocker (01-27): Need Redis host:port" |

## tasks.md

| Criterion | Standard |
|-----------|----------|
| Granularity | Each task <2h, independently testable (single/sub); milestone-level (root) |
| Verification | Each phase has explicit pass criteria |
| Progress tracking | Update after completing EACH task |

## handover.md

| Field | Purpose | Bad Example | Good Example |
|-------|---------|-------------|--------------|
| Background | One-sentence overview | "Doing auth" | "JWT+Redis cache to reduce auth from 5s to <1s" |
| Accomplished | What's done this session | "Made progress" | "Phase 1 complete: redis pool + middleware" |
| Next Steps | 1-3 specific actions | "Continue" | "1. Code jwt.py:refresh_token() 2. Add expiry tests" |
| Conventions | Patterns discovered | (empty) | "Cache key: `auth:{user_id}`, TTL: 900s" |

**Quality test**: New Agent can resume in <30 seconds?

## Optional Directories

### reference/ (Design Iteration)

Use for **complex changes** needing design iteration before implementation.

| Use Case | File Example |
|----------|--------------|
| Architecture exploration | `design-draft.md` |
| API alternatives | `api-options.md` |
| Research notes | `research.md` |

**Workflow**: Draft in reference/ → Iterate via `@ask` → Finalize into spec.md A/B/C.

**Skip for**: Simple bug fixes, well-understood features.

### script/ (One-Off Tools)

Migrations, test data generators, analysis tools. Created during DOING, may promote to project-level if reusable.

---

## Anti-Patterns

| Bad Practice | Why It Fails | Correct Approach |
|--------------|--------------|------------------|
| Skip @handover | Next session re-discovers context | **ALWAYS** handover before ending |
| Mark `[x]` without testing | False progress, hidden bugs | Done = coded **AND** verified |
| No file paths in spec.md C | Agent guesses wrong files | List specific paths per task |
| Stay DOING when blocked | Waste time on workarounds | BLOCKED immediately + document |
| Skip REVIEW status | No user validation | DOING → REVIEW → DONE |
| Batch progress updates | Lose track of actual state | Update after **each** task |
| Over-use reference/ | Wasted effort on simple changes | Reserve for complex design |
| Forget reference field | Lost traceability | Use CLI auto-link or add manually |
| Create change for trivial fix | Ceremony overhead > actual work | Micro: do directly or track in request |
| Put architecture in project.md | Should be scannable in 10s | Use spec-docs for complex knowledge |
| Forget to write Notes | Learnings lost between sessions | Append project-level discoveries to project.md |
