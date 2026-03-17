# Design Examples — Refactor / Migration

Scenario examples for changes that restructure code or migrate data/schemas.
These are **references, not prescriptions** — adapt dimensions to your specific change.

**Typical dimensions**: Structural Blueprint + Migration Path

Path note: when a sample includes `reference.source`, it is workspace-relative and normally starts with `.sspec/`.

---

## Refactor Example: Extract auth into service layer

Dimensions chosen: Structural Blueprint (before/after module layout), Behavioral Spec (new call chain).

```markdown
---
name: extract-auth-service
status: PLANNING
change-type: single
created: 2026-02-20T09:00:00
reference: null
---

# extract-auth-service

## A. Problem Statement

`src/auth.py` is a 2,400 LOC monolith handling JWT validation, permission checks,
and Redis caching in one file. Auth latency is 5s on cold start. No unit tests
exist because every function depends on global state.

## B. Proposed Solution

### Approach

Extract auth into a service layer with clear boundaries. The monolith becomes
three focused modules behind an `AuthService` interface. Redis caching moves
from inline calls to a dedicated cache layer.

### Key Design

#### Structural Blueprint

\`\`\`text
# Before
src/
├── auth.py              (2,400 LOC monolith)
└── middleware/
    └── auth.py          (imports directly from auth.py globals)

# After
src/
├── auth/
│   ├── __init__.py      (re-exports AuthService)
│   ├── service.py       (AuthService class — pure business logic)
│   ├── jwt.py           (JWT encode/decode/validate)
│   └── cache.py         (Redis cache layer, TTL management)
├── middleware/
│   └── auth.py          (calls AuthService, no direct Redis/JWT)
└── auth.py              (deleted)
\`\`\`

#### Behavioral Spec

\`\`\`text
Request → AuthMiddleware
  └── AuthService.authenticate(token)
        ├── cache.get(token_hash)    → HIT: return cached User
        └── MISS:
              ├── jwt.decode(token)  → extract claims
              ├── db.get_user(claims.user_id)
              ├── cache.set(token_hash, user, ttl=300)
              └── return User
\`\`\`

AuthService is the only public interface. Middleware never touches JWT or cache directly.
This makes AuthService unit-testable without Redis or HTTP.

### Key Change

**Refactor A: Extract auth service layer** — Split monolithic `auth.py` (2,400 LOC) into three focused modules behind `AuthService` interface. Redis caching moves from inline calls to dedicated `cache.py`. Middleware calls `AuthService` only — no direct JWT or cache access. The old `auth.py` is deleted entirely.

### Scope Summary

| File | Change |
|------|--------|
| `src/auth/service.py` | New — `AuthService` class with `authenticate()`, `invalidate()` |
| `src/auth/jwt.py` | New — JWT encode/decode extracted from monolith |
| `src/auth/cache.py` | New — Redis cache layer with TTL jitter |
| `src/middleware/auth.py` | Refactor to call `AuthService` instead of `auth.py` globals |
| `src/auth.py` | Delete — logic moved to `src/auth/` package |
| `tests/test_auth_service.py` | New — unit tests for AuthService (no Redis needed) |
```

---

## Large Change Variant: Use `reference/design.md`

When a refactor or migration grows beyond roughly 15 files, keep `spec.md` predictive and move exhaustive detail into `reference/design.md`.

```markdown
---
name: multi-tenant-rbac
status: PLANNING
change-type: single
created: 2026-02-15T10:00:00
reference:
  - source: ".sspec/requests/260210_multi-tenancy.md"
    type: "request"
---

# multi-tenant-rbac

## A. Problem Statement

Single-tenant auth system. Need isolated tenant data and tenant-scoped RBAC.

## B. Proposed Solution

### Approach

Add tenant isolation and RBAC on top of existing JWT auth.
Full architecture, migration sequencing, and permission matrix: see [reference/design.md](reference/design.md).

### Key Design

#### Interface Contract

\`\`\`python
@dataclass
class AuthClaims:
    user_id: str
    tenant_id: str  # NEW
    roles: list[str]
\`\`\`

### Key Change

**Refactor A: Tenant isolation + RBAC** — Add tenant-scoped data isolation and role-permission matrix on top of existing JWT auth. Full architecture, migration sequencing, and permission matrix in [reference/design.md](reference/design.md).

### Scope Summary

| File | Change |
|------|--------|
| `src/auth/` | Add tenant-aware auth and RBAC flows |
| `src/middleware/` | Inject tenant context before business handlers |
| `reference/design.md` | Full architecture, migration, and permission matrix |
```

---

## Migration Example: Add `type` field to HOWTO frontmatter

Dimensions chosen: Migration Path (before/after format, compatibility), Interface Contract (changed dataclass).

```markdown
---
name: howto-type-field
status: PLANNING
change-type: single
created: 2026-03-17T20:00:00
reference: null
---

# howto-type-field

## A. Problem Statement

All HOWTOs are listed in a flat, unfiltered list. With 20+ HOWTOs, finding
dimension-specific cards requires scanning every entry. No classification mechanism exists.

## B. Proposed Solution

### Approach

Add an optional `type` field to HOWTO frontmatter. `sspec howto list` gains `--type`
filtering. Backward compatible — existing HOWTOs without `type` continue to work.

### Key Design

#### Migration Path

\`\`\`yaml
# Before: HOWTO frontmatter
---
name: resume-change
desc: Resume an in-progress change from handover.md in 30 seconds.
---

# After: HOWTO frontmatter (type field added)
---
name: resume-change
desc: Resume an in-progress change from handover.md in 30 seconds.
type: null                    # optional, not present in existing files
---
\`\`\`

Migration strategy: backward-compatible addition.
- `type` is optional, defaults to `None` when absent
- Existing HOWTO files require zero changes
- No data migration script needed
- Rollback: simply ignore the field

#### Interface Contract

\`\`\`python
@dataclass(frozen=True, slots=True)
class HowtoInfo:
    name: str
    lookup_key: str
    description: str
    path: Path
    source: HowtoSource
    file: str
    type: str | None = None  # NEW: optional classification
\`\`\`

\`\`\`python
# howto.py — list_cmd gains --type filter
@click.option('--type', 'howto_type', default=None,
              help='Filter by howto type')
def list_cmd(howto_type: str | None, ...):
    ...
    if howto_type:
        items = [h for h in items if h.type == howto_type]
\`\`\`

### Key Change

**Feat A: HOWTO type classification** — Add optional `type` field to HOWTO frontmatter. Backward compatible: existing files without `type` default to `None` and require zero changes. `sspec howto list` gains `--type` filtering. No data migration needed; rollback = ignore the field.

### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/services/howto_service.py` | Add `type` to `HowtoInfo`; parse in `_build_howto_info` |
| `src/sspec/commands/howto.py` | Add `--type` filter to `list_cmd`; type column in output |
```
