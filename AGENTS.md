# sspec Development Protocol

## 0. Self-Hosting Notice

This project uses sspec to develop sspec. Two sets of rules coexist:

| | This file (above SSPEC block) | SSPEC block (below) |
|---|---|---|
| Purpose | How to **develop** sspec | How to **use** sspec |
| Audience | Agent working on this repo | Agent using sspec in any project |
| Authority | **This file wins** on conflicts | Provides workflow structure |

**Rule**: When developing templates, the **template source files** in `src/sspec/templates/` are ground truth.

**Hard rule**:
- Edit of sspec itself SHOULD lies within `src/`, `tests/`
- MUST NOT hand-edit `.github/`, `.claude/`, or `.sspec/` copies, refresh them with `uv run sspec project update`.

**Auto-managed rule**: The SSPEC block below `SSPEC:START` is generated from `src/sspec/templates/AGENTS.md`. If that block needs to change, update the template source and run `uv run sspec project update` instead of editing the block directly.

---

## 1. Source

`src/sspec/`:

```
src/sspec/
├── cli.py              # Entry point
├── core.py             # Shared types, constants, utilities
├── commands/           # CLI commands (project/change/ask/request/doc/tool/...)
├── services/           # Business logic (CLI-agnostic)
├── libs/               # Pure utilities (hashing, etc.)
└── templates/          # Product: what users get on `sspec init`
    ├── AGENTS.md       # ⭐ The protocol template
    ├── project.md      # Project context template
    ├── change/         # spec.md, tasks.md, handover.md
    ├── change-root/    # Root change variants
    ├── requests/       # Request template
    └── skills/         # User-facing SKILL templates
```

---

## 2. Template Change Protocol

Changing templates = changing the product. Extra care required.

### What counts as a template change
- Any file under `src/sspec/templates/`
- SKILL files under `src/sspec/templates/skills/`

### Workflow

1. Edit template source in `src/sspec/templates/`
2. Reinstall: `uv pip install -e .`  ← **必须，否则模板缓存不更新**
3. Sync self-hosted copies: `uv run sspec project update`
4. Test in sandbox:

```powershell
# Create clean test environment
cd tmp
mkdir test_<feature>
cd test_<feature>

# Test init
uv run sspec project init
# Verify: check generated files match expectations

# Test update (if applicable)
uv run sspec project update --dry-run
```

5. If template structure changed → check `UPDATABLE_FILES`, `USER_FILES` in `core.py`
6. If a skill was added/renamed/removed → verify both init/install flow in `project_init_service.py` and update/orphan flow in `project_update_service.py`

### Template editing rules

Templates use `{{VARIABLE}}` placeholders. Current variables:
- `{{SCHEMA_VERSION}}` — from `core.py:SCHEMA_VERSION`
- `{{TODO}}` — user fills after init
- `{{NAME}}`, `{{TIME}}`, `{{CHANGE_NAME}}` — CLI fills at creation

**Never** put development-specific content in templates. Templates are for users.

**Never** patch installed/generated copies under `.github/`, `.claude/`, or `.sspec/` by hand. Re-sync from template source.

---

## 3. Code Change Protocol

### After editing Python files

```powershell
uv pip install -e .          # Reinstall editable
uv run ruff check src/       # Lint
uv run ruff format src/      # Format
```

Then run focused verification for the behavior you changed (for example a targeted `uv run pytest ...` module and/or a `tmp/` CLI sandbox check).

### CLI testing pattern

```powershell
# Always test in tmp/ — never pollute project root
cd tmp/test_<feature>
uv run sspec <command>       # Test the command
```

### Windows terminal encoding rule

- Treat Windows GBK/cp936 terminals as a supported environment.
- Any CLI output path must not crash on non-UTF encodings.
- Keep `configure_stdio_error_fallback()` wired in CLI startup when refactoring entrypoints.
- For new symbols/emojis in user-facing text, verify behavior in legacy encodings or provide ASCII fallback.

---

<!-- ====================================================================
     Below: SSPEC protocol block, auto-managed by `sspec project update`.
     Provides the standard workflow (changes, requests, handover, etc.).
     When in doubt: Section 0 of this file defines precedence.
     ==================================================================== -->



<!-- SSPEC:START -->
# sspec Router

SSPEC_SCHEMA::7.0

## Project Context

If `.sspec/project.md` exists, read it before project-specific work.
Use its Key Paths, Conventions, and Spec-Docs Index for orientation.
Read spec-docs only when the current task matches their index entry.

## Full Rule Trigger

Read `.sspec/SSPEC.rule.md` when:
- user mentions sspec, spec, change, request, spec-doc, align, or argue;
- task references `.sspec/requests/*`, `.sspec/changes/*`, or `.sspec/spec-docs/*`;
- user asks to create/update project context, request, change, spec-doc, memory, or workflow state;
- user asks to clarify/design/plan/implement/review using sspec;
- user intends a change of any scale (micro, single, or multi).

Pure code edits with no sspec workflow intent may be done directly.

## Skills

After reading `.sspec/SSPEC.rule.md`, load matching `.sspec/skills/<name>/SKILL.md` before that phase/task.
If a SKILL references relative files, read them relative to that SKILL directory.

## Output Safety

When showing content that contains ` ``` `, outer fence MUST use more backticks (e.g. `````). Always outer > inner.
<!-- SSPEC:END -->
