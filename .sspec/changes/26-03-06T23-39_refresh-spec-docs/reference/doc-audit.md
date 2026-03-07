# Spec Doc Audit

## Scope

- `.sspec/project.md`
- `.sspec/spec-docs/`
- Runtime code paths used to verify current behavior

## Confirmed Drift

- `.sspec/project.md` still describes an older Windows link fallback order; current implementation uses junction-first behavior on Windows.
- `.sspec/spec-docs/skill-installation.md` still references `.agent/skills`, while the active workspace locations are `.agents`, `.claude`, and `.github`.
- `.sspec/spec-docs/testing-standards.md` still references removed `config.py` / `test_config.py` and older `.meta.json` field names.
- `.sspec/spec-docs/builtin-tools.md` still describes the system as if only one builtin tool exists, but the CLI now ships `patch`, `pack-zip`, `view-tree`, and `mdtoc`.
- `.sspec/spec-docs/README.md` index coverage is narrower than the current spec-doc set and the live CLI surface.

## Missing Long-Lived Contracts

- Change directory lifecycle: create, parse, archive, and cross-reference rewrite behavior.
- Request and ask record formats: frontmatter/schema, linking rules, archive behavior.
- Command registry storage: `.sspec/commands/registry.yaml` plus script `copy` / `move` / `ref` semantics.
- Root `AGENTS.md` managed block sync behavior.

## Proposed Documentation Scope

1. Fix factual drift in existing docs.
2. Add missing spec-docs for stable on-disk and workflow contracts.
3. Rebuild indexes and cross-links so the doc set is internally consistent.
