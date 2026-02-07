# Project Context

**Name**: sspec
**Description**: Spec-driven CLI framework for AI-assisted development (vibe coding)
**Repo**: (local)

## Tech Stack
- Python 3.11+
- uv (package management)
- Click (CLI framework)
- Rich (terminal output)
- Questionary (interactive prompts)
- PyYAML (frontmatter parsing)

## Key Paths

| Path | Purpose |
|------|---------|
| `src/sspec/cli.py` | CLI entry point |
| `src/sspec/core.py` | Types, constants, shared utilities |
| `src/sspec/commands/` | CLI command implementations |
| `src/sspec/services/` | Business logic (CLI-agnostic) |
| `src/sspec/libs/` | Pure utilities (hashing, etc.) |
| `src/sspec/templates/` | ⭐ Product templates (what users get) |
| `src/sspec/templates/skills/` | SKILL templates |
| `tmp/` | Testing sandbox (gitignored) |
| `.sspec/` | Self-hosting sspec data |

## Conventions
- ruff for lint + format, line length ≤ 90
- Type hints for all function signatures
- Docstrings for public functions
- commands/ = thin CLI layer; services/ = business logic; core.py = shared types
- Test all CLI changes in `tmp/` sandbox, never in project root
- `uv pip install -e .` after any code or template change
- `uv run sspec <cmd>` to invoke CLI

## Notes
<!-- @RULE: Project-level memory. Append-only log of learnings, gotchas, preferences.
Agent appends here during @handover when a discovery is project-wide (not change-specific).
Format each entry as: `- YYYY-MM-DD: <learning>`
Prune entries that become outdated or graduate to Conventions/spec-docs. -->
