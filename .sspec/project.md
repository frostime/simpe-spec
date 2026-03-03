# Project Context

<!-- This file is the stable identity layer for agents working on this project.
Read it first every session. Update Conventions + Notes via @handover. -->

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
| `src/sspec/commands/` | CLI command implementations (thin CLI layer) |
| `src/sspec/services/` | Business logic (CLI-agnostic) |
| `src/sspec/libs/` | Pure utilities (hashing, etc.) |
| `src/sspec/templates/` | Product templates (what users get on `sspec init`) |
| `src/sspec/templates/skills/` | SKILL templates (distributed to users) |
| `.github/skills/` | Dev-time skills (used when developing sspec itself) |
| `tmp/` | Testing sandbox (gitignored) |
| `.sspec/` | Self-hosting sspec data |

## Conventions
- ruff for lint + format, line length <= 90
- Type hints for all function signatures
- Docstrings for public functions
- commands/ = thin CLI layer; services/ = business logic; core.py = shared types
- Test all CLI changes in `tmp/` sandbox, never in project root
- `uv pip install -e .` after any code or template change
- `uv run sspec <cmd>` to invoke CLI
- Template source files in `src/sspec/templates/` are ground truth — not `.sspec/` copies

## Spec-Docs Index

- [Builtin Tools System](spec-docs/builtin-tools.md) — `sspec tool` subcommands, built-in tool registration and execution
- [Project Specifications](spec-docs/README.md) — overview index for all spec-docs
- [SKILL Installation & Sync](spec-docs/skill-installation.md) — hub-spoke skill install model, symlink strategy
- [meta.json (Project Metadata)](spec-docs/meta-json.md) — `.sspec/.meta.json` schema + migration + update-time guarantees
- [Testing Standards](spec-docs/testing-standards.md) — test patterns, fixtures, coverage conventions

## Notes
<!-- @RULE: Project-level memory. Append-only log of learnings, gotchas, preferences, and vital change.
Agent appends here during @handover when a discovery is project-wide (not change-specific).
Format each entry as: `- YYYY-MM-DD: <learning>`
Prune entries that become outdated or graduate to Conventions/spec-docs. -->
- 2026-02-13: SKILL hub-spoke (`.sspec/skills` as hub, external as spoke), avoids state forking from per-skill links.
- 2026-02-13: Windows link strategy: `symlink -> elevated symlink -> junction -> copy`; supports "user rejects elevation -> direct junction".
- 2026-02-13: Legacy migration backup must not recreate symlinks (avoids WinError 1314); skip hub-pointing link nodes.
- 2026-02-24: 完全重构 SSPEC 的 SKILL 体系，将旧版本的 sspec-change 拆分，并构建了新的 research/design/plan/implement/review/handover/ask 模块化流程，见已经归档的 change `.sspec\changes\archive\26-02-24T21-47_refactor-to-perf-workflow\spec.md`。
