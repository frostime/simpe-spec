# Design Examples — Root Change

Concrete examples of spec.md for root changes (multi-phase coordinators).
Root spec describes scope and phase decomposition — NOT file-level implementation detail.
File-level design detail belongs in each sub-change's own spec.md + design.md.

Path note: when a sample includes `reference.source`, it is workspace-relative and normally starts with `.sspec/`.

---

## Table of Contents

- [Root Example (3-phase, linear)](#root-example-3-phase-linear)
- [Root Example (4-phase, branching dependencies)](#root-example-4-phase-branching-dependencies)
- [Sub-change spec.md guidance](#sub-change-specmd-guidance)

---

## Root Example (3-phase, linear)

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

## Problem Statement

Current auth system is a monolithic module (2,400 LOC in `auth.py`) with no caching,
no token refresh, and hard-coded permissions. Auth latency is 5s on cold start,
contributing to 12% conversion drop. Needs complete overhaul to support multi-tenancy
requirement by Q3.

## Proposed Solution

### Approach

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

```text
Phase 1: Auth Backend
  ├── Phase 2: Token Refresh  (start once Phase 1 API is stable)
  └── Phase 3: RBAC           (start once Phase 1 API is stable, parallel with Phase 2)
```

Coordination note: Phase 1 must expose a stable `AuthService` interface before
Phases 2 and 3 begin. Phases 2 and 3 can run in parallel after that point.

### Scope Summary

| Phase | Sub-Change | Scope |
|-------|------------|-------|
| Phase 1: Auth Backend | `auth-overhaul--phase1` | `src/auth/`, `src/middleware/` |
| Phase 2: Token Refresh | `auth-overhaul--phase2` | `src/auth/jwt.py`, `src/middleware/auth.py` |
| Phase 3: RBAC | `auth-overhaul--phase3` | `src/models/`, `src/auth/rbac.py` |
```

---

## Root Example (4-phase, branching dependencies)

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

## Problem Statement

API p95 latency is 4.2s. Page load time is 8.1s on cold cache.
DB CPU is at 85% during peak. No CDN or asset pipeline.

Target: p95 API latency <200ms, page load <2s. Deliver in two calendar months
across the full stack — DB, API, static assets, and infrastructure.

## Proposed Solution

### Approach

Address bottlenecks in priority order: DB first (foundational), then API caching
(unlocked by DB improvements), then CDN (independent track), then auto-scaling
(requires stable API layer). Phases 1 and 3 can proceed in parallel immediately.

### Phase Overview

| Phase | Goal | Depends On | Scope |
|-------|------|-----------|-------|
| **Phase 1: DB Optimization** | Eliminate N+1 queries, add missing indexes. Target: DB CPU <40%. | — | `src/models/`, `migrations/` |
| **Phase 2: API Response Cache** | Redis-backed cache for read-heavy endpoints. Target: p95 <200ms. | Phase 1 | `src/api/`, `src/services/cache.py` |
| **Phase 3: CDN + Asset Pipeline** | Vite build pipeline + CloudFront distribution. Target: page load <2s. | — (independent) | `frontend/`, `infra/cdn/` |
| **Phase 4: Auto-scaling** | ECS task auto-scaling + connection pooling. Target: no manual scale events. | Phase 1 + Phase 2 | `infra/ecs/`, `src/db/pool.py` |

```text
Phase 1: DB Optimization ──────────────────────────────────┐
  └── Phase 2: API Response Cache                          │
        └── Phase 4: Auto-scaling ←────────────────────────┘
Phase 3: CDN + Asset Pipeline  (parallel independent track)
```

Coordination notes:
- Phase 1 and Phase 3 can start immediately in parallel.
- Phase 2 starts after Phase 1 reaches REVIEW.
- Phase 4 starts after Phase 2 is DONE.

### Scope Summary

| Phase | Sub-Change | Scope |
|-------|------------|-------|
| Phase 1 | `perf--db-optimization` | `src/models/`, `migrations/` |
| Phase 2 | `perf--api-cache` | `src/api/`, `src/services/cache.py` |
| Phase 3 | `perf--cdn-pipeline` | `frontend/`, `infra/cdn/` |
| Phase 4 | `perf--auto-scaling` | `infra/ecs/`, `src/db/pool.py` |
```

---

## Sub-change spec.md guidance

Each sub-change gets its own spec.md (and design.md if needed).
Root spec describes phases; sub-change specs describe the implementation design for each phase.

Sub-change spec.md must:
- Reference the root change in frontmatter (`type: root-change`)
- Have a scoped Problem Statement (just this phase's problem, not the full root scope)
- Have a full Proposed Solution with Key Change labels and Scope Summary

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

## Problem Statement

Phase 1 of `auth-overhaul`: extract the monolithic `auth.py` (2,400 LOC) into
a service layer with Redis caching. Target: auth latency <1s.

## Proposed Solution

### Approach

Split monolith into three focused modules behind `AuthService`. Redis caching
moves from inline calls to a dedicated cache layer. Middleware calls `AuthService`
only — no direct JWT or cache access.

### Key Change

**Refactor A: Extract auth service** — Split monolithic `auth.py` into `AuthService`
behind a clean interface. Redis caching moves to dedicated `cache.py`. Middleware
calls `AuthService` only — no direct JWT or cache access.

### Scope Summary

| File | Change |
|------|--------|
| `src/auth/service.py` | New — `AuthService` class |
| `src/auth/jwt.py` | New — JWT encode/decode |
| `src/auth/cache.py` | New — Redis cache layer |
| `src/middleware/auth.py` | Refactor to call `AuthService` |
| `src/auth.py` | Delete — logic moved to service |

### Design Reference

→ 详细技术设计见 [design.md](./design.md)
```

### What root spec does NOT include

| Not in root spec | Goes in sub-change |
|------------------|--------------------|
| Function/class signatures | sub-change design.md |
| Data models per phase | sub-change design.md |
| Per-item decisions | sub-change Key Change |
| File-level Scope Summary | sub-change Scope Summary |
| Task lists | sub-change tasks.md |
