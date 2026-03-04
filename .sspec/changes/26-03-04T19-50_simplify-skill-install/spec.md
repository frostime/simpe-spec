---
name: simplify-skill-install
status: REVIEW
type: refactor
change-type: single
created: 2026-03-04 19:50:23
reference:
- source: .sspec/requests/26-03-04T19-40_simplify-skill-install.md
  type: request
  note: Linked from request
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

# simplify-skill-install

## A. Problem Statement
Current SKILL install flow still carries legacy Windows symlink-elevation branches (non-elevated symlink -> elevated symlink -> junction -> copy) and persists `skill_install_strategies` in `.meta.json`, causing multi-path logic across installer/init/update/commands that is no longer needed after hub-spoke switched to directory-level links. This branch-heavy path increases regression risk and maintenance overhead for each SKILL install/update change.

### Current Situation
- Windows now works reliably with junction links for spoke directories, but code still keeps symbolic-link elevation flow.
- `.meta.json` keeps `skill_install_strategies`, but update behavior already relies on filesystem reality (link/copy detection), not this field.
- This leaves dead compatibility burden in both runtime logic and schema normalization/migration paths.

### User Requirement
- Simplify install strategy: Windows default to junction, Linux/macOS default to symlink, and both without sudo/admin elevation.
- Remove obsolete strategy persistence from `.meta.json` and migrate schema to `2.1` with explicit linear migration.
- Keep existing hub-spoke behavior and update safety semantics unchanged.

<!-- @RULE: Quantify impact. Format: "[metric] causing [impact]".
Simple: single paragraph. Complex: split "Current Situation" + "User Requirement". -->

## B. Proposed Solution
### Approach
Use filesystem-deterministic behavior and remove metadata-coupled strategy branching.

`SkillInstaller` becomes a two-branch installer: on Windows, create junction then fallback copy; on non-Windows, create symlink then fallback copy. No elevation prompt, no elevated symlink attempt, no per-location strategy persistence. Externally, strategy semantics are unified to `link|copy` for cross-platform consistency; internally, installer keeps symlink/junction detection for safe operations.

In parallel, `.meta.json` schema bumps from `2.0` to `2.1` and drops `skill_install_strategies` as a managed field. Migration stays explicit and linear (`<1.0 -> 1.0`, `<2.0 -> 2.0`, `<2.1 -> 2.1`) and removes this key during upgrade. This follows config-schema-design principles: explicit version marker, ordered one-step migrations, and no structural guessing.

### Key Design

**Refactor A: Installer strategy simplification + external strategy unification**
- Remove Windows symlink elevation path and related feature flags from install flow.
- Expose only `link|copy` to service/CLI outputs.
- Keep `check_path_link` / junction detection contract unchanged for update/migration correctness.

**Refactor B: Meta schema 2.1 + field removal**
- `META_SCHEMA` -> `2.1`.
- Add migration step `2.0 -> 2.1` that removes `skill_install_strategies`.
- Remove default injection/normalization of this field from `MetaModel` upgrade path.

**Refactor C: Service/command contract cleanup**
- `project init` and `sync_skill_locations` no longer pass elevation/junction preference toggles.
- `skill dominate` keeps recording `skill_locations`, but no longer writes strategy map into meta.

#### Interface Design
```python
# src/sspec/skill_installer.py
SkillStrategy = Literal["link", "copy"]
LinkKind = Literal["none", "symlink", "junction"]

def install_batch(
    self,
    items: list[tuple[Path, Path]],
    prefer_symlink: bool = True,
) -> list[SkillInstallResult]:
    ...


# src/sspec/services/project_init_service.py
def sync_skill_locations(
    *,
    project_root: Path,
    locations: list[str],
    prefer_symlink: bool = True,
    sspec_dir: str = SSPEC_DIR,
) -> SkillSyncResult:
    ...


# src/sspec/services/meta_service.py
META_SCHEMA = "2.1"

def _migrate_to_2_1(data: dict[str, Any]) -> dict[str, Any]:
    """2.0 -> 2.1: remove deprecated skill_install_strategies key."""
    ...

def normalize_legacy_strategy(raw: str | None) -> SkillStrategy:
    """Map symlink/junction/link/copy into public link/copy strategy."""
    ...
```

#### Data Flow
```
project init / sync_skill_locations
  │
  ├── prepare hub-spoke targets
  ├── SkillInstaller.install_batch(items, prefer_symlink=True)
  │    ├── win32: try junction -> public strategy 'link' | fallback 'copy'
  │    └── others: try symlink -> public strategy 'link' | fallback 'copy'
  ├── collect runtime strategies (public link/copy only)
  └── persist meta without skill_install_strategies

project update
  │
  ├── load_meta_latest()
  ├── upgrade_meta()
  │    ├── <1.0 -> 1.0
  │    ├── <2.0 -> 2.0
  │    └── <2.1 -> 2.1 (drop deprecated key)
  └── continue update pipeline using file_hashes + filesystem link detection
```

`project update` does not change status semantics; it keeps using actual filesystem checks (`check_path_link`) and hash comparison, so removing strategy metadata does not reduce safety.

#### Key Logic
- Link creation policy is platform-fixed (Windows junction, others symlink) instead of prompt/flag-driven.
- Copy remains the only fallback path for failed link creation.
- Public strategy model is normalized to `link|copy`; legacy `symlink|junction` values are read as compatibility input and mapped to `link`.
- Meta migration is version-driven only (declared schema marker), never inferred by field shape.
- Legacy meta files containing `skill_install_strategies` are accepted as input, then normalized out in upgraded output.
- Keep link-kind granularity (`symlink` vs `junction`) in installer internals for safe unlink/relink behavior; only external contract is flattened.

#### Risk Check
- **Dependency audit**: runtime logic does not read `meta.skill_install_strategies` to decide behavior; it is only written/normalized today.
- **Update safety**: `project update` already uses filesystem checks (`check_path_link`) + hashes; removing metadata strategy map does not alter candidate classification.
- **Dominate flow**: `skill dominate` link correctness depends on `check_path_link`/`detect_path_link`, not meta strategy map.
- **Compatibility risk**: only external tooling (if any) that reads `skill_install_strategies` from `.meta.json` may be affected; mitigate via schema bump + migration + spec-doc update.

#### Scope Summary
| File | Change |
|------|--------|
| `src/sspec/skill_installer.py` | Remove elevation flow and simplify install strategy branches |
| `src/sspec/services/project_init_service.py` | Drop elevation/junction flags from sync API and stop writing strategy map |
| `src/sspec/commands/project.py` | Remove Windows elevation/junction option wiring in init flow |
| `src/sspec/commands/skill.py` | Stop persisting dominate strategy to `.meta.json` |
| `src/sspec/services/meta_service.py` | Bump schema to `2.1`, add `2.1` migration, remove strategy field model/defaults |
| `src/sspec/services/project_update_service.py` | Remove strategy-map writes during legacy migration |
| `tests/test_meta_service.py` | Update migration assertions for schema `2.1` and key removal |
| `tests/test_project_init_service.py` | Assert meta no longer includes strategy field |
| `tests/test_skill_command_error_handling.py` | Remove strategy persistence expectation from dominate command |
| `tests/test_skill_installer.py` | Update installer tests to platform-fixed strategy behavior |
