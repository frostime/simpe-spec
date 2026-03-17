# Design Examples — Root Change

Concrete examples of spec.md (A + B) for root changes (multi-phase coordinators).
Root spec describes scope and phase decomposition — NOT file-level implementation detail.
File-level design detail belongs in each sub-change's own spec.md.

Path note: when a sample includes `reference.source`, it is workspace-relative and normally starts with `.sspec/`.

**📚 Standards**: See [SKILL.md](./SKILL.md) for Universal Rules and workflow.

---

## Table of Contents

- [Root Example (3-phase, linear)](#root-example-3-phase-linear) (L22)
- [Root Example (4-phase, branching dependencies)](#root-example-4-phase-branching-dependencies) (L87)
- [Sub-change Section B Guidance](#sub-change-section-b-guidance) (L163)

---

## Root Example (3-phase, linear)

Three phases with clear sequential dependencies. Use dependency-annotated list + ASCII tree.

```markdown
---
name: auth-overhaul
status: PLANNING
change-type: root
created: 2026-02-15T10:00:00
reference:
  - source: ".sspec/requests/260210_auth-rewrite.md"
    type: "request"
---

# auth-overhaul

## A. Problem Statement

Current auth system is a monolithic module (2,400 LOC in `auth.py`) with no caching,
no token refresh, and hard-coded permissions. Auth latency is 5s on cold start,
contributing to 12% conversion drop. Needs complete overhaul to support multi-tenancy
requirement by Q3.

## B. Proposed Solution

### Overall Approach

Break the auth overhaul into three sequential phases. Each phase delivers independently
testable value. Phase 1 is foundational — Phases 2 and 3 depend on it and should
not start until Phase 1 is in REVIEW or DONE.

### Phase Overview

- **Phase 1: Auth Backend** — Extract auth into a service layer, add JWT + Redis cache.
  Goal: <1s auth response. Scope: `src/auth/`, `src/services/auth.py`, `src/middleware/`.

- **Phase 2: Token Refresh** — Add silent token refresh via middleware. Depends on Phase 1
  (`AuthService` interface must be stable). Scope: `src/auth/jwt.py`, `src/middleware/auth.py`.

- **Phase 3: RBAC** — Role-permission matrix, tenant-scoped. Depends on Phase 1.
  Independent of Phase 2. Scope: `src/models/`, `src/auth/rbac.py`, `src/middleware/rbac.py`.

Dependency tree:
\`\`\`
Phase 1: Auth Backend
  ├── Phase 2: Token Refresh  (can start once Phase 1 API is stable)
  └── Phase 3: RBAC           (can start once Phase 1 API is stable)
\`\`\`

Coordination note: Phase 1 must expose a stable `AuthService` interface before
Phases 2 and 3 begin. Phases 2 and 3 can run in parallel after that point.
```

---

## Root Example (4-phase, branching dependencies)

Four or more phases with a branching dependency graph. Use a dependency table.

```markdown
---
name: platform-perf-overhaul
status: PLANNING
change-type: root
created: 2026-02-15T10:00:00
reference:
  - source: ".sspec/requests/260210_platform-perf.md"
    type: "request"
---

# platform-perf-overhaul

## A. Problem Statement

### Current Situation

API p95 latency is 4.2s. Page load time is 8.1s on cold cache.
DB CPU is at 85% during peak. No CDN or asset pipeline.

### User Requirement

Target: p95 API latency <200ms, page load <2s. Deliver in two calendar months
across the full stack — DB, API, static assets, and infrastructure.

## B. Proposed Solution

### Overall Approach

Address bottlenecks in priority order: DB first (foundational), then API caching
(unlocked by DB improvements), then CDN (independent track), then auto-scaling
(requires stable API layer). Phases 1 and 3 can proceed in parallel immediately.

### Phase Overview

| Phase | Goal | Depends On | Scope |
|-------|------|-----------|-------|
| **Phase 1: DB Optimization** | Eliminate N+1 queries, add missing indexes. Target: DB CPU <40%. | — | `src/models/`, `migrations/` |
| **Phase 2: API Response Cache** | Redis-backed cache for read-heavy endpoints. Target: p95 <200ms. | Phase 1 (stable query perf) | `src/api/`, `src/services/cache.py` |
| **Phase 3: CDN + Asset Pipeline** | Vite build pipeline + CloudFront distribution. Target: page load <2s. | — (independent track) | `frontend/`, `infra/cdn/` |
| **Phase 4: Auto-scaling** | ECS task auto-scaling + connection pooling. Target: no manual scale events. | Phase 1 + Phase 2 (stable backend) | `infra/ecs/`, `src/db/pool.py` |

Dependency tree:
\`\`\`
Phase 1: DB Optimization  ──────────────────────────────────────────┐
  └── Phase 2: API Response Cache                                   │
        └── Phase 4: Auto-scaling  ←────────────────────────────────┘
Phase 3: CDN + Asset Pipeline  (parallel independent track)
\`\`\`

Coordination notes:
- Phase 1 and Phase 3 can start immediately in parallel.
- Phase 2 starts after Phase 1 reaches REVIEW.
- Phase 4 starts after Phase 2 is DONE (requires stable cache layer).
- Each phase creates its own sub-change with full design → plan → implement → review.
```

---

## Sub-change Section B Guidance

Each sub-change gets its own spec.md.
Root spec describes phases; sub-change specs describe the **implementation design** for each phase.

Sub-change spec.md must:
- Reference the root change in frontmatter (`type: root-change`)
- Have a scoped Section A (just this phase's problem, not the full root scope)
- Have a full Section B with appropriate predictability dimensions (see SKILL.md Step 3A)
- Include a Scope Summary Table for its own file set (Universal Rule)

### What the Root spec does NOT include

| Not in root spec | Goes in sub-change spec |
|--------------------|--------------------------|
| Function/class signatures per phase | Each sub-change's relevant design dimensions |
| Data models for each phase | Each sub-change's relevant design dimensions |
| File-level Scope Summary (per phase) | Each sub-change's Scope Summary Table |
| Task lists | Each sub-change's tasks.md |

### Example Sub-change spec.md Reference

```markdown
---
name: auth-overhaul--phase1-auth-backend
status: PLANNING
change-type: sub
created: 2026-02-20T09:00:00
reference:
  - source: ".sspec/changes/26-02-15T10-00_auth-overhaul"
    type: "root-change"
    note: "Phase 1: Auth Backend"
---

# auth-overhaul--phase1-auth-backend

## A. Problem Statement

Phase 1 of `auth-overhaul`: extract the monolithic `auth.py` (2,400 LOC) into
a service layer with Redis caching. Target: auth latency <1s.

## B. Proposed Solution

### Approach
...

### Key Design

#### Interface Contract
\`\`\`python
class AuthService:
    def authenticate(self, token: str) -> User: ...
    def invalidate(self, user_id: str) -> None: ...
\`\`\`

#### Behavioral Spec
\`\`\`
Request → AuthMiddleware
  └── AuthService.authenticate(token)
        ├── cache.get(token_hash)    → HIT: return cached User
        └── MISS: db.get_user() → cache.set(token_hash, user, ttl=300) → return User
\`\`\`

Note: cache lookup stays on the hot path, while database work only happens on misses and immediately repopulates the cache for the next request.

#### Scope Summary
| File | Change |
|------|--------|
| `src/services/auth.py` | New — `AuthService` class |
| `src/middleware/auth.py` | Refactor to call `AuthService` |
| `src/auth.py` | Remove — logic moved to service |
\`\`\`
```
