---
name: meta.json (Project Metadata)
description: Define `.sspec/.meta.json` schema, migration strategy, and update-time guarantees
updated: 2026-03-03
scope:
  - /.sspec/.meta.json
  - /src/sspec/services/meta_service.py
  - /src/sspec/services/project_init_service.py
  - /src/sspec/services/project_update_service.py
  - /src/sspec/commands/project.py
  - /tests/test_meta_service.py
  - /tests/test_project_update_service.py
  - /tests/test_project_command.py
deprecated: false
replacement: ""
---

# meta.json (Project Metadata)

## Overview

`.sspec/.meta.json` is the persistent metadata file for a sspec project.

Primary responsibilities:
- Track which template + skill files are managed and their hashes (`file_hashes`).
- Record installed template skill set (`managed_skills`) and spoke locations (`skill_locations`).
- Provide a stable, versioned schema with explicit migrations.

This file is part of project state (not a cache). `sspec project update` relies on it to decide whether an installed file is:
- `current` (matches template)
- `updatable` (matches previous known hash)
- `modified` (user changed)
- `unknown` (cannot safely infer)

## File Location

- Path: `.sspec/.meta.json`

The file is created by:
- `sspec project init` (writes initial meta).

The file is upgraded and maintained by:
- `sspec project update` (migration + refresh).

## Schema Axes

`.meta.json` uses two different schema markers:

1) `meta_schema` (meta file schema)
- Meaning: the schema version of `.meta.json` itself.
- Owned by: `src/sspec/services/meta_service.py`.
- Current: `2.0` (`META_SCHEMA`).

2) `sspec_schema` (sspec protocol schema)
- Meaning: the sspec protocol schema used by templates (not the meta file schema).
- Owned by: `src/sspec/core.py` (`SCHEMA_VERSION`).
- Written by: `project init` and refreshed by `project update`.

Design rule: these two versions are independent and must not be conflated.

## Current On-Disk Model (meta_schema = 2.0)

Canonical keys in v2.0:

| Key | Type | Meaning |
|-----|------|---------|
| `meta_schema` | string | meta file schema version, current `2.0` |
| `sspec_schema` | string | sspec protocol schema version (e.g. `9.1`) |
| `sspec_version` | string | sspec package version used to write meta |
| `created_at` | string | ISO datetime string |
| `updated_at` | string | ISO datetime string |
| `file_hashes` | object | map of tracked paths -> hash |
| `managed_skills` | array | template skill names that are managed |
| `skill_locations` | array | directories where `skills/` are installed/synced |
| `skill_install_strategies` | object | map of location -> `symlink/junction/copy` |

Typed model (source of truth): `MetaModel` in `src/sspec/services/meta_service.py`.

Extensibility:
- Unknown keys are allowed.
- Migrations preserve unknown keys.

## Backward Compatibility

Legacy keys (pre-v2.0):
- `meta_schema_version` (old meta schema marker)
- `schema_version` (historically used to store sspec protocol schema)

These are supported ONLY as migration inputs.

## Migration Strategy

Migration is schema-driven and declared-schema-based:

- The declared schema is read from:
  - `meta_schema` (preferred), or
  - `meta_schema_version` (legacy)

- Missing schema is treated as `0.0`.

- Upgrade path is linear:
  - `< 1.0` -> migrate to `1.0`
  - `< 2.0` -> migrate to `2.0`

### 1.0 -> 2.0 Migration (Key Renames)

- `schema_version` -> `sspec_schema`
- `meta_schema_version` -> `meta_schema` (and set to `2.0`)
- Drop old keys after migration.

Implementation: `upgrade_meta()` in `src/sspec/services/meta_service.py`.

### Future Schema Handling

If `.meta.json` declares a `meta_schema` newer than the current implementation supports:
- `upgrade_meta()` raises `ValueError`.
- `project update` converts this into a CLI-friendly `ClickException`.

This policy prevents silent data loss.

## Update-Time Guarantees

`sspec project update` treats meta migration as a mandatory stage.

Pipeline stage:
- `prepare_meta_for_project_update(sspec_root)` in `src/sspec/services/project_update_service.py`
  - loads meta via `load_meta_latest()` (migration-aware)
  - returns:
    - `meta` (migrated dict)
    - `old_hashes` snapshot
    - `migration_needed` boolean

Persistence rules:
- If `migration_needed` is true, then on non-dry-run `project update` will write back migrated meta even if no other file updates occur.
- `project update` also refreshes `sspec_schema` and `meta_schema` on every meta write.

These guarantees are tested by:
- `tests/test_project_command.py`
- `tests/test_project_update_service.py`

## Examples

### Example: Legacy meta (pre-v2)

```json
{
  "meta_schema_version": "1",
  "schema_version": "6.0",
  "file_hashes": {},
  "managed_skills": []
}
```

### After upgrade (v2.0)

```json
{
  "meta_schema": "2.0",
  "sspec_schema": "6.0",
  "file_hashes": {},
  "managed_skills": []
}
```

## Notes / Known Risks

- Path normalization: `skill_locations` should be stored as workspace-relative POSIX paths (use `/`).
  Windows-style `\\` separators can harm portability if the same project is used on non-Windows platforms.
  Current code will generally work on Windows either way, but cross-platform usage should standardize.
