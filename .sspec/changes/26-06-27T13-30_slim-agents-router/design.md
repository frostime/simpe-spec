---
change: "slim-agents-router"
created: 2026-06-27T13:30:14
---

# Design: slim-agents-router

## 1. Target Structure

```text
Installed project
├── AGENTS.md                         # auto-read router, managed SSPEC block only
└── .sspec/
    ├── project.md                    # user-managed project context; read first
    ├── SSPEC.rule.md                 # managed full sspec workflow rule
    ├── spec-docs/                    # read by project.md index match
    ├── skills/                       # loaded by phase/task trigger
    ├── changes/
    └── requests/

Template source
└── src/sspec/templates/
    ├── AGENTS.md                     # router source
    ├── SSPEC.rule.md                 # full rule source
    ├── project.md                    # user file source for init only
    └── skills/
```

No `rules/` directory is introduced. `SSPEC.rule.md` is a single top-level `.sspec` managed file.

## 2. Ownership Model

| Installed path | Source template | Owner | Update behavior |
|---|---|---|---|
| `AGENTS.md` managed block | `src/sspec/templates/AGENTS.md` | sspec | Replaced inside `SSPEC:START/END`; outside content preserved |
| `.sspec/SSPEC.rule.md` | `src/sspec/templates/SSPEC.rule.md` | sspec-managed | Init creates; update tracks hash; modified/unknown skipped unless `--force` |
| `.sspec/project.md` | `src/sspec/templates/project.md` | user | Init creates; update does not overwrite |
| `.sspec/skills/*` | `src/sspec/templates/skills/*` | sspec-managed hub + user extensions | Existing skill update/orphan/link behavior unchanged |
| `.sspec/spec-docs/*` | user/CLI-created docs | user | Read only by relevance from project.md index |

## 3. Root Router Content Outline

```text
<!-- SSPEC:START -->
# sspec Router

SSPEC_SCHEMA::{{SCHEMA_VERSION}}

## Project Context
- If `.sspec/project.md` exists, read it before project-specific work.
- Use Key Paths, Conventions, and Spec-Docs Index.
- Read spec-docs only when the current task matches the index entry.

## Full Rule Trigger
Read `.sspec/SSPEC.rule.md` when:
- user mentions sspec/spec/change/request/spec-doc/align/argue;
- task references `.sspec/requests/*`, `.sspec/changes/*`, `.sspec/spec-docs/*`;
- user asks to create/update project context, request, change, spec-doc, memory, or workflow state;
- user asks to clarify/design/plan/implement/review using sspec;
- change is non-micro: broad, architectural, API/schema/data/security/privacy/UX affecting, or hard to predict safely.

Micro/local/reversible edits may be done directly.

## Skills
- After reading `.sspec/SSPEC.rule.md`, load matching `.sspec/skills/<name>/SKILL.md` before that phase/task.
- If a SKILL references relative files, read them relative to that SKILL directory.

## Output Safety
- When showing content that contains fenced code blocks, use a longer outer fence.
<!-- SSPEC:END -->
```

The exact final wording may be compressed, but it MUST preserve the trigger categories above.

## 4. Full Rule Content Outline

`src/sspec/templates/SSPEC.rule.md` receives the current full protocol from `src/sspec/templates/AGENTS.md`:

```text
# .sspec Agent Protocol
SSPEC_SCHEMA::{{SCHEMA_VERSION}}

0. Structure
1. Dispatch
2. Change Lifecycle
   2.1 Change Scale
   2.2 Mini Change Protocol
3. User-Agent Protocol
4. Peripheral Rule
```

Adjustments required inside the full rule:
- Treat root `AGENTS.md` as router, not full protocol.
- Keep `.sspec/project.md` as the first context read for project-specific work.
- Keep references to SKILL/HOWTO behavior unchanged unless they incorrectly name `AGENTS.md` as the full source.

## 5. CLI Flow

### `project init`

```text
initialize_project()
  → create .sspec directories
  → install skills
  → copy UPDATABLE_FILES
       SSPEC.rule.md → .sspec/SSPEC.rule.md
  → copy USER_FILES
       project.md → .sspec/project.md
  → compute file_hashes
       skills/<name>
       SSPEC.rule.md
  → save .meta.json
  → update_root_agents_block(templates/AGENTS.md router)
```

User-facing output should stay simple:

```text
+ Initialized sspec project in .sspec/
+ Installed core skills to .sspec/skills/ (copy)
+ Created/Updated root AGENTS.md

Structure:
  .sspec/
  ├── project.md       # Project overview
  ├── SSPEC.rule.md    # Managed sspec workflow rule
  ├── spec-docs/       # Project-level specification documents
  ├── changes/         # Active change proposals
  └── requests/        # Ad-hoc AI requests
```

### `project update`

```text
prepare_meta_for_project_update()
  → old_hashes includes optional SSPEC.rule.md
collect_update_candidates()
  → template files from UPDATABLE_FILES include SSPEC.rule.md
  → skills unchanged
update_root_agents_block(..., dry_run=True)
  → root router block handled separately as today
apply actions
  → normal file update path writes .sspec/SSPEC.rule.md
save_meta()
  → records SSPEC.rule.md hash when updated/current backfilled
```

Update status examples:

| Installed state | Old hash | Current vs template | Status | Default action | `--force` action |
|---|---|---|---|---|---|
| missing | any | n/a | `missing` | create | create |
| matches template | absent or same | same | `current` | skip/backfill | skip/backfill |
| unchanged from old managed version | old hash matches current | differs from new | `updatable` | update | update |
| user edited | old hash differs from current | differs from new | `modified` | skip | overwrite |
| unknown local file | absent | differs from new | `unknown` | skip | update |

## 6. Protocol Schema and Migration Compatibility

This change bumps the sspec protocol schema, not the `.meta.json` schema.

```python
SCHEMA_VERSION = '7.0'
META_SCHEMA = '2.1'  # unchanged
UPDATABLE_FILES = ['SSPEC.rule.md']
```

Meaning of `7.0`:

```text
6.2 installed layout
  root AGENTS.md = full protocol
  .sspec/project.md = project context

7.0 installed layout
  root AGENTS.md = router
  .sspec/SSPEC.rule.md = full protocol
  .sspec/project.md = project context
```

Current code already has a schema-chain for `meta_schema`, but `sspec_schema` is currently a protocol marker only. For this change, do not introduce a full `sspec_schema` migration runner. Use the existing managed-template update flow and add one explicit metadata drift check:

```python
sspec_schema_needs_update = meta.get('sspec_schema') != SCHEMA_VERSION
```

`sspec_schema_needs_update` participates in metadata persistence so `project update` records `7.0` even when the only protocol change is schema drift or root AGENTS/router sync.

No future-version rejection is added for `sspec_schema` in this change. `meta_schema` keeps the existing fail-fast future-schema protection.

## 7. Hash/Data Contract

No meta schema bump is required.

```json
{
  "meta_schema": "2.1",
  "sspec_schema": "7.0",
  "file_hashes": {
    "SSPEC.rule.md": "<rendered-template-hash>",
    "skills/sspec-design": "<dir-hash>"
  },
  "managed_skills": ["sspec-design"],
  "skill_locations": [".sspec/skills"]
}
```

Rationale:
- `file_hashes` already tracks arbitrary managed template paths.
- `UPDATABLE_FILES` already drives candidate collection for `.sspec` files.
- `project.md` remains excluded because it is a user file.
- The schema migration pattern is applied at the principle level: explicit schema marker, no structural inference, deterministic update path. A full Markov-chain runner is deferred until sspec protocol migrations need non-template data transforms.

## 8. Portable Compatibility Shim

Current resolver:

```python
resource = _templates_root().joinpath('AGENTS.md')
```

Target resolver:

```python
resource = _templates_root().joinpath('SSPEC.rule.md')
```

Public behavior stays:

```text
sspec portable read rule:sspec
  → returns full sspec rule content
  → source path ends with src/sspec/templates/SSPEC.rule.md
```

No change to `sspec portable`, resource grammar, portable overlay, or bootstrap output.

## 9. Internal Reference Cleanup

Known reference updates:

| Reference | Target wording |
|---|---|
| `src/sspec/templates/skills/sspec-design/SKILL.md`: `Use AGENTS.md Scale Assessment` | `Use .sspec/SSPEC.rule.md Change Scale` |
| README folder layout: `AGENTS.md ← the protocol` | `AGENTS.md ← lightweight router`; add `SSPEC.rule.md ← managed workflow rule` |
| `.sspec/spec-docs/agents-sync.md` | Document router block sync plus rule file management |
| `.sspec/spec-docs/meta-json.md` | Document `SSPEC.rule.md` as a managed `file_hashes` entry |
| portable tests expecting `AGENTS.md` source | Expect `SSPEC.rule.md` source |

## 10. Verification Matrix

| Contract | Test surface | Expected |
|---|---|---|
| BC-1 | `tests/test_agents_service.py` | Generated `AGENTS.md` has markers, project.md trigger, SSPEC.rule.md trigger, and no full lifecycle body |
| BC-2 | `tests/test_project_init_service.py` | Init creates `.sspec/SSPEC.rule.md`; `.meta.json.file_hashes` contains `SSPEC.rule.md` |
| BC-2 | `tests/test_project_update_service.py` | `collect_update_candidates()` includes `SSPEC.rule.md`; local edits become `modified` or `unknown` |
| BC-3 | `tests/test_project_command.py` | `project update --dry-run` reports missing rule creation and root AGENTS router update when applicable |
| BC-4 | `tests/test_portable_service.py`, `tests/test_portable_command.py` | `rule:sspec` source path ends with `SSPEC.rule.md` and content contains full protocol |
| BC-5 | `tests/test_project_command.py` | Old project with `sspec_schema = 6.2` updates to `.meta.json.sspec_schema == 7.0` |
| BC-5 | `tests/test_agents_service.py`, portable tests | Rendered rule/router markers contain `SSPEC_SCHEMA::7.0` |
| BC-6 | README/spec-doc review | User docs distinguish project context, router, and managed rule |

## 11. Migration and Rollback

Migration path:

```text
old initialized project with sspec_schema 6.2
  → sspec project update
  → root AGENTS managed block becomes router
  → .sspec/SSPEC.rule.md is created
  → .meta.json gains file_hashes["SSPEC.rule.md"]
  → .meta.json.sspec_schema becomes 7.0
```

Rollback path for a user:

```text
restore previous root AGENTS.md block from VCS
remove .sspec/SSPEC.rule.md if undesired
restore .sspec/.meta.json from VCS or rerun sspec project update with the previous sspec version
```

No destructive migration is required. Existing `.sspec/project.md`, changes, requests, spec-docs, and skills remain in place.

If a future sspec version requires non-template project-state transforms, introduce a dedicated `sspec_schema` migration chain then. This change intentionally avoids that framework because 7.0 is representable by managed template creation/update plus metadata marker persistence.
