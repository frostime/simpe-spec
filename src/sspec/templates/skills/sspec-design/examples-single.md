# Design Examples — Single Change

Concrete examples of spec.md (A + B) for single/sub changes at three complexity levels.
Reference this when filling spec.md in the design phase.

**📚 Standards**: See [SKILL.md](./SKILL.md) for Presentation Rules 1–4 and workflow.

---

## Table of Contents

- [Simple Example](#simple-example) (L23) — ≤5 files, inline design
- [Medium Example](#medium-example) (L57) — 5-15 files, all 4 Presentation Rules
- [Complex Example](#complex-example) (L155) — >15 files, reference/ design
- [B → tasks.md Boundary](#b--tasksmd-boundary) (L185) — what goes where

---

## Simple Example

≤5 files. Interface/data model inline in Approach. Rules 1 and 2 apply in abbreviated form.

````markdown
---
name: request-tldr-autofill
status: PLANNING
change-type: single
created: 2026-02-15T10:00:00
reference:
  - source: "requests/260215_request-ux.md"
    type: "request"
---

# request-tldr-autofill

## A. Problem Statement

`sspec request list` displays `tldr: ""`  for most requests because users skip the field.
The empty string makes the list view useless as a navigation aid.

## B. Proposed Solution

### Approach

Auto-populate `tldr` from the first non-empty paragraph of `## Background` when
the request is saved/created. Users can still override it manually.

Why first Background paragraph: it's the most stable summary of context and is
required by template — always present.

### Key Design

```python
# src/sspec/services/request_service.py
def extract_tldr(content: str) -> str:
    """Return first non-empty paragraph of ## Background, truncated to 120 chars."""
```

Flow: `create_request()` → `extract_tldr(content)` → write to frontmatter `tldr`.
Applied only when `tldr` is empty string or missing; never overwrites user-set value.
````

---

## Medium Example

5-15 files. Dedicated sub-sections. Demonstrates all **4 Presentation Rules**.

This example: add `--tag` to `sspec change new` so changes can carry project-defined
labels (e.g. `frontend`, `backend`, `docs`) for filtering in `sspec change list`.

````markdown
---
name: change-tags
status: PLANNING
change-type: single
created: 2026-02-15T10:00:00
reference:
  - source: "requests/260215_change-list-ux.md"
    type: "request"
---

# change-tags

## A. Problem Statement

`sspec change list` returns all changes in flat order. Projects with ≥10 simultaneous
changes have no way to scope the list to a subsystem (e.g. "show only frontend changes").
Users work around this by grepping handover.md, which is fragile.

## B. Proposed Solution

### Approach

Add optional `tags: []` to change frontmatter. The CLI exposes `--tag <label>` on
`sspec change new` and `--filter-tag <label>` on `sspec change list`.

Why tags over a free-text `area` field: tags are multi-valued, machine-parseable,
and consistent with the existing `type` field pattern in `core.py`.

### Key Design

#### Interface Design

```python
# src/sspec/core.py — new type alias
ChangeTag = str  # validated against project-defined allowed tags

@dataclass
class ChangeMeta:
    name: str
    status: ChangeStatus
    change_type: ChangeType
    created: str
    tags: list[ChangeTag] = field(default_factory=list)  # NEW
    reference: list[ChangeRef] | None = None
```

```python
# src/sspec/services/change_service.py — updated signature
def create_change(
    name: str,
    root: bool = False,
    from_request: str | None = None,
    tags: list[str] | None = None,   # NEW
) -> ChangePaths: ...

def list_changes(
    filter_tag: str | None = None,   # NEW
) -> list[ChangeMeta]: ...
```

#### Data Flow

```
sspec change new <name> --tag frontend --tag backend
  │
  ├── validate_tags(tags)           → check tag values (allow all if no allowlist configured)
  ├── create_change_dir(name)       → mkdir .sspec/changes/<ts>_<name>/
  ├── copy_templates()              → spec.md, tasks.md, handover.md
  └── write_frontmatter(spec_path, tags=tags)
        └── tags: ["frontend", "backend"]  written to spec.md YAML

sspec change list --filter-tag frontend
  │
  └── scan_changes()
        └── for each change: parse_frontmatter() → filter by tags
```

#### Key Logic

**Feat A: Tag allowlist** — If `project.md` defines `allowed-tags: [...]`, validate
that each `--tag` value is in the list. If no allowlist configured, accept any string.

**Feat B: `change new --tag`** — One or more `--tag` options allowed; stored as YAML
list in frontmatter `tags` field.

**Feat C: `change list --filter-tag`** — Only shows changes whose `tags` list contains
the given value. Case-insensitive match.

#### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/core.py` | Add `tags` field to `ChangeMeta`; `validate_tags()` helper |
| `src/sspec/services/change_service.py` | `tags` param in `create_change()`; `filter_tag` in `list_changes()` |
| `src/sspec/commands/change.py` | `--tag` option on `change new`; `--filter-tag` on `change list` |
| `src/sspec/templates/change/spec.md` | Add `tags: []` to frontmatter template |
````

---

## Complex Example

>15 files, architectural change. Core approach in B, detailed design in `reference/design.md`.

````markdown
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
Support multiple organizations on the same instance with isolated data and RBAC.
Target: 50 tenants within 3 months.

## B. Proposed Solution

### Approach

Add tenant isolation layer + RBAC on top of existing JWT auth. Every request carries
`tenant_id` in JWT claims. A middleware injects tenant context before any DB query.
Roles are tenant-scoped (admin in Org A ≠ admin in Org B).

Full architecture, data model, and API contracts: see [reference/design.md](reference/design.md).

### Key Design

**Core interfaces** (summary — full detail in reference/design.md):

```python
# Tenant model
@dataclass
class Tenant:
    id: str
    name: str
    plan: Plan
    created_at: datetime

# JWT claims extension
@dataclass
class AuthClaims:
    user_id: str
    tenant_id: str      # NEW
    roles: list[str]    # NEW (tenant-scoped role names)
    exp: int
```

**Core flow**: `Request → TenantMiddleware (extract tenant_id from JWT) → set request.tenant → DB queries filtered by tenant_id via SQLAlchemy mixin`.

Full data model, migration strategy, and permission matrix: [reference/design.md](reference/design.md).
````

---

## B → tasks.md Boundary

B defines *how it should work*. tasks.md defines *what to do*. Tasks reference B — never repeat it.

| Content | Where | Example |
|---------|-------|---------|
| **Why** this approach | spec.md B → Approach | "Tags over free-text because multi-valued" |
| **What** the design is | spec.md B → Key Design | Interface signatures, data models, flow diagrams |
| **What to do** (file-level) | tasks.md phases | `- [ ] Add tags field to ChangeMeta in core.py` |
| **How to verify** | tasks.md verification | `sspec change new foo --tag x && sspec change list --filter-tag x shows foo` |

### ❌ Bad — Repeating B's interface in tasks.md

```markdown
### Phase 1: Core Types ⏳
- [ ] Add to `ChangeMeta` in `core.py`:
  - `tags: list[ChangeTag] = field(default_factory=list)`    ← repeated from B!
  - `ChangeTag = str`                                          ← repeated from B!
```

### ✅ Good — Referencing B

```markdown
### Phase 1: Core Types ⏳
- [ ] Add `tags` field + `validate_tags()` to `src/sspec/core.py` per spec.md §B Interface Design
**Verification**: `core.py` parses `tags: ["frontend"]` in spec.md frontmatter correctly
```
