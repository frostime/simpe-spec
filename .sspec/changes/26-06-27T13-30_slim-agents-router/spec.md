---
name: slim-agents-router
status: REVIEW
change-type: single
created: 2026-06-27T13:30:14
reference: null
---

# slim-agents-router

## Problem Statement

Root `AGENTS.md` currently contains the full sspec protocol at about 5.5K chars, causing every agent session in an initialized project to load the complete change workflow even when the task only needs project context or a micro edit. The largest low-frequency content is the change lifecycle/workflow section, while `.sspec/project.md` and its Spec-Docs Index remain high-value default context.

## Proposed Solution

### Approach

Split the installed-project guidance into a small root `AGENTS.md` router and a managed `.sspec/SSPEC.rule.md` full protocol file. The root router remains auto-installed and auto-updated through the existing `SSPEC:START/END` block, but it only tells agents to read `.sspec/project.md`, when to read spec-docs, when to load `.sspec/SSPEC.rule.md`, and how to load matching SKILL files.

`.sspec/SSPEC.rule.md` becomes the managed home for the current full sspec protocol. It is installed and updated like other managed template files: local edits are detected and skipped by default, and `--force` is required to overwrite. `.sspec/project.md` remains user-managed and continues to be the first project-specific context entry.

Portable mode is not redesigned in this change. To avoid regression, `sspec portable read rule:sspec` will keep the same CLI contract but read the new full-rule template source instead of the root `AGENTS.md` router.

This is a protocol layout change, so `SCHEMA_VERSION` / `.meta.json.sspec_schema` moves from `6.2` to `7.0`. The `.meta.json` file structure does not change, so `meta_schema` stays unchanged.

### Behavior Contract

**BC-1: Root AGENTS router**
- Surface: generated root `AGENTS.md` managed `SSPEC:START/END` block.
- Before: the managed block embeds full sspec structure, dispatch, lifecycle, scale, align/argue, CLI, HOWTO, and spec-doc rules.
- After: the managed block is a short router that:
  - tells agents to read `.sspec/project.md` before project-specific work when present;
  - tells agents to use `.sspec/project.md` Spec-Docs Index and read spec-docs only when relevant;
  - lists conditions that require reading `.sspec/SSPEC.rule.md`;
  - tells agents to load matching `.sspec/skills/<name>/SKILL.md` after the rule requires a phase/task skill;
  - keeps low-cost global guidance such as fence nesting if needed.
- Boundary: root `AGENTS.md` block markers and block-outside preservation behavior stay unchanged.

**BC-2: Managed full rule file**
- Surface: `.sspec/SSPEC.rule.md` in initialized sspec projects.
- Before: the full sspec protocol exists only as the root `AGENTS.md` template body.
- After: `sspec project init` creates `.sspec/SSPEC.rule.md` from `src/sspec/templates/SSPEC.rule.md`; `sspec project update` tracks it through `file_hashes` and reports it in the normal Update Status table.
- Compatibility: local modifications to `.sspec/SSPEC.rule.md` are skipped by default as `modified` or `unknown`; `--force` is required to overwrite. `.sspec/project.md` remains user-managed and is not auto-updated.

**BC-3: Existing project migration**
- Surface: `sspec project update` on projects initialized before this change.
- After: update can create missing `.sspec/SSPEC.rule.md` and replace only the root `AGENTS.md` managed block with the router, while preserving root `AGENTS.md` content outside `SSPEC:START/END`.
- Boundary: skill hub-spoke sync, orphan skill handling, `.meta.json` migration, and `project.md` behavior remain unchanged except for the new rule hash entry.

**BC-4: Portable compatibility shim**
- Surface: `sspec portable read rule:sspec`.
- Before: reads `src/sspec/templates/AGENTS.md`.
- After: reads `src/sspec/templates/SSPEC.rule.md` so portable users still receive the full sspec rule, not the router.
- Boundary: no new portable CLI commands, options, or bootstrap redesign.

**BC-5: Protocol schema marker**
- Surface: `src/sspec/core.py::SCHEMA_VERSION`, generated `SSPEC_SCHEMA::...` markers, and `.sspec/.meta.json.sspec_schema`.
- Before: protocol schema is `6.2`.
- After: protocol schema is `7.0` for new projects and for existing projects after `sspec project update` persists the protocol update.
- Boundary: `.meta.json.meta_schema` remains unchanged because the metadata file shape is unchanged.

**BC-6: Documentation and internal references**
- Surface: README, spec-docs, and built-in SKILL text that mention root `AGENTS.md` as the full protocol.
- After: references distinguish root `AGENTS.md` router, `.sspec/project.md` context, and `.sspec/SSPEC.rule.md` full workflow rule.

### Implementation Changes

**refactor(templates): Split AGENTS router from full rule** — Move current full protocol content to `src/sspec/templates/SSPEC.rule.md`; replace `src/sspec/templates/AGENTS.md` with the root router content. Serves BC-1, BC-2.

**feat(update): Track managed SSPEC.rule.md** — Add `SSPEC.rule.md` to managed template update flow so init creates it, update detects missing/current/updatable/modified/unknown, and `.meta.json.file_hashes` stores its hash. Serves BC-2, BC-3.

**refactor(cli): Clarify project init/update wording** — Keep ordinary init output simple, but ensure structure/update status makes `SSPEC.rule.md` visible as a managed workflow rule when relevant. Serves BC-2, BC-3.

**fix(portable): Preserve rule:sspec full-rule output** — Change portable rule resolution to read the new full-rule template source while keeping the existing public command contract. Serves BC-4.

**chore(protocol): Bump sspec schema to 7.0** — Update `SCHEMA_VERSION` and ensure project update persists `sspec_schema` drift even when no other metadata migration is required. Serves BC-5.

**docs(protocol): Update docs for router/rule split** — Refresh README and spec-docs that currently describe root `AGENTS.md` as the full protocol. Serves BC-6.

**test(project): Cover router/rule lifecycle** — Add/update service and command tests for generated router content, rule creation/hash/update status, modified rule protection, schema marker persistence, and portable shim source. Serves BC-1 through BC-6.

### Scope Summary

| File | Change | Effort |
|---|---|---:|
| `src/sspec/templates/AGENTS.md` | Replace full protocol with root router | M |
| `src/sspec/templates/SSPEC.rule.md` | New managed full protocol template | S |
| `src/sspec/core.py` | Bump `SCHEMA_VERSION` to `7.0`; add `SSPEC.rule.md` to managed template file list and update comments | S |
| `src/sspec/services/project_init_service.py` | Ensure init hash/output behavior remains correct for managed rule | S |
| `src/sspec/commands/project.py` | Adjust user-facing wording/counting only where misleading | S |
| `src/sspec/services/portable_service.py` | Point `rule:sspec` to full-rule template source | XS |
| `src/sspec/templates/skills/sspec-design/SKILL.md` | Replace stale `AGENTS.md` scale reference | XS |
| `.sspec/spec-docs/agents-sync.md` | Document root router + managed rule sync model | M |
| `.sspec/spec-docs/meta-json.md` | Document `SSPEC.rule.md` hash tracking | S |
| `README.md` | Update folder layout and Quick Start wording | S |
| `tests/test_agents_service.py` | Assert router content/markers/preservation | S |
| `tests/test_project_init_service.py` | Assert rule file creation and hash metadata | S |
| `tests/test_project_update_service.py` | Assert rule update candidate states | M |
| `tests/test_portable_service.py`, `tests/test_portable_command.py` | Assert portable `rule:sspec` reads full rule source | S |
| `tests/test_project_command.py` | Assert 6.2 project update persists `sspec_schema == 7.0` | S |

What stays unchanged:
- No `rules/` directory is introduced.
- `.sspec/project.md` remains user-managed and top-level project context.
- `sspec portable` bootstrap behavior is not redesigned.
- Skill installation/sync semantics stay unchanged.
- `.meta.json.meta_schema` stays unchanged; only `.meta.json.sspec_schema` moves to `7.0`.

### Design Reference

See [design.md](./design.md).
