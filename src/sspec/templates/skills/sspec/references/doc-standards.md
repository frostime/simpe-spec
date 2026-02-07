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

handover.md serves **dual purposes**: cross-session handover AND intra-session working memory.

### Core Fields

| Field | Purpose | Bad | Good |
|-------|---------|-----|------|
| Background | One-sentence overview | "Doing auth" | "JWT+Redis cache: 5s→<1s auth" |
| Accomplished | This session's work | "Made progress" | "redis pool + middleware done" |
| Next Steps | 1-3 specific actions | "Continue" | "1. Code jwt.py:refresh_token()" |

### References & Memory Fields

| Field | Purpose | Bad | Good |
|-------|---------|-----|------|
| Key Files | Critical file references | (empty) | "`src/auth/jwt.py` — token logic; `asks/260207_auth.md` — confirmed JWT approach" |
| Decisions & Rationale | Choices + full reasoning | "Use Redis" | "**Redis over Memcached**: need per-key TTL + persistence. Memcached faster but no TTL granularity → stale tokens." |
| Gotchas & Context | Non-obvious findings, risks | (empty) | "Redis SCAN cursor resets on topology change; use KEYS only in dev. Risk: cluster mode not tested yet." |

### Quality Tests

1. **Cross-session**: Can a new Agent resume in <30 seconds?
2. **Intra-session**: If context were compressed right now, could you continue from handover.md alone?

### Update Frequency

| Content | When to write |
|---------|---------------|
| Key Files | Immediately when a critical file is identified |
| Decisions & Rationale | Immediately when a non-trivial decision is made |
| Gotchas & Context | Immediately when discovered |
| Accomplished & Next Steps | At session end (minimum) |

**Rule**: If you'd struggle to reconstruct this information after context compression, write it down NOW.

### Depth Guidance

**Thin memory** (simple change): 3-5 bullet points total across the three sections. Don't force content.

**Rich memory** (complex change with many decisions): Organize into numbered items with sub-structure. See this pattern for Decisions & Rationale:

```markdown
#### 1. Why current approach fails?
**Root cause**: Format too strict for model output...
**Evidence**: 3/10 attempts produce valid format...

#### 2. Why SEARCH/REPLACE over alternatives?
**Three advantages**: (1) simpler format (2) model familiarity (3) token savings...
**Tradeoff**: Less precise than line-based diff, acceptable because BlockID handles positioning...
```

Let content grow organically — don't pre-structure what you don't need.

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
| Only update handover at session end | Update References & Memory **during** work |
| Record decision without reasoning | Capture full chain: problem → alternatives → conclusion |
| Mark `[x]` without testing | Done = coded **AND** verified |
| No file paths in spec.md C | List specific `path:function()` per task |
| No file paths in handover Key Files | List files you'd need to re-find after compression |
| Stay DOING when blocked | BLOCKED immediately + document in D |
| Skip REVIEW status | DOING → REVIEW → DONE, no shortcuts |
| Batch progress updates | Update tasks.md after **each** task |
| Create change for trivial fix | Micro: do directly or track in request |
| Put architecture in project.md | project.md ≤10s scan; use spec-docs |
| Forget Notes in @handover | Append project-level learnings to project.md |
