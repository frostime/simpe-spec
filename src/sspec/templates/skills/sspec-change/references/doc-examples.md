# Document Examples: spec.md & tasks.md

Detailed examples for spec.md and tasks.md standards. Load when you need concrete examples of how to write these documents.

**📚 For standards and rules**: See [doc-standards.md](./doc-standards.md)

---

## Table of Contents

- [Section B Examples](#section-b-examples) (L18-99) — Simple, Medium, Complex
- [Section C Examples](#section-c-examples) (L100-155) — single/sub, root
- [Complete Example Flow](#complete-example-flow) (L156-272) — B → C → tasks.md
- [Duplication Avoidance](#duplication-avoidance) (L273-END)

---

## Section B Examples

### Example 1: Simple (≤5 files, clear logic)

Interface/data model inline in Approach:

```markdown
## B. Proposed Solution
### Approach
Add JWT token refresh mechanism to reduce re-auth friction.

**Interface**: Modify `src/auth/jwt.py:validate_token()` to accept optional `refresh=True` param.
Returns new token if expiry <5min.

**Why**: Refresh-on-expire simpler than standalone refresh endpoint; no client changes needed.

### Key Changes
- `src/auth/jwt.py` — token validation + refresh logic
- `src/middleware/auth.py` — integrate refreshed token in response header
```

---

### Example 2: Medium (5-15 files, cross-module)

Dedicated sub-sections for Interface Design, Data Model, Key Logic:

```markdown
## B. Proposed Solution
### Approach
Implement Redis-based auth cache to reduce DB load (500 QPS → <50 QPS).

### Interface Design
**New Module**: `src/services/cache.py`
- `get_cached_user(user_id: str) -> Optional[User]`
- `set_cached_user(user: User, ttl: int = 300)`
- `invalidate_user_cache(user_id: str)`

**Modified**: `src/services/auth.py`
- `authenticate(token: str) -> User`: Add cache lookup before DB query

### Data Model
**Cache Key Format**: `user:<user_id>` → JSON serialized User
**TTL**: 5 minutes (300s)

### Key Logic
1. Check cache: `get_cached_user(user_id)`
2. If miss → query DB → `set_cached_user()`
3. On user update → `invalidate_user_cache()`

### Key Changes
- `src/services/cache.py` — new caching layer
- `src/services/auth.py` — cache integration
- `src/services/user.py` — cache invalidation on update
```

---

### Example 3: Complex (>15 files, architectural)

Link to detailed design in reference/:

```markdown
## B. Proposed Solution
### Approach
Refactor auth system to support multi-tenancy with role-based access control (RBAC).

**Design**: See `reference/auth-rbac-design.md` for full architecture, data model, and API contracts.

**Core Changes**:
- Tenant isolation layer
- Role-permission matrix
- Token claims extension (tenant_id, roles)

### Key Changes
- `src/auth/` — complete refactor (see reference/)
- `src/models/` — new Tenant, Role, Permission models
- `src/middleware/` — tenant context injection
```

---

## Section C Examples

### Example 1: single/sub change

File-level mentions, references Section B:

```markdown
## C. Implementation Strategy

### Phase 1: Cache Module
- `src/services/cache.py` — create, implement interface per Section B
- Uses Redis client from existing `config.py`

### Phase 2: Auth Integration
- `src/services/auth.py` — modify `authenticate()`, add cache lookup per B's Key Logic step 1-3
- `src/services/user.py` — modify `update_user()`, add cache invalidation

### Phase 3: Testing & Validation
- `tests/test_cache.py` — create, cover get/set/invalidate
- `tests/test_auth.py` — add cache hit/miss scenarios

### Dependencies
- Phase 2 depends on Phase 1 (cache module must exist)

### Risks & Mitigations
- **Risk**: Redis unavailable → **Mitigation**: Fallback to direct DB (try-except wrapper in cache.py)
- **Risk**: Cache stampede on popular users → **Mitigation**: Add TTL jitter (±10%)
```

---

### Example 2: root change

Milestone-level (one phase per sub-change):

```markdown
## C. Implementation Strategy

### Phase 1: Tenant Isolation Layer
- **Sub-change**: (filled when created via `sspec change new --from <root>`)
- **Goal**: Tenant-scoped queries working in auth + user modules
- **Dependencies**: None (foundational)
- **Scope**: `src/models/tenant.py`, `src/auth/context.py`, `src/services/auth.py`, `src/services/user.py`

### Phase 2: RBAC Layer
- **Sub-change**: (filled when created)
- **Goal**: Role-permission matrix functional, token claims extended
- **Dependencies**: Phase 1 (requires tenant context)
- **Scope**: `src/models/role.py`, `src/auth/jwt.py`, `src/middleware/rbac.py`

### Risks
- Phase 1 failure blocks entire change → Mitigation: Allocate extra buffer for Phase 1
```

---

## Complete Example Flow

Medium complexity change: Redis auth cache

### Step 1: Section B (Design)

```markdown
## B. Proposed Solution
### Approach
Implement Redis-based auth cache to reduce DB load (500 QPS → <50 QPS).

### Interface Design
**New Module**: `src/services/cache.py`
- `get_cached_user(user_id: str) -> Optional[User]`
- `set_cached_user(user: User, ttl: int = 300)`
- `invalidate_user_cache(user_id: str)`

**Modified**: `src/services/auth.py`
- `authenticate(token: str) -> User`: Add cache lookup before DB query

### Data Model
**Cache Key Format**: `user:<user_id>` → JSON serialized User
**TTL**: 5 minutes (300s)

### Key Logic
1. Check cache: `get_cached_user(user_id)`
2. If miss → query DB → `set_cached_user()`
3. On user update → `invalidate_user_cache()`

### Key Changes
- `src/services/cache.py` — new caching layer
- `src/services/auth.py` — cache integration
- `src/services/user.py` — cache invalidation on update
```

---

### Step 2: Section C (Plan)

```markdown
## C. Implementation Strategy

### Phase 1: Cache Module
- `src/services/cache.py` — create, implement interface per Section B
- Uses Redis client from existing `config.py`

### Phase 2: Auth Integration
- `src/services/auth.py` — modify `authenticate()`, add cache lookup per B's Key Logic
- `src/services/user.py` — modify `update_user()`, add cache invalidation

### Phase 3: Testing & Validation
- `tests/test_cache.py` — create, cover get/set/invalidate
- `tests/test_auth.py` — add cache hit/miss scenarios

### Dependencies
- Phase 2 depends on Phase 1 (cache module must exist)

### Risks & Mitigations
- **Risk**: Redis unavailable → **Mitigation**: Fallback to direct DB (try-except in cache.py)
- **Risk**: Cache stampede → **Mitigation**: Add TTL jitter (±10%)
```

---

### Step 3: tasks.md (Execution)

```markdown
---
change: "auth-cache"
updated: ""
---

# Implementation Tasks

## Legend
`[ ]` Todo | `[x]` Done (implemented + verified)

## Tasks

### Phase 1: Cache Module 🚧
- [ ] Create `src/services/cache.py` — implement `get_cached_user()`
- [ ] Implement `set_cached_user()` with TTL jitter
- [ ] Implement `invalidate_user_cache()`
- [ ] Add Redis config to `config.py` with fallback
**Verification**: `pytest tests/test_cache.py` passes

### Phase 2: Auth Integration ⏳
- [ ] Modify `src/services/auth.py` — add cache lookup in `authenticate()`
- [ ] Add fallback to DB query if cache miss
- [ ] Modify `src/services/user.py` — add cache invalidation in `update_user()`
**Verification**: Auth flow works with cache enabled/disabled

### Phase 3: Testing & Validation ⏳
- [ ] Create `tests/test_cache.py` — cover get/set/invalidate
- [ ] Add cache hit scenario in `tests/test_auth.py`
- [ ] Add cache miss scenario in `tests/test_auth.py`
- [ ] Add Redis unavailable fallback test
**Verification**: All tests pass, coverage >90%

---

## Progress

**Overall**: 0%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 0% | 🚧 |
| Phase 2 | 0% | ⏳ |
| Phase 3 | 0% | ⏳ |

**Recent**:
- (none yet)
```

---

## Duplication Avoidance

**Key Principle**: Define once, reference elsewhere.

| Where | Content |
|-------|---------|
| **Section B** | Define `CacheService` interface (4 methods), data model, logic |
| **Section C** | "implement interface per Section B" — no copy-paste |
| **tasks.md** | "implement `get_cached_user()`" — break into atomic tasks |

**❌ Bad** (repeating interface in C):
```markdown
## C. Implementation Strategy
### Phase 1: Cache Module
- `src/services/cache.py` — create with:
  - `get_cached_user(user_id: str) -> Optional[User]`  ← Repeated from B!
  - `set_cached_user(user: User, ttl: int = 300)`      ← Repeated from B!
```

**✅ Good** (referencing B):
```markdown
## C. Implementation Strategy
### Phase 1: Cache Module
- `src/services/cache.py` — create, implement interface per Section B
```
