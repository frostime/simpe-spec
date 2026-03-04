# Handover: simplify-skill-install

**Updated**: 2026-03-04 20:30

---

## Background
<!-- Write once on first session. What this change does and why (1-3 sentences).
Update only if scope fundamentally changes. Details belong in spec.md. -->

This change simplifies SKILL install strategy and removes deprecated strategy metadata. The existing Windows symlink-elevation flow and `.meta.json.skill_install_strategies` were legacy complexity no longer needed after directory-level hub-spoke links became stable.

## This Session

### Accomplished
<!-- Specific list of what got done this session -->
- Read request, project context, related spec-docs (`skill-installation`, `meta-json`), and current `.meta.json`.
- Investigated implementation in installer/init/update/meta/skill command + related tests.
- Created linked change `26-03-04T19-50_simplify-skill-install`.
- Completed design draft in `spec.md` (Problem + Proposed Solution + key interfaces/data flow/scope).
- Per user follow-up, completed deeper risk audit for removing `skill_install_strategies` and for `SkillStrategy`/`LinkKind` modeling.
- Validated in sandbox (`tmp/test_skill_strategy_research`) that removing the field does not break `project update` or `skill dominate` execution.
- Implemented installer simplification in `src/sspec/skill_installer.py`: removed elevation flow, platform-fixed link creation, public `link|copy` strategy, legacy strategy normalization.
- Implemented `.meta.json` schema migration to `2.1` and removed strategy-field persistence across init/sync/update/dominate paths.
- Updated docs (`.sspec/spec-docs/meta-json.md`, `.sspec/spec-docs/skill-installation.md`) and related tests.
- Validation complete: `uv run ruff check src/` passed; targeted pytest suite passed (57 tests).

### Next Steps
<!-- 1-3 specific file-level actions for the next agent -->
- Request user review/acceptance for implemented changes.
- Run broader regression suite if user wants full confidence beyond targeted tests.
- If accepted, archive change and update project-level notes via handover flow.

## Working Memory
<!-- Agent's external memory. Survives context compression and session boundaries.
Update PROACTIVELY: important decision, key file found, non-obvious insight.
Test: "Would I struggle to reconstruct this after losing context?" → Write NOW. -->

### Key Files
<!-- Files critical to understanding/continuing this change.
- `path/file` — what it contains, why it matters -->
- `src/sspec/skill_installer.py` — current multi-stage symlink/elevation/junction/copy logic to simplify.
- `src/sspec/services/meta_service.py` — meta schema and migration chain; target schema bump to 2.1.
- `src/sspec/services/project_init_service.py` — sync API and `.meta.json` writes including deprecated strategy map.
- `src/sspec/services/project_update_service.py` — legacy migration currently still writes strategy map.
- `src/sspec/commands/project.py` — init flow has obsolete Windows elevation/junction toggles.
- `src/sspec/commands/skill.py` — dominate command currently writes strategy map into meta.

### Decisions
<!-- Important decisions with reasoning.
- **Decision**: Redis over Memcached
  **Why**: Need per-key TTL + persistence -->
- **Decision**: Keep `check_path_link` contract and filesystem-based update safety; only remove deprecated strategy metadata.
  **Why**: Update pipeline already uses real link/copy state, so simplification can reduce complexity without changing correctness semantics.
- **Decision**: Use explicit linear meta migrations and drop `skill_install_strategies` in `2.1` migration step.
  **Why**: Align with declared-schema migration pattern and avoid structural inference.
- **Decision**: Externally unify strategy to `link|copy`, while keeping internal symlink/junction detection.
  **Why**: Preserves cross-platform contract stability for callers while retaining safe low-level unlink/relink behavior on Windows junction vs symlink nodes.

### Notes
<!-- Non-obvious findings, edge cases, gotchas, risks.
Project-wide items → ALSO append to project.md Notes. -->
- `project update` skill candidate logic already ignores `skill_install_strategies`; field is informational/dead state.
- Existing tests assert strategy persistence in meta; these assertions must be updated together with schema migration tests.
- Sandbox verification commands run successfully after field removal:
  - `uv run sspec project update --dry-run`
  - `uv run sspec skill dominate .claude`
  - `uv run sspec project update`
- `skill_install_strategies` is now treated as deprecated migration input only and removed on upgrade to schema `2.1`.
