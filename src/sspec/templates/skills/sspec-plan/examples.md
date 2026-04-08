# Plan Examples

Concrete examples of tasks.md at different complexity levels.
Shows how tasks.md references spec.md without repeating design content.

**📚 Standards**: See [SKILL.md](./SKILL.md) for rules and workflow.

---

## Table of Contents

- [Simple tasks.md](#simple-tasksmd) — Single phase, ≤5 files
- [Medium tasks.md](#medium-tasksmd) — Multi-phase, cross-module
- [Root tasks.md](#root-tasksmd) — Milestones, not file-level
- [Complete Flow: spec → tasks.md](#complete-flow-spec--tasksmd) — End-to-end example

---

## Simple tasks.md

Single phase, few files. Verification is straightforward.

```markdown
---
change: "jwt-refresh"
updated: ""
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Token Refresh ⏳
- [ ] Modify `src/auth/jwt.py` — add refresh logic to `validate_token()` per spec.md
- [ ] Modify `src/middleware/auth.py` — set `X-Refreshed-Token` header when refresh occurs
- [ ] Add tests `tests/test_jwt_refresh.py` — cover: valid token, near-expiry refresh, expired token
**Verification**: `pytest tests/test_jwt_refresh.py` passes; manual test confirms header appears for tokens expiring within 5 min

---

## Progress

**Overall**: 0%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 0% | ⏳ |

**Recent**:
- (none yet)
```

---

## Medium tasks.md

Multi-phase, references spec.md Key Change labels and design.md.

```markdown
---
change: "auth-cache"
updated: ""
---

# Tasks

## Legend
`[ ]` Todo | `[x]` Done

## Tasks

### Phase 1: Cache Module ⏳
- [ ] Create `src/services/cache.py` — implement interface per design.md
- [ ] Add `REDIS_URL` to `.env.example` and `config.py` (with `localhost:6379` fallback)
- [ ] Implement stampede prevention: `SET NX` lock per design.md Behavior section
- [ ] Add TTL jitter (±10%) to `set_cached_user()`
**Verification**: Unit tests for get/set/invalidate pass; stampede lock verified with concurrent test

### Phase 2: Auth Integration ⏳
- [ ] Modify `src/services/auth.py:authenticate()` — add cache lookup per design.md call chain
- [ ] Modify `src/services/user.py:update_user()` — call `invalidate_user_cache()` after write
- [ ] Add fallback: if Redis unreachable, skip cache and query DB directly (try-except in cache.py)
**Verification**: Auth flow works with Redis up/down; user update invalidates cache within 1s

### Phase 3: Testing ⏳
- [ ] Create `tests/test_cache.py` — cover: hit, miss, invalidation, TTL expiry, Redis-down fallback
- [ ] Add cache scenarios to `tests/test_auth.py` — cache hit path, cache miss path
- [ ] Load test: verify DB QPS drops from 500 to <50 under simulated load
**Verification**: All tests pass; load test confirms <50 QPS to DB

---

## Progress

**Overall**: 0%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 0% | ⏳ |
| Phase 2 | 0% | ⏳ |
| Phase 3 | 0% | ⏳ |

**Recent**:
- (none yet)
```

---

## Root tasks.md

Milestone-level, one entry per sub-change. No file-level detail.

```markdown
---
change: "auth-overhaul"
change-type: root
updated: ""
---

# Milestones

## Legend
`[ ]` Todo | `[x]` Done (sub-change completed + verified)

## Milestones

### Phase 1: Auth Backend ⏳
- [ ] Sub-change created and linked
- [ ] Sub-change completed
**Deliverable**: Auth service layer with JWT + Redis cache, <1s response
**Sub-change**: (link when created)

### Phase 2: Token Refresh ⏳
- [ ] Sub-change created and linked
- [ ] Sub-change completed
**Deliverable**: Silent token refresh, no client changes required
**Sub-change**: (link when created)

### Phase 3: RBAC ⏳
- [ ] Sub-change created and linked
- [ ] Sub-change completed
**Deliverable**: Tenant-scoped role-permission matrix
**Sub-change**: (link when created)

---

## Progress

**Overall**: 0%

| Phase | Sub-Change | Status | Deliverable |
|-------|------------|--------|-------------|
| Phase 1 | (pending) | ⏳ | Auth service + cache |
| Phase 2 | (pending) | ⏳ | Token refresh |
| Phase 3 | (pending) | ⏳ | RBAC |

**Recent**:
- (none yet)
```

---

## Complete Flow: spec → tasks.md

End-to-end example showing the auth-cache change from design to plan.

### Step 1: spec.md (Design Phase Output)

```markdown
## Problem Statement

DB load is 500 QPS during peak. Auth service queries DB on every request.
No caching layer exists. Target: reduce DB QPS to <50.

## Proposed Solution

### Approach

Redis-based user cache to reduce DB load. Multiple app instances share one cache;
per-key TTL prevents stale sessions.

### Key Change

**Cache A: User cache module** — New `src/services/cache.py` with get/set/invalidate
interface. TTL 300s ±10% jitter. SET NX lock prevents cache stampede on concurrent misses.

**Cache B: Auth integration** — `authenticate()` checks cache before DB. `update_user()`
invalidates cache after write. Redis-down fallback: skip cache, query DB directly.

### Scope Summary

| File | Change |
|------|--------|
| `src/services/cache.py` | New — user cache module |
| `src/services/auth.py` | Add cache lookup in `authenticate()` |
| `src/services/user.py` | Add cache invalidation in `update_user()` |
| `tests/test_cache.py` | New — cache unit tests |

### Design Reference

→ 详细技术设计见 [design.md](./design.md)
```

### Step 2: design.md (Technical Detail)

```markdown
## Interface

```python
# src/services/cache.py
def get_cached_user(user_id: str) -> User | None: ...
def set_cached_user(user: User, ttl: int = 300) -> None: ...
def invalidate_user_cache(user_id: str) -> None: ...
```

## Behavior

```
authenticate(token)
  │
  ├── cache.get(user_id)   → HIT: return User
  └── MISS:
        ├── db.get_user(user_id)
        ├── cache.set(user, ttl=300 ± jitter)
        └── return User

update_user(user)
  ├── db.update(user)
  └── cache.invalidate(user.id)
```

Concurrent misses: SET NX lock ensures only one DB query per key.
Redis-down: ConnectionError caught in cache.py → skip cache, query DB directly.
```

### Step 3: tasks.md (Plan Phase Output)

```markdown
### Phase 1: Cache Module ⏳
- [ ] Create `src/services/cache.py` — implement interface per design.md
- [ ] Add Redis config to `config.py` with `localhost:6379` fallback
- [ ] Implement SET NX stampede lock per design.md Behavior
- [ ] Add TTL jitter (±10%) to `set_cached_user()`
**Verification**: `pytest tests/test_cache.py` — get/set/invalidate/stampede/Redis-down

### Phase 2: Auth Integration ⏳
- [ ] Modify `src/services/auth.py:authenticate()` — cache lookup per design.md call chain
- [ ] Modify `src/services/user.py:update_user()` — add invalidation call (Cache B)
- [ ] Add Redis-down fallback (try-except ConnectionError)
**Verification**: Auth works with Redis up and down; update invalidates within 1s
```

### The boundary in practice

| In spec.md / design.md | In tasks.md | Relationship |
|------------------------|-------------|--------------|
| `get_cached_user(user_id: str) -> User \| None` | `implement interface per design.md` | reference, not repeat |
| SET NX lock mechanism | `Implement SET NX stampede lock per design.md Behavior` | reference |
| TTL 300s ±10% jitter | `Add TTL jitter (±10%) to set_cached_user()` | distill to action |
| call chain diagram | `cache lookup per design.md call chain` | reference |

Design stays in spec.md/design.md. Actions go in tasks.md.
