# Plan Examples

Concrete examples of tasks.md at different complexity levels.
Shows how tasks.md references spec.md B without repeating design content.

**📚 Standards**: See [SKILL.md](./SKILL.md) for rules and workflow.

---

## Table of Contents

- [Simple tasks.md](#simple-tasksmd) (L15) — Single phase, ≤5 files
- [Medium tasks.md](#medium-tasksmd) (L52) — Multi-phase, cross-module
- [Root tasks.md](#root-tasksmd) (L108) — Milestones, not file-level
- [Complete Flow: B → tasks.md](#complete-flow-b--tasksmd) (L145) — End-to-end example

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
- [ ] Modify `src/auth/jwt.py` — add refresh logic to `validate_token()` per spec.md B
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

Multi-phase, references spec.md B's design sections.

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
- [ ] Create `src/services/cache.py` — implement interface per spec.md B
- [ ] Add `REDIS_URL` to `.env.example` and `config.py` (with `localhost:6379` fallback)
- [ ] Implement stampede prevention: `SET NX` lock per spec.md B Key Logic
- [ ] Add TTL jitter (±10%) to `set_cached_user()`
**Verification**: Unit tests for get/set/invalidate pass; stampede lock verified with concurrent test

### Phase 2: Auth Integration ⏳
- [ ] Modify `src/services/auth.py:authenticate()` — add cache lookup following B's data flow
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
- [ ] Sub-change completed and archived
**Deliverable**: Auth service layer with JWT + Redis cache, <1s response
**Sub-change**: (link when created)

### Phase 2: Token Refresh ⏳
- [ ] Sub-change created and linked
- [ ] Sub-change completed and archived
**Deliverable**: Silent token refresh, no client changes required
**Sub-change**: (link when created)

### Phase 3: RBAC ⏳
- [ ] Sub-change created and linked
- [ ] Sub-change completed and archived
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

## Complete Flow: B → tasks.md

End-to-end example showing the auth-cache change from design to plan. Demonstrates how tasks.md references B without duplication.

### Step 1: spec.md B (Design Phase Output)

```markdown
## B. Proposed Solution

### Approach
Redis-based user cache to reduce DB load (500 QPS → <50 QPS).
Why Redis: multiple app instances share one cache; per-key TTL prevents stale sessions.

### Interface Design
**New**: `src/services/cache.py`
- `get_cached_user(user_id: str) -> Optional[User]`
- `set_cached_user(user: User, ttl: int = 300)`
- `invalidate_user_cache(user_id: str)`

**Modified**: `src/services/auth.py`
- `authenticate(token: str) -> User` — add cache lookup before DB

### Data Model
Cache key: `user:{user_id}` → JSON User. TTL 300s ±10% jitter.

### Key Logic
cache.get → HIT: return | MISS: db.get → cache.set → return
On user update → cache.invalidate
Concurrent misses share one DB query via SET NX lock.
```

### Step 2: tasks.md (Plan Phase Output)

```markdown
## Tasks

### Phase 1: Cache Module ⏳
- [ ] Create `src/services/cache.py` — implement interface per spec.md B
- [ ] Add Redis config to `config.py` with fallback
- [ ] Implement SET NX stampede lock per B's Key Logic
- [ ] Add TTL jitter to `set_cached_user()`
**Verification**: `pytest tests/test_cache.py` — get/set/invalidate/stampede

### Phase 2: Auth Integration ⏳
- [ ] Modify `src/services/auth.py:authenticate()` — cache lookup per B's data flow
- [ ] Modify `src/services/user.py:update_user()` — add invalidation call
- [ ] Add Redis-down fallback (try-except, skip cache on ConnectionError)
**Verification**: Auth works with Redis up and down

### Phase 3: Testing ⏳
- [ ] Create `tests/test_cache.py` — hit, miss, invalidation, TTL, Redis-down
- [ ] Add cache paths to `tests/test_auth.py`
- [ ] Load test: confirm <50 QPS to DB
**Verification**: All tests pass, load test meets target
```

### What Happened

| In B (design) | In tasks.md (plan) | Relationship |
|---|---|---|
| `get_cached_user(user_id: str) -> Optional[User]` | `implement interface per spec.md B` | Reference, not repeat |
| SET NX lock mechanism explained | `Implement SET NX stampede lock per B's Key Logic` | Reference |
| TTL 300s ±10% jitter | `Add TTL jitter to set_cached_user()` | Distill to action |
| Cache miss → DB query → populate | `cache lookup per B's data flow` | Reference |

**Design** stays in B. **Actions** go in tasks.md. tasks.md tells you *what to do*; B tells you *how it should work*.
