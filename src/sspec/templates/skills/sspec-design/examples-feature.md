# Design Examples — Feature / Bugfix

Scenario examples for changes that add new functionality or fix bugs.
These are **references, not prescriptions** — adapt dimensions to your specific change.

**Typical dimensions**: Interface Contract + Behavioral Spec + Impact Map

Path note: when a sample includes `reference.source`, it is workspace-relative and normally starts with `.sspec/`.

---

## Feature Example: Add `--tag` to `sspec change new`

Dimensions chosen: Interface Contract (new CLI option + data field), Behavioral Spec (tag validation flow), Impact Map (scope table).

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

## A. Problem Statement

`sspec change list` returns all changes in flat order. Projects with ≥10 simultaneous
changes have no way to scope the list to a subsystem (e.g. "show only frontend changes").

## B. Proposed Solution

### Approach

Add optional `tags: []` to change frontmatter. The CLI exposes `--tag <label>` on
`sspec change new` and `--filter-tag <label>` on `sspec change list`.

Why tags over a free-text `area` field: tags are multi-valued, machine-parseable,
and consistent with the existing `type` field pattern in `core.py`.

### Key Design

#### Interface Contract

\`\`\`python
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
\`\`\`

\`\`\`python
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
\`\`\`

#### Behavioral Spec

\`\`\`
sspec change new <name> --tag frontend --tag backend
  │
  ├── validate_tags(tags)           → check against allowlist if configured
  ├── create_change_dir(name)       → mkdir .sspec/changes/<ts>_<name>/
  ├── copy_templates()              → spec.md, tasks.md, handover.md
  └── write_frontmatter(spec_path, tags=tags)
        └── tags: ["frontend", "backend"]  written to spec.md YAML

sspec change list --filter-tag frontend
  │
  └── scan_changes()
        └── for each change: parse_frontmatter() → filter by tags
\`\`\`

Note: tag validation happens before any change files are written, so invalid input fails fast and never leaves a partial change directory behind.

#### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/core.py` | Add `tags` field to `ChangeMeta`; `validate_tags()` helper |
| `src/sspec/services/change_service.py` | `tags` param in `create_change()`; `filter_tag` in `list_changes()` |
| `src/sspec/commands/change.py` | `--tag` option on `change new`; `--filter-tag` on `change list` |
| `src/sspec/templates/change/spec.md` | Add `tags: []` to frontmatter template |
```

---

## Bugfix Example: Fix HOWTO list crash on missing frontmatter

Dimensions chosen: Outcome Preview (before/after CLI output), Behavioral Spec (error handling flow).

```markdown
---
name: fix-howto-list-crash
status: PLANNING
change-type: single
created: 2026-03-10T14:00:00
reference: null
---

# fix-howto-list-crash

## A. Problem Statement

`sspec howto list` crashes with `KeyError: 'name'` when a howto file has empty
or malformed frontmatter. Affects any project with hand-created `.sspec/howto/` files.

## B. Proposed Solution

### Approach

Make `_build_howto_info` resilient to missing/malformed frontmatter by falling back
to the file stem for `name` and empty string for `desc`. Log a warning instead of crashing.

### Key Design

#### Outcome Preview

\`\`\`text
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
  desc: Resume an in-progress change from handover.md in 30 seconds.
\`\`\`

#### Behavioral Spec

\`\`\`
_build_howto_info(path)
  │
  ├── parse_frontmatter(content)
  │     ├── valid YAML    → extract name, desc, type
  │     └── malformed/empty → return {}
  │
  ├── name = meta.get('name') or path.stem    # fallback
  ├── desc = meta.get('desc') or ''           # fallback
  └── return HowtoInfo(...)                   # never None for parse issues
\`\`\`

Note: parse failures stay local to `_build_howto_info()`, so one malformed project HOWTO no longer takes down the whole list command.
```

---

## B → tasks.md Boundary

B defines *how it should work*. tasks.md defines *what to do*. Tasks reference B — never repeat it.

| Content | Where | Example |
|---------|-------|---------|
| **Why** this approach | spec.md B → Approach | "Tags over free-text because multi-valued" |
| **What** the design is | spec.md B → Key Design | Interface signatures, behavior diagrams |
| **What to do** (file-level) | tasks.md phases | `- [ ] Add tags field to ChangeMeta in core.py` |
| **How to verify** | tasks.md verification | `sspec change new foo --tag x && sspec change list --filter-tag x shows foo` |
