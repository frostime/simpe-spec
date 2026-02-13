# Document Standards: spec.md & tasks.md

Quality criteria and filling guidance. Load when writing or reviewing these documents.

---

## spec.md

### Frontmatter Schema

```yaml
---
name: <change-name>           # Auto-filled by CLI
status: PLANNING               # PLANNING | DOING | REVIEW | DONE | BLOCKED
type: ""                       # User-defined label (optional)
change-type: single            # single | sub | root
created: <iso-timestamp>       # Auto-filled by CLI
reference: null                # Array<{source, type, note?}> or null
---
```

**`change-type`**:
- `single`: Standalone change (default)
- `sub`: Part of a multi-change; must have `reference` linking to root
- `root`: Coordinator for sub-changes; spec.md C lists phases, not file-level tasks

**`reference`** field types:

| RefType | Meaning | Example |
|---------|---------|---------|
| `request` | Originating user request | `{source: "requests/26-02-05_auth.md", type: "request"}` |
| `root-change` | Parent root change (used in sub) | `{source: "changes/auth-root", type: "root-change"}` |
| `sub-change` | Child sub-change (used in root) | `{source: "changes/auth-phase1", type: "sub-change"}` |
| `doc` | Related spec-doc | `{source: "spec-docs/auth-system.md", type: "doc"}` |

### Section Standards

#### A. Problem Statement

**Standard**: Quantify impact. Format: "[metric] causing [impact]".

| Scenario | Approach |
|----------|----------|
| Simple change (≤5 files, clear scope) | Single paragraph. No sub-headings needed. |
| Complex change (ambiguous scope, multiple stakeholders) | Split into "Current Situation" + "User Requirement" sub-headings |

| ❌ Fail | ✅ Pass |
|---------|---------|
| "Need to refactor" | "Auth takes 5s → 12% conversion drop" |
| "Improve the UI" | "Form completion rate 23% → target 60%" |

#### B. Proposed Solution

**Standard**: Core approach (1-3 paragraphs) + why this over alternatives.

Sub-sections:
- **Approach**: The "what" and "why this way"
- **Key Changes**: Major modules, interfaces, dependencies affected

#### C. Implementation Strategy

**Standard (single/sub change)**: File-level breakdown with paths.

```markdown
### Phase 1: <name>
- `src/auth/jwt.py` — create, refresh_token() + validate_token()
- `src/middleware/auth.py` — modify, add JWT middleware

### Risks & Dependencies
- Redis cluster mode untested; fallback to single-node
```

**Standard (root change)**: Phase-level breakdown. Each phase becomes a sub-change.

```markdown
### Phase 1: <name>
- **Sub-change**: (filled when created)
- **Goal**: <measurable deliverable>
- **Dependencies**: <what must complete first>
- **Scope**: <subsystems affected>
```

#### D. Blockers & Feedback

**Standard**: Dated, actionable entries.

```markdown
### Blocker (2026-02-10)
**Blocked**: Redis connection pooling | **Needed**: DevOps to provide host:port

### PIVOT (2026-02-12)
Direction change: switched from JWT to session-based auth. Reason: client requires server-side revocation.
```

---

## tasks.md

### Frontmatter

```yaml
---
change: "<change-name>"
updated: ""                  # ISO date, updated by agent
---
```

Root changes additionally have `change-type: root`.

### Task Granularity

| Change Type | Task Level | Example |
|-------------|-----------|---------|
| single / sub | File-level, <2h each | `- [ ] Create src/auth/jwt.py — refresh_token()` |
| root | Milestone-level (one per sub-change) | `- [ ] Phase 1 sub-change completed and archived` |

### Phase Structure

```markdown
### Phase 1: <name> 🚧
- [ ] Task description `path/file.py`
- [ ] Task description `path/file.py`
**Verification**: <how to verify this phase>
```

### Phase Emoji Convention

| Emoji | Meaning |
|-------|---------|
| 🚧 | In progress — actively working |
| ✅ | Done — all tasks completed and verified |
| ⏳ | Pending — not yet started |

### Progress Table

```markdown
**Overall**: 40%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 100% | ✅ |
| Phase 2 | 30% | 🚧 |
| Phase 3 | 0% | ⏳ |
```

**Critical Rule**: Update percentage and status after **EACH** task completion, not in batches. `sspec change status` auto-calculates from checkboxes — keep tasks.md as the single source of truth.

### Verification Criteria

Each task (or at minimum each phase) must have explicit pass criteria:

| ❌ Vague | ✅ Specific |
|----------|------------|
| "Add tests" | "Add tests in `tests/test_jwt.py`, cover: valid token, expired token, malformed token" |
| "Update config" | "Add `REDIS_URL` to `.env.example`, verify `config.py` reads it with fallback" |

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
| No file paths in spec.md C | List specific `path/file:function()` per task |
| Mark `[x]` without testing | Done = coded **AND** verified |
| Stay DOING when blocked | BLOCKED immediately + document in D |
| Skip REVIEW status | DOING → REVIEW → DONE, no shortcuts |
| Batch progress updates | Update tasks.md after **each** task |
| Over-structure simple changes | Simple = single paragraph in A, flat list in C |
| Forget reference field | Always link to originating request |
