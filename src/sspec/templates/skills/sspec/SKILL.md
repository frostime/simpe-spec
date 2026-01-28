---
skill: sspec
version: 3.0.0
description: Deep reference for SSPEC workflow - document writing guidelines, status transition rules, edge cases. MUST read on first use of sspec workflow or when handling complex scenarios.
---

# SSPEC Skill

**When to consult this SKILL**:
- Unsure how to write spec.md / tasks.md / handover.md effectively
- Status transitions are ambiguous (e.g., partial blockers)
- Handling edge cases not covered in AGENTS.md
- Need to edit existing change documents

**Quick reference**: For basic usage, change templates have inline `@AGENT: RULE/` markers. Read this SKILL for quality guidelines and edge cases.

---

## Table of Contents

**Core Essentials** (Read first):
- [Core Editing Patterns](#core-editing-patterns) — Understanding @AGENT markers
- [Document Writing Guidelines](#document-writing-guidelines) — spec.md, tasks.md, handover.md quality standards
- [Status Transition Rules](#status-transition-rules) — State machine and prohibited transitions

**Reference**:
- [spec-docs/ Directory](#spec-docs-directory) — Project-level specifications
- [Change Auxiliary Files](#change-auxiliary-files) — reference/ and scripts/
- [Edge Cases](#edge-cases) — Partial blockers, mid-flight rejection, multi-change
- [Anti-Patterns](#anti-patterns) — Common mistakes to avoid
- [Quick Reference](#quick-reference-document-checklist) — Checklists

---

## Core Editing Patterns

### Understanding @AGENT Markers

**`@AGENT: RULE/<topic>`** — Constraint to follow when editing this section
```markdown
<!-- @AGENT: RULE/quantify-pain
Describe current pain points with metrics.
-->
```

**`@AGENT: REPLACE-FOR-EDIT/<section>`** — This section is meant to be replaced, not appended
```markdown
<!-- @AGENT: REPLACE-FOR-EDIT/problem-statement -->
```

### Common Editing Operations

| Operation | When | How |
|-----------|------|-----|
| **Replace section** | Marker present | Use str_replace with full section content |
| **Update progress** | After each task | Replace entire "Progress Tracking" section |
| **Add blocker** | When stuck | Append new blocker entry to Section D |
| **Update handover** | End of session | Replace entire handover content |

**Anti-pattern**: Appending to a `REPLACE-FOR-EDIT` section creates duplication.

---

## Document Writing Guidelines

### spec.md — Specification

**Purpose**: Let the next Agent (or future you) **quickly understand problem and solution**.

#### Section A: Problem Statement

Answer: **Why are we doing this?**

✅ Quantifiable problem, explains urgency  
❌ "Need to refactor" (missing why)

Example: "Auth takes 5s average, causing 12% conversion drop. Reduce to <1s."

#### Section B: Proposed Solution

Answer: **How to solve? Why this approach?**

✅ Core approach + key decisions  
❌ Jumping to implementation details

Example: "JWT + Redis caching: move token validation from DB to memory lookups."

#### Section C: Implementation Strategy

**Critical**: Break down to **file level**.

✅ Lists specific files to create/modify  
❌ "Modify related files" (not specific)

Format:
```markdown
### Phase 1: Infrastructure
- `src/cache/redis.py` — create, Redis pool
- `requirements.txt` — modify, add redis
```

#### Section D: Blockers & Feedback

Record blockers and user feedback with dates:
```markdown
### Blocker (2026-01-27)
**Blocked**: Waiting for DevOps Redis info
**Impact**: Cannot run integration tests
**Needed**: Redis host, port, password
```

---

### tasks.md — Task List

**Purpose**: Each task **independently executable, verifiable, <2h to complete**.

#### Task Granularity

❌ Too broad: "Implement auth system"  
✅ Appropriate: "Create Redis pool `src/cache/redis.py` — Verify: unit tests pass"

#### Task Organization

Organize by phases with clear verification:
```markdown
### Phase 1: Infrastructure ✅
- [x] Add redis dependency `requirements.txt`
- [x] Create `src/cache/redis.py` connection pool
**Verification**: `pytest tests/test_cache.py` passes

### Phase 2: Auth Logic 🚧
- [x] Modify `src/auth/middleware.py` cache-first
- [ ] Add token refresh logic
**Verification**: Auth response <100ms
```

#### Progress Tracking

Update after **each task completion** (not batched).
```markdown
**Overall**: 60% (3/5 tasks)
| Phase | Progress | Status |
| Phase 1: Infrastructure | 100% | ✅ Done |
| Phase 2: Auth Logic | 33% | 🚧 In Progress |
```

---

### handover.md — Session Handover

**Purpose**: Get the next Agent working in **30 seconds**.

**Philosophy**: Time bridge. Bad handover = 30min wasted. Good handover = 30sec to start.

#### Essential Content

Must include:
1. **Background** — What is this change about?
2. **Accomplished** — What was done this session?
3. **Current status** — PLANNING/DOING/BLOCKED/REVIEW
4. **Next steps** — Specific, file-level actions
5. **Conventions** — Patterns, naming, error codes

#### Quality Comparison

| Dimension | ❌ Poor | ✅ Good |
|-----------|---------|---------|
| Background | "Doing auth" | "JWT+Redis cache, <1s target" |
| Progress | "Did some stuff" | "Phase 1 done, 60% complete" |
| Next step | "Keep going" | "Implement jwt.py:refresh_token()" |
| Conventions | None | Key format, expiry, error codes |

---

## Status Transition Rules

### Status Definitions

| Status | Meaning | Enter When | Exit When |
|--------|---------|------------|-----------|
| **PLANNING** | Defining scope and approach | New change / major pivot | User approves plan |
| **DOING** | Implementation in progress | Plan approved / blocker resolved | Tasks complete / blocked / pivot |
| **BLOCKED** | Waiting for external | Missing info/resources/approval | Blocker resolved / pivot |
| **REVIEW** | Complete, awaiting acceptance | All tasks done | User accepts / requests changes |
| **DONE** | Completed and archived | User accepts | `sspec change archive` |

### Prohibited Transitions

| Prohibited | Reason |
|------------|--------|
| PLANNING → DONE | Cannot complete without implementation |
| DOING → DONE | Must go through REVIEW |
| BLOCKED → DONE | Blocker must be resolved first |

### State Transition Flow

**Normal**: PLANNING → DOING → REVIEW → DONE  
**With blockers**: DOING ↔ BLOCKED → DOING  
**Pivot**: DOING → PLANNING (scope changed)

---

## spec-docs/ Directory

`.sspec/spec-docs/` stores **project-level technical specs**, unrelated to individual changes.

### Suitable Content

| Type | Example |
|------|---------|
| Architecture | `architecture.md` — system design, module boundaries |
| Dev standards | `coding-standards.md` — naming, style guidelines |
| API specs | `api-spec.md` — interface definitions, data formats |
| Tech decisions | `adr/` — Architecture Decision Records |

### Difference from change

- **change/spec.md**: Single change's problem and solution (temporary)
- **spec-docs/**: Project-level specs and design (persistent)

### Referencing

```markdown
## B. Proposed Solution
Follow auth interface format defined in [API Spec](.sspec/spec-docs/api-spec.md).
```

---

## Change Auxiliary Files

Beyond core trio (spec.md, tasks.md, handover.md), store supporting files:

```
.sspec/changes/<name>/
├── spec.md, tasks.md, handover.md  # Required
├── reference/                      # Optional: detailed design, research
└── scripts/                        # Optional: migration scripts, test data
```

| Directory | Purpose | Examples |
|-----------|---------|----------|
| `reference/` | Detailed design, research, drafts | Architecture diagrams, API design |
| `scripts/` | One-off scripts, test data | Data migration, env setup, mock data |

**Archive**: `sspec change archive <name>` archives entire directory including reference/ and scripts/.

---

## Edge Cases

### Partial Blockers

**Situation**: Some tasks blocked, others can continue.

**Options**:
1. **Split change**: Move blocked tasks to new change
2. **Reorder tasks**: Move non-critical blocked tasks to end
3. **Document and continue**: Record blocker in spec.md Section D, use workaround

### REVIEW Spanning Multiple Sessions

**Handling**:
- Keep status as REVIEW
- Update handover: "Awaiting user verification since <date>"
- Can work on other changes simultaneously

### User Mid-Flight Rejection

**Situation**: User says "this isn't what I wanted" during implementation.

**Handling**:
1. Stop implementation immediately
2. Use `@argue` to clarify scope
3. Update spec.md and tasks.md
4. Get explicit approval before continuing
5. Consider status change: DOING → PLANNING

### Multiple Changes DOING Simultaneously

**Problem**: Context switching causes errors.

**Best practices**:
1. `@handover` current change before switching
2. Use `@change <other>` to explicitly switch context
3. Avoid having >2 changes in DOING status

---

## Anti-Patterns

| Anti-Pattern | Consequence | Correct Approach |
|--------------|-------------|------------------|
| Skip handover | Next session wastes 30min | Write handover every session |
| Mark done without testing | False progress, later bugs | "Done" = implemented + verified |
| No file-level breakdown | Don't know what to modify | Section C lists specific files |
| Stay DOING when blocked | Waste time on workarounds | Change to BLOCKED, document |
| DOING → DONE skip REVIEW | Missing user validation | Always go through REVIEW |
| Update progress only at end | Lose track of what's done | Update after each task |

---

## Quick Reference: Document Checklist

### When Creating New Change

- [ ] spec.md Section A: Problem quantified
- [ ] spec.md Section B: Solution rationale clear
- [ ] spec.md Section C: File-level breakdown
- [ ] tasks.md: Tasks <2h each with verification
- [ ] handover.md: Initial context set

### During Implementation

- [ ] Update tasks.md progress after each task
- [ ] Record blockers in spec.md Section D immediately
- [ ] Update handover at end of each session
- [ ] Change status when appropriate (DOING ↔ BLOCKED)

### Before Moving to REVIEW

- [ ] All tasks marked [x]
- [ ] Verification criteria met
- [ ] Handover reflects completion
- [ ] spec.md Section D documents any remaining concerns

### Before Archiving (DONE)

- [ ] User has accepted the change
- [ ] All documentation updated
- [ ] No outstanding blockers or concerns
