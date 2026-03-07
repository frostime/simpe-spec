# Project Context

<!-- This file is the stable identity layer for agents working on this project.
Read it first every session. Update Conventions + Notes via @handover. -->

**Name**: sspec
**Description**: Spec-driven CLI framework for AI-assisted development (vibe coding)
**Repo**: (local)

## Tech Stack
- Python 3.10+
- uv (package management + execution)
- Click (CLI framework)
- Rich (terminal output)
- Questionary + prompt_toolkit (interactive prompts)
- PyYAML (frontmatter parsing)
- python-dotenv (editor command resolution)
- pathspec (gitignore-aware packaging/filtering)

## Key Paths

| Path | Purpose |
|------|---------|
| `src/sspec/cli.py` | CLI entry point; keeps stdio fallback wired for Windows terminals |
| `src/sspec/core.py` | Shared constants, enums, path resolution, and template helpers |
| `src/sspec/commands/` | Thin CLI layer: Click wiring, prompts, output formatting |
| `src/sspec/services/` | Business logic and on-disk contract implementation |
| `src/sspec/builtin_tools/` | Code-driven builtin `sspec tool` subcommands |
| `src/sspec/skill_installer.py` | Hub-spoke skill install, link detection, and gitignore fences |
| `src/sspec/templates/` | Product templates; ground truth when generated content changes |
| `tests/` | Behavioral test suite for services, commands, and helpers |
| `.sspec/` | Self-hosted project state, docs, changes, asks, and requests |
| `tmp/` | Disposable sandbox for CLI/manual verification |

## Conventions
- Ruff handles lint + format; line length is `100`
- Keep type hints on public and non-trivial helper functions
- Keep docstrings on public functions; add comments only for non-obvious logic blocks
- `commands/` = CLI shell, `services/` = business logic, `builtin_tools/` = self-contained tool modules
- Test CLI workflows in `tmp/`, never in project root
- Use `tmp_path`-style filesystem tests for service contracts instead of mocking file I/O
- Run `uv pip install -e .` after Python or template changes
- Invoke the local CLI with `uv run sspec <cmd>`
- Keep `configure_stdio_error_fallback()` in CLI startup for Windows GBK/cp936 terminals
- When product templates change, edit `src/sspec/templates/` first and sync generated copies afterward

## Spec-Docs Index

- [Project Specifications](spec-docs/README.md) — master index and maintenance rules for this spec-doc set
- [Builtin Tools System](spec-docs/builtin-tools.md) — builtin `sspec tool` architecture, registration, and current tool inventory
- [SKILL Installation & Sync](spec-docs/skill-installation.md) — hub-spoke skill install model, link policy, migration, and gitignore rules
- [meta.json (Project Metadata)](spec-docs/meta-json.md) — `.sspec/.meta.json` schema, migration, and update-time guarantees
- [Testing Standards](spec-docs/testing-standards.md) — test layering, required behavior coverage, and anti-patterns
- [Change Lifecycle](spec-docs/change-lifecycle.md) — `.sspec/changes/` structure, status parsing, archive flow, and dashboard semantics
- [Interaction Records](spec-docs/interaction-records.md) — request/ask file schemas, linking, completion, and archive rewrites
- [Command Registry](spec-docs/cmd-registry.md) — `.sspec/commands/registry.yaml` contract and script strategies
- [Root AGENTS Sync](spec-docs/agents-sync.md) — managed `SSPEC:START/END` block behavior in root `AGENTS.md`

## Notes
<!-- @RULE: Project-level memory. Append-only log of learnings, gotchas, preferences, and vital change.
Agent appends here during @handover when a discovery is project-wide (not change-specific).
Format each entry as: `- YYYY-MM-DD: <learning>`
Prune entries that become outdated or graduate to Conventions/spec-docs. -->
- 2026-02-13: SKILL hub-spoke (`.sspec/skills` as hub, external as spoke), avoids state forking from per-skill links.
- 2026-02-13: Legacy migration backup must not recreate symlinks (avoids WinError 1314); skip hub-pointing link nodes.
- 2026-02-24: 完全重构 SSPEC 的 SKILL 体系，将旧版本的 sspec-change 拆分，并构建了新的 research/design/plan/implement/review/handover/align 模块化流程，见已经归档的 change `.sspec\changes\archive\26-02-24T21-47_refactor-to-perf-workflow\spec.md`。
- 2026-03-07: Windows skill sync currently prefers junction on `win32` and falls back to copy; 旧的 elevated symlink 流程说明已不再适用。
- 2026-03-07: 当前 builtin tool 集合为 `patch`、`pack-zip`、`view-tree`、`mdtoc`；修改它们时要同步更新 spec-doc。
- 2026-03-07: 新创建的 change handover 现在会记录创建前的 immutable Git Baseline，包含 repo/branch/HEAD 和原始 `git status --short --branch` 快照；Agent 无需改 SKILL/AGENTS 即可在 resume 时看到它。
