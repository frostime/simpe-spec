# Design Examples

Concrete examples of spec.md (A + B) at three complexity levels.
Reference this when filling spec.md in the design phase.

**📚 Standards**: See [SKILL.md](../SKILL.md) for rules and workflow.

---

## Table of Contents

- [Simple Example](#simple-example) (L16) — ≤5 files
- [Medium Example](#medium-example) (L48) — 5-15 files
- [Complex Example](#complex-example) (L114) — >15 files, reference/ design
- [Root Change Example](#root-change-example) (L143)
- [B → tasks.md Boundary](#b--tasksmd-boundary) (L178) — What goes where

---

## Simple Example

≤5 files. Interface/data model inline in Approach.

```markdown
---
name: jwt-refresh
status: PLANNING
change-type: single
created: 2026-02-15T10:00:00
reference:
  - source: "requests/260215_auth-timeout.md"
    type: "request"
---

# jwt-refresh

## A. Problem Statement

Auth tokens expire after 30 minutes with no refresh mechanism. Users must re-login mid-session, causing 12% session abandonment.

## B. Proposed Solution

### Approach

Add token refresh to the existing JWT validation middleware. When a token is within 5 minutes of expiry, the middleware returns a refreshed token in the response header. This avoids a separate refresh endpoint and requires no client-side changes beyond reading the header.

Why middleware-based: intercepting at the HTTP layer avoids modifying every API call site (currently 23 endpoints).

### Key Design

**Interface**: `src/auth/jwt.py:validate_token(token: str, refresh: bool = True) -> TokenResult`
Returns `TokenResult(valid=True, refreshed_token=<new_token>|None)`.

**Modified**: `src/middleware/auth.py` — if `refreshed_token` is not None, set `X-Refreshed-Token` response header.
```

---

## Medium Example

5-15 files, cross-module. Dedicated sub-sections for interface, data model, key logic.

```markdown
---
name: auth-cache
status: PLANNING
change-type: single
created: 2026-02-15T10:00:00
reference:
  - source: "requests/260215_auth-perf.md"
    type: "request"
---

# auth-cache

## A. Problem Statement

Auth validation queries the database on every request. Current load: 500 QPS to the users table, causing p95 latency of 340ms. Target: <50 QPS to DB, p95 <80ms.

## B. Proposed Solution

### Approach

Add a Redis-based user cache between the auth middleware and the database. Cache validated user objects with per-key TTL. On cache miss, fall back to DB and populate cache.

Why Redis over in-memory: multiple app instances share one cache, and per-key TTL prevents stale sessions (in-memory LRU can't expire individual keys by token lifetime).

### Interface Design

**New module**: `src/services/cache.py`
- `get_cached_user(user_id: str) -> Optional[User]`
- `set_cached_user(user: User, ttl: int = 300)`
- `invalidate_user_cache(user_id: str)`

**Modified**: `src/services/auth.py`
- `authenticate(token: str) -> User` — add cache lookup before DB query

### Data Model

Cache key format: `user:{user_id}` → JSON-serialized `User` object.
TTL: 300s (5 min) with ±10% jitter to prevent stampede.

### Key Logic

```
Request → auth middleware → validate JWT → extract user_id
  → cache.get_cached_user(user_id)
    → HIT: return cached User
    → MISS: db.get_user(user_id) → cache.set_cached_user(user) → return User
  → On user update (any write to users table):
    → cache.invalidate_user_cache(user_id)
```

Concurrent requests during cache miss share a single DB query via Redis `SET NX` lock (5s timeout). Second request waits and reads from cache.
```

---

## Complex Example

>15 files, architectural change. Core approach in B, detailed design in `reference/design.md`.

```markdown
---
name: multi-tenant-rbac
status: PLANNING
change-type: single
created: 2026-02-15T10:00:00
reference:
  - source: "requests/260210_multi-tenancy.md"
    type: "request"
  - source: "spec-docs/auth-system.md"
    type: "doc"
---

# multi-tenant-rbac

## A. Problem Statement

### Current Situation
Single-tenant auth system. All users share one permission space. No data isolation between organizations.

### User Requirement
Support multiple organizations on the same instance with isolated data and role-based access control. Target: 50 tenants within 3 months.

## B. Proposed Solution

### Approach

Add tenant isolation layer + RBAC on top of existing JWT auth. Every request carries `tenant_id` in the JWT claims. A middleware injects tenant context before any DB query. Roles are tenant-scoped (admin in Org A ≠ admin in Org B).

Full architecture, data model, and API contracts: see [reference/design.md](reference/design.md).

### Key Design

**Core changes** (summary — detail in reference/design.md):
- `Tenant` model: `{id, name, plan, created_at}`
- `Role` model: `{id, tenant_id, name, permissions: Permission[]}`
- `Permission` enum: `READ | WRITE | ADMIN | SUPER_ADMIN`
- JWT claims extended: `{..., tenant_id: str, roles: str[]}`
- `TenantMiddleware`: extracts `tenant_id` from JWT, sets `request.tenant` context
- All DB queries filtered by `tenant_id` via SQLAlchemy query mixin
```

---

## Root Change Example

Root spec.md — phase-level overview, no file-level detail.

```markdown
---
name: auth-overhaul
status: PLANNING
change-type: root
created: 2026-02-15T10:00:00
reference:
  - source: "requests/260210_auth-rewrite.md"
    type: "request"
---

# auth-overhaul

## A. Problem Statement

Current auth system is a monolithic module (2,400 LOC in one file) with no caching, no token refresh, and hard-coded permissions. Auth latency is 5s on cold start, contributing to 12% conversion drop. Needs complete overhaul to support multi-tenancy requirement by Q3.

## B. Proposed Solution

### Overall Approach

Break the auth overhaul into three sequential phases. Each phase delivers independently testable value. Phase 1 is foundational — Phases 2 and 3 depend on it but are independent of each other.

### Phase Overview

- **Phase 1: Auth Backend** — Extract auth into service layer, add JWT + Redis cache. Goal: <1s auth response. Scope: `src/auth/`, `src/services/`, `src/middleware/`.
- **Phase 2: Token Refresh** — Add silent refresh mechanism. Depends on Phase 1. Scope: `src/auth/jwt.py`, `src/middleware/auth.py`.
- **Phase 3: RBAC** — Role-permission matrix, tenant-scoped. Depends on Phase 1. Scope: `src/models/`, `src/auth/`, `src/middleware/rbac.py`.

Coordination: Phase 1 defines the `AuthService` interface that Phases 2 and 3 extend. Interface contract must be frozen before Phase 2/3 start.
```

---

## B → tasks.md Boundary

With Section C removed, the responsibilities divide cleanly between B and tasks.md:

| Content | Where | Example |
|---------|-------|---------|
| **Why** this approach | spec.md B → Approach | "Redis over Memcached because per-key TTL" |
| **What** the design is | spec.md B → Key Design | Interface signatures, data model, logic flow |
| **What to do** (file-level) | tasks.md phases | `- [ ] Create src/services/cache.py` |
| **How to verify** | tasks.md verification | `pytest tests/test_cache.py passes` |
| **Phase organization** | tasks.md phase headers | `### Phase 1: Cache Module ⏳` |

**Key rule**: B defines the design, tasks.md organizes execution. Tasks reference B, never repeat it.

### ❌ Bad — Repeating B's interface in tasks.md

```markdown
### Phase 1: Cache Module ⏳
- [ ] Create `src/services/cache.py` with:
  - `get_cached_user(user_id: str) -> Optional[User]`    ← repeated from B!
  - `set_cached_user(user: User, ttl: int = 300)`         ← repeated from B!
  - `invalidate_user_cache(user_id: str)`                  ← repeated from B!
```

### ✅ Good — Referencing B

```markdown
### Phase 1: Cache Module ⏳
- [ ] Create `src/services/cache.py` — implement interface per spec.md B
- [ ] Add Redis config to `config.py` with fallback default
**Verification**: `pytest tests/test_cache.py` passes
```
