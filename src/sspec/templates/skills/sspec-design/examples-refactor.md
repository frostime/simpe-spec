# Design Examples — Refactor / Migration

Scenario examples for changes that restructure code or migrate data/schemas.
These are **references, not prescriptions** — adapt to your specific change.

Path note: when a sample includes `reference.source`, it is workspace-relative and normally starts with `.sspec/`.

---

## Refactor Example: Extract auth into service layer

```markdown
---
name: extract-auth-service
status: PLANNING
change-type: single
created: 2026-02-20T09:00:00
reference: null
---

# extract-auth-service

## Problem Statement

`src/auth.py` is a 2,400 LOC monolith handling JWT validation, permission checks,
and Redis caching in one file. Auth latency is 5s on cold start. No unit tests
exist because every function depends on global state.

## Proposed Solution

### Approach

Extract auth into a service layer with clear boundaries. The monolith becomes
three focused modules behind an `AuthService` interface. Redis caching moves
from inline calls to a dedicated cache layer.

### Key Change

**Refactor A: Extract auth service layer** — Split monolithic `auth.py` (2,400 LOC)
into three focused modules behind `AuthService` interface. Redis caching moves to
dedicated `cache.py`. Middleware calls `AuthService` only — no direct JWT or cache
access. The old `auth.py` is deleted entirely.

### Scope Summary

| File | Change |
|------|--------|
| `src/auth/service.py` | New — `AuthService` class with `authenticate()`, `invalidate()` |
| `src/auth/jwt.py` | New — JWT encode/decode extracted from monolith |
| `src/auth/cache.py` | New — Redis cache layer with TTL jitter |
| `src/middleware/auth.py` | Refactor to call `AuthService` instead of `auth.py` globals |
| `src/auth.py` | Delete — logic moved to `src/auth/` package |
| `tests/test_auth_service.py` | New — unit tests for AuthService (no Redis needed) |

### Design Reference

→ 详细技术设计见 [design.md](./design.md)
```

**design.md** — before/after structure and call chain shown directly, no prose narration:

```markdown
---
change: "extract-auth-service"
created: 2026-02-20T09:00:00
---

# Design: extract-auth-service

## Module Structure

```text
# Before
src/
├── auth.py              (2,400 LOC monolith)
└── middleware/
    └── auth.py          (imports directly from auth.py globals)

# After
src/
├── auth/
│   ├── __init__.py      (re-exports AuthService)
│   ├── service.py       (AuthService — pure business logic, no global state)
│   ├── jwt.py           (JWT encode/decode/validate)
│   └── cache.py         (Redis cache layer, TTL management)
├── middleware/
│   └── auth.py          (calls AuthService only — no direct Redis/JWT)
└── auth.py              (deleted)
```

## Public Interface

```python
class AuthService:
    def authenticate(self, token: str) -> User: ...
    def invalidate(self, user_id: str) -> None: ...
```

Middleware never touches JWT or cache directly. This makes `AuthService`
unit-testable without Redis or HTTP.

## Call Chain

```
Request → AuthMiddleware
  └── AuthService.authenticate(token)
        ├── cache.get(token_hash)    → HIT: return cached User
        └── MISS:
              ├── jwt.decode(token)  → extract claims
              ├── db.get_user(claims.user_id)
              ├── cache.set(token_hash, user, ttl=300)
              └── return User
```
```

---

## Migration Example: Add `type` field to HOWTO frontmatter

```markdown
---
name: howto-type-field
status: PLANNING
change-type: single
created: 2026-03-17T20:00:00
reference: null
---

# howto-type-field

## Problem Statement

All HOWTOs are listed in a flat, unfiltered list. With 20+ HOWTOs, finding
dimension-specific cards requires scanning every entry. No classification mechanism exists.

## Proposed Solution

### Approach

Add an optional `type` field to HOWTO frontmatter. `sspec howto list` gains `--type`
filtering. Backward compatible — existing HOWTOs without `type` continue to work.

### Key Change

**Feat A: HOWTO type classification** — Add optional `type` field to HOWTO frontmatter.
Backward compatible: existing files without `type` default to `None` and require zero
changes. `sspec howto list` gains `--type` filtering. No data migration needed.

### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/services/howto_service.py` | Add `type` to `HowtoInfo`; parse in `_build_howto_info` |
| `src/sspec/commands/howto.py` | Add `--type` filter to `list_cmd`; type column in output |

### Design Reference

→ 详细技术设计见 [design.md](./design.md)
```

**design.md** — schema before/after and interface change shown side by side:

```markdown
---
change: "howto-type-field"
created: 2026-03-17T20:00:00
---

# Design: howto-type-field

## Schema Change

```yaml
# Before
---
name: resume-change
desc: Resume an in-progress change from memory.md in 30 seconds.
---

# After (type is optional — existing files require zero changes)
---
name: resume-change
desc: Resume an in-progress change from memory.md in 30 seconds.
type: workflow   # optional; absent = None
---
```

## Data Model

```python
@dataclass(frozen=True, slots=True)
class HowtoInfo:
    name: str
    lookup_key: str
    description: str
    path: Path
    source: HowtoSource
    file: str
    type: str | None = None  # NEW — optional classification
```

## Interface Change

```python
# howto.py — list_cmd gains --type filter
@click.option('--type', 'howto_type', default=None, help='Filter by howto type')
def list_cmd(howto_type: str | None, ...):
    ...
    if howto_type:
        items = [h for h in items if h.type == howto_type]
```

Migration strategy: backward-compatible addition. `type` defaults to `None` when
absent. No migration script needed. Rollback = ignore the field.
```

---

## Large Refactor Variant: When design.md grows large

When a refactor spans >15 files, keep spec.md predictive and move exhaustive detail into design.md.
The spec.md Key Change still labels every independent item — design.md carries the full technical depth.

```markdown
### Key Change

**Refactor A: Tenant isolation + RBAC** — Add tenant-scoped data isolation and
role-permission matrix on top of existing JWT auth.

### Scope Summary

| File | Change |
|------|--------|
| `src/auth/` | Add tenant-aware auth and RBAC flows |
| `src/middleware/` | Inject tenant context before business handlers |

### Design Reference

→ 详细技术设计见 [design.md](./design.md)
```

The design.md then carries the full architecture, migration sequencing, and permission matrix —
without cluttering the spec that the user reviews at the gate.
