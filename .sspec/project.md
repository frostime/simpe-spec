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
- 2026-02-13: SKILL 安装体系已收敛为 hub-spoke（`.sspec/skills` 为 hub，外部为目录级 spoke），避免逐 skill 链接造成的状态分叉。
- 2026-02-13: Windows 链路策略固定为 `symlink -> elevated symlink -> junction -> copy`，且支持“用户拒绝提权时直接 junction”。
- 2026-02-13: Legacy 迁移备份禁止重建 symlink（避免 WinError 1314），只备份真实目录并跳过指向 hub 的链接节点。
- 2026-02-13: Skill update 候选已引入 `modified` 保护语义（默认不覆盖用户改动，需 `--force`）。
