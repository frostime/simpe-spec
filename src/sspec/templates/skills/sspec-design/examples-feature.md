# Design Examples — Feature / Bugfix

Scenario examples for changes that add new functionality or fix bugs.
These are **references, not prescriptions** — adapt to your specific change.

Path note: when a sample includes `reference.source`, it is workspace-relative and normally starts with `.sspec/`.

---

## Feature Example: Add `--tag` to `sspec change new`

```markdown
---
name: change-tags
status: PLANNING
change-type: single
created: 2026-02-15T10:00:00
reference:
  - source: ".sspec/requests/260215_change-list-ux.md"
    type: "request"
---

# change-tags

## Problem Statement

`sspec change list` returns all changes in flat order. Projects with ≥10 simultaneous
changes have no way to scope the list to a subsystem (e.g. "show only frontend changes").

## Proposed Solution

### Approach

Add optional `tags: []` to change frontmatter. The CLI exposes `--tag <label>` on
`sspec change new` and `--filter-tag <label>` on `sspec change list`.

Why tags over a free-text `area` field: tags are multi-valued, machine-parseable,
and consistent with the existing `type` field pattern in `core.py`.

### Behavior Contract

**BC-1: Changes can be tagged and filtered**

Surface: `sspec change new` and `sspec change list` CLI.

After:
- `sspec change new --tag frontend` writes `tags: [frontend]` to change frontmatter.
- `sspec change list --filter-tag frontend` shows only matching changes.
- Invalid tag input fails before any files are written.

### Implementation Changes

**feat(change): Add tag-based filtering** - Add optional `tags: []` to change frontmatter.
CLI exposes `--tag <label>` on `change new` and `--filter-tag <label>` on `change list`.
Tag validation happens before any files are written so invalid input fails fast.

Serves: BC-1.

### Scope Summary

| File | Change | Effort |
|------|--------|--------|
| `src/sspec/core.py` | feat(change): add `tags` field to `ChangeMeta`; `validate_tags()` helper | S |
| `src/sspec/services/change_service.py` | feat(change): add `tags` param in `create_change()`; `filter_tag` in `list_changes()` | M |
| `src/sspec/commands/change.py` | feat(change): add `--tag` option on `change new`; `--filter-tag` on `change list` | S |
| `src/sspec/templates/change/spec.md` | feat(change): add `tags: []` to frontmatter template | XS |

### Design Reference

→ 详细技术设计见 [design.md](./design.md)
```

**design.md** for the same change — note how interfaces and behavior are shown, not described:

```markdown
---
change: "change-tags"
created: 2026-02-15T10:00:00
---

# Design: change-tags

## Data Model

New field on `ChangeMeta`. Backward-compatible: defaults to empty list.

```python
@dataclass
class ChangeMeta:
    name: str
    status: ChangeStatus
    change_type: ChangeType
    created: str
    tags: list[str] = field(default_factory=list)  # NEW
    reference: list[ChangeRef] | None = None
```

## Interface Changes

```python
# change_service.py
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

## Behavior

```
sspec change new <name> --tag frontend --tag backend
  │
  ├── validate_tags(tags)           → check against allowlist if configured
  ├── create_change_dir(name)       → mkdir .sspec/changes/<ts>_<name>/
  ├── copy_templates()              → spec.md, tasks.md, memory.md
  └── write_frontmatter(tags=tags)  → tags: ["frontend", "backend"] in spec.md

sspec change list --filter-tag frontend
  │
  └── scan_changes()
        └── for each change: parse_frontmatter() → filter by tags
```

Tag validation happens before any change files are written — invalid input fails fast
and never leaves a partial change directory behind.
```

---

## Bugfix Example: Fix HOWTO list crash on missing frontmatter

```markdown
---
name: fix-howto-list-crash
status: PLANNING
change-type: single
created: 2026-03-10T14:00:00
reference: null
---

# fix-howto-list-crash

## Problem Statement

`sspec howto list` crashes with `KeyError: 'name'` when a howto file has empty
or malformed frontmatter. Affects any project with hand-created `.sspec/howto/` files.

## Proposed Solution

### Approach

Make `_build_howto_info` resilient to missing/malformed frontmatter by falling back
to the file stem for `name` and empty string for `desc`. Log a warning instead of crashing.

### Behavior Contract

**BC-1: Malformed HOWTO frontmatter does not crash listing**

Surface: `sspec howto list`.

Before:
- A HOWTO with missing or malformed frontmatter can raise `KeyError` and stop the command.

After:
- The command logs a warning, uses the file stem as `name`, uses an empty `desc`, and continues listing other HOWTOs.

### Implementation Changes

**fix(howto): Add resilient frontmatter parsing** - Make `_build_howto_info` fall back to file
stem for `name` and empty string for `desc` when frontmatter is missing or malformed.
Log a warning instead of crashing. Parse failures stay local so one bad file never
takes down the whole list command.

Serves: BC-1.

### Scope Summary

| File | Change | Effort |
|------|--------|--------|
| `src/sspec/services/howto_service.py` | fix(howto): add fallback logic in `_build_howto_info` | S |
```

**design.md** — before/after output and the fix logic, shown concretely:

```markdown
---
change: "fix-howto-list-crash"
created: 2026-03-10T14:00:00
---

# Design: fix-howto-list-crash

## Before / After

```text
# Before
$ sspec howto list
Traceback (most recent call last):
  ...
KeyError: 'name'

# After
$ sspec howto list
WARNING: Malformed frontmatter in .sspec/howto/bad-file.md, using filename as name.
- name: bad-file
  source: project
  desc: (no description)
- name: resume-change
  source: builtin
  desc: Resume an in-progress change from memory.md in 30 seconds.
```

## Fix Logic

```
_build_howto_info(path)
  │
  ├── parse_frontmatter(content)
  │     ├── valid YAML    → extract name, desc, type
  │     └── malformed/empty → return {}
  │
  ├── name = meta.get('name') or path.stem    # fallback — never KeyError
  ├── desc = meta.get('desc') or ''           # fallback
  └── return HowtoInfo(...)                   # always returns, never raises
```
```

---

## spec.md → tasks.md Boundary

spec.md defines *how it should work*. tasks.md defines *what to do*. Tasks reference spec labels — never repeat design logic.

| Content | Where |
|---------|-------|
| Why this approach | spec.md Approach |
| What the interfaces / behavior are | design.md |
| What each labeled item does | spec.md Implementation Changes |
| File-level actions | tasks.md phases |
| How to verify | tasks.md verification |
