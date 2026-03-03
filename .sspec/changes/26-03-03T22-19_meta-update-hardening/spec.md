---
name: meta-update-hardening
status: PLANNING
type: fix
change-type: single
created: 2026-03-03T22:19:21
reference:
  - source: .sspec/changes/26-03-03T00-46_analyse-project-level
    type: prev-change
    note: Follow-up hardening after introducing meta schema v2 and migrations
  - source: .sspec/spec-docs/meta-json.md
    type: doc
    note: Project spec-doc for meta.json schema and guarantees
  - source: .sspec/changes/26-03-03T22-19_meta-update-hardening/reference/last-audit-report.md
    type: doc
    note: Audit report for c7d82f0..HEAD (src/sspec) diff and bug findings
---

<!-- @RULE: Frontmatter
status: PLANNING | DOING | REVIEW | DONE | BLOCKED
change-type: single | sub
reference?: Array<{source, type: 'request'|'root-change'|'sub-change'|'prev-change' |'doc', note?}>

Sub-change MUST link root:
reference:
  - source: ".sspec/changes/<root-change-dir>"
    type: "root-change"
    note: "Phase <n>: <phase-name>"

Single-change common reference:
reference:
  - source: ".sspec/requests/<request-file>.md"
    type: "request"
  - source: ".sspec/changes/<change-dir>"
    type: "prev-change"
    note: "This change is a follow-up to <change-name> which introduced <feature/bug>. This change addresses <issue> with that feature/bug."
-->

# meta-update-hardening

## A. Problem Statement

The previous iteration introduced `.sspec/.meta.json` schema v2 (`meta_schema=2.0`), key renames, and a mandatory migration stage during `sspec project update`.

After code review, several correctness and hardening issues remain. These issues can cause misleading CLI output, brittle behavior under malformed/future schemas, and cross-platform inconsistencies.

Current problems (src/sspec/):

Audit reference:
- See `.sspec/changes/26-03-03T22-19_meta-update-hardening/reference/last-audit-report.md` for the full, line-referenced review notes.

1) Schema parsing is too permissive
- If `meta_schema` is present but non-numeric (e.g. `2.0-beta`), it can be treated as `0.0` and migrated, which may rename/delete keys unexpectedly.
- Policy should be: missing schema -> treat as `0.0`; declared-but-unparseable schema -> fail loudly.

2) `project update` can report "All files are up to date" when candidates are `unknown`
- If `file_hashes` are missing/empty, template files may become `unknown`, yet no actions are taken by default.
- This leads to a false-positive "up to date" message and the project can remain stuck in `unknown` state.

3) Meta loading strictness is uneven across commands
- Some commands use `load_meta()` without converting schema errors into user-friendly CLI errors.
- A project with a future `.meta.json` schema can cause non-update commands to crash.

4) Path normalization and safety gaps
- `skill_locations` can be stored with Windows separators (`\\`) in init, and POSIX separators (`/`) in dominate, causing duplicates and mismatches.
- `sspec skill dominate <path>` resolves relative paths against CWD, not project root (easy to link the wrong directory).
- `sspec skill new <name>` does not validate name (can be used to escape `.sspec/skills` via `../`).
- `sspec project init --skill-loc <loc>` accepts free strings without validation (path traversal / absolute path risk).

5) A clear bug exists
- Duplicate/unreachable `return` in `create_skill_in_hub()`.

<!-- @RULE: Quantify impact. Format: "[metric] causing [impact]".
Simple: single paragraph. Complex: split "Current Situation" + "User Requirement". -->

## B. Proposed Solution

Harden the meta migration and project update pipeline to be:
- strict on declared schema (no accidental migrations on invalid schema strings),
- honest in output (never claim "up to date" while still blocked on `unknown`),
- resilient across commands (future schema handled consistently),
- consistent in path storage (POSIX paths in meta),
- safe for user input (validate skill names and location paths).

### Approach

1) Make schema parsing policy explicit
- Missing schema markers are treated as `0.0` (legacy).
- If schema marker exists but is unparsable (non-numeric), raise `ValueError`.
- Future numeric schemas (`> META_SCHEMA`) raise `ValueError`.

2) Strengthen `project update` behavior when meta is incomplete
- Do not print "All files are up to date" when there are any `unknown`/`modified` candidates that block safe updates.
- When `file_hashes` is missing/empty and candidates are verifiably `current`, rebuild `file_hashes` for those candidates so future updates become actionable.

3) Normalize and validate paths
- Always store `skill_locations` in POSIX form (forward slashes).
- Treat `skill dominate <relative>` as relative to project root, not current working directory.
- Validate `skill new <name>` and reject path-like names.
- Validate `--skill-loc` and custom input: must be relative, must not escape project root.

4) Fix the known bug
- Remove duplicate/unreachable `return` in `create_skill_in_hub()`.

### Key Design

#### Meta schema parsing contract

Rules:
- If `meta_schema` or legacy `meta_schema_version` is present and not parseable as dot-separated integers: raise.
- If no schema marker exists: treat as `0.0`.

#### project update: meta is mandatory and must be usable

Data flow (simplified):

```
sspec project update
  ├── stage 0: prepare_meta_for_project_update()
  │     ├── load + upgrade meta
  │     └── return (meta, old_hashes, migration_needed)
  ├── stage 1: migrations/orphans detection
  ├── stage 2: collect_update_candidates(...)
  ├── stage 3: decide actions
  └── stage 4: write meta
        ├── always persist schema migration (if needed)
        └── if hashes incomplete: backfill hashes for verifiably current items
```

#### Validation rules

Skill name validation (service-side):
- Must be a simple name (no slashes, no `..`, no path separators).
- Must not escape `.sspec/skills`.

Skill location validation (command/service boundary):
- Must be relative to project root.
- Must not resolve outside project root.

### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/services/meta_service.py` | Tighten schema parsing policy; ensure declared-but-invalid schema fails |
| `src/sspec/commands/project.py` | Avoid false "up to date" when unknown; backfill hashes when meta incomplete |
| `src/sspec/services/project_update_service.py` | Keep migration stage explicit; pass enough info to enforce invariants |
| `src/sspec/services/project_init_service.py` | Store `skill_locations` as POSIX; validate/normalize locations |
| `src/sspec/commands/skill.py` | Resolve dominate paths relative to project root; record location even if already linked |
| `src/sspec/services/skill_service.py` | Fix duplicate return; validate skill names |
| `tests/` | Add/adjust tests covering unknown/meta backfill, schema strictness, and path validation |
