---
name: builtin-tools
description: "Extensible CLI tool system for cross-project development utilities via sspec tool command"
updated: 2026-03-07
scope:
  - /src/sspec/commands/tool.py
  - /src/sspec/builtin_tools/**
deprecated: false
replacement: ""
---

# Builtin Tools System

Cross-project development utilities accessible via `sspec tool <name>`.

## Overview

**Purpose**: Provide standardized CLI access to builtin development utilities.

**Design Philosophy**:
- Minimal Interface 1.0 — simple now, extensible later
- Manual registration (current) → auto-discovery (future, low-friction switch)
- Tools are self-contained modules (metadata + CLI + logic)

**Distinct from `sspec cmd`**:
- `cmd` — data-driven, project-specific commands stored in `.sspec/commands/registry.yaml`
- `tool` — code-driven, builtin cross-project utilities registered in Python

## Tool Interface Specification

Every tool module in `/src/sspec/builtin_tools/` must provide:

### Required Exports

```python
TOOL_NAME = "example"
TOOL_DESCRIPTION = "Brief description shown in help"
TOOL_PROMPT = """Detailed specification for LLM consumption."""


def register_command(group: click.Group) -> None:
    ...
```

### Interface Rationale

- `TOOL_NAME` — CLI subcommand name
- `TOOL_DESCRIPTION` — short help text
- `TOOL_PROMPT` — long-form prompt/spec for agent copy-paste or `--prompt`
- `register_command()` — keeps command wiring inside the tool module

## Registration (Current: Manual)

Location: `/src/sspec/commands/tool.py`

```python
from sspec.builtin_tools import apply_patch, mdtoc, pack_zip, view_tree


@click.group()
def tool() -> None:
    pass


apply_patch.register_command(tool)
pack_zip.register_command(tool)
view_tree.register_command(tool)
mdtoc.register_command(tool)
```

**Current tool set**: `patch`, `pack-zip`, `view-tree`, `fileinfo`, `write`, `mdtoc`, `now`, `ask`

**Adding a new tool**:
1. Create module in `src/sspec/builtin_tools/new_tool.py`
2. Implement `TOOL_NAME`, `TOOL_DESCRIPTION`, `TOOL_PROMPT`, `register_command()`
3. Import it in `commands/tool.py`
4. Call `new_tool.register_command(tool)`
5. Run `uv pip install -e .`

## Registration (Future: Auto-Discovery)

当 builtin tool 数量继续增长（当前 4 个）并且显式 import 变得笨重时，可切换到 auto-discovery。
当前文档保留这一扩展方向，但代码尚未启用。

## Built-in Tools

| Subcommand | Module | Purpose |
|------------|--------|---------|
| `patch` | `/src/sspec/builtin_tools/apply_patch.py` | Apply SEARCH/REPLACE patches with stdin/file input, retry-aware statuses, and markdown failed-bundle output |
| `pack-zip` | `/src/sspec/builtin_tools/pack_zip.py` | Package a project into zip while respecting `.gitignore` and extra include/exclude rules |
| `view-tree` | `/src/sspec/builtin_tools/view_tree.py` | Render a project tree with gitignore-aware filtering and optional file stats |
| `fileinfo` | `/src/sspec/builtin_tools/fileinfo.py` | Inspect file size, encoding, newline style, and text/binary status across files, directories, and globs |
| `write` | `/src/sspec/builtin_tools/write.py` | Write file content via pipe or text argument using explicit create/append/overwrite modes |
| `mdtoc` | `/src/sspec/builtin_tools/mdtoc.py` | Pre-scan Markdown size/headings before targeted reading |
| `now` | `/src/sspec/builtin_tools/now.py` | Provide stable local/UTC timestamps for agent-authored docs |
| `ask` | `/src/sspec/builtin_tools/ask.py` | Fallback user consultation workflow when no native question tool exists |

### `patch` — Apply SEARCH/REPLACE Patches

**Module**: `/src/sspec/builtin_tools/apply_patch.py`

**Notable behavior**:
- Exactly one input source: patch file, `--file`, `--stdin`, or `--input`
- Accepts relative targets rooted at the detected project root / cwd, plus absolute target paths
- Patch header paths may contain spaces, for example `# C:\My Project\docs\my file.md:L3-`
- Absolute target paths outside the current workspace require explicit confirmation, or `--unsafe` to bypass in automation
- Supports canonical and open-ended line ranges such as `L10-L25`, `L10-`, and `-L25`
- Repeated apply attempts can report `already_applied` instead of a generic `SEARCH` failure
- `--dry-run` still surfaces outside-workspace absolute path warnings even though no write occurs
- Rich preview before apply
- Failed patches are bundled into one markdown file; inside `.sspec/tmp/failed-patches/` for sspec projects or system temp otherwise
- Failure summaries print patch-source and target-file line numbers plus a truncated SEARCH/REPLACE preview
- `--prompt` prints the agent-facing patch spec instead of applying

### `pack-zip` — Package Project Snapshot

**Module**: `/src/sspec/builtin_tools/pack_zip.py`

**Notable behavior**:
- Walks the target tree and writes a zip archive
- Respects nested `.gitignore` files when `pathspec` is available
- Supports additional include/exclude patterns beyond default ignores
- Never mutates the source tree

### `view-tree` — Visualize Directory Structure

**Module**: `/src/sspec/builtin_tools/view_tree.py`

**Notable behavior**:
- Resolves a project root for gitignore filtering
- Hides universal noise dirs such as `.git`, `__pycache__`, and `node_modules`
- Can show file sizes or line/char detail for text files

### `fileinfo` — Inspect File Metadata

**Module**: `/src/sspec/builtin_tools/fileinfo.py`

**Notable behavior**:
- Works outside `.sspec/` projects and accepts absolute or relative paths
- Accepts multiple files, directories, and glob patterns in one command
- Reports size, modified time, text/binary classification, encoding guess, BOM, newline style, and line count when available
- Supports `--json` for agent-friendly structured output

### `write` — Explicit File Writing

**Module**: `/src/sspec/builtin_tools/write.py`

**Notable behavior**:
- Works outside `.sspec/` projects and accepts absolute or relative paths
- Requires explicit `--mode create|append|overwrite`
- Supports `--stdin` for multi-line piped content and `--text` for short inline writes
- Preserves existing newline style during append/overwrite when it can decode the target file

### `mdtoc` — Markdown TOC Pre-Scan

**Module**: `/src/sspec/builtin_tools/mdtoc.py`

**Notable behavior**:
- Accepts a file, directory, or glob pattern
- Reports char count, line count, and heading structure with `L<n>` line tags
- Skips fenced code blocks while parsing headings
- Serves as the standard pre-read tool for large Markdown docs in this repo

## Common Patterns

### Import Management

Import heavy dependencies inside `register_command()` when practical:

```python
def register_command(group):
    import click
    from rich.console import Console
```

这样可以减少顶层 import 负担，也让每个 tool 模块更自包含。

### Path Resolution

When a tool needs the project root:

```python
from sspec.core import find_sspec_root

sspec_root = find_sspec_root()
project_root = sspec_root.parent if sspec_root else Path.cwd()
```

### Rich Output

Use Rich for enhanced UX:
- `Table` — preview and result tables
- `console.print()` — status lines and warnings
- `Tree` — directory visualizations

## Testing

Test tools in `tmp/test_<tool>/` or via direct helper tests under `tests/`:

```powershell
mkdir tmp\test_mdtoc
uv run sspec tool mdtoc README.md
```

Never test destructive or archive-writing paths in project root.

## Key Decisions

**Manual registration over auto-discovery (now)**:
- **Trade-off**: explicit code vs automatic discovery
- **Decision**: manual for now (current set remains small enough for explicit registration)
- **Rationale**: the registry is still small enough that explicit imports in `commands/tool.py` are clearer than discovery magic
- **Future**: auto-discovery when tool count or plugin needs justify it

**Tool interface over thin `commands/tool.py` wrappers**:
- **Trade-off**: self-contained tool modules vs scattered CLI wiring
- **Decision**: `register_command()` lives in the tool module
- **Rationale**: portable, testable, and easier for agents to extend

**`--prompt` flag over long help output**:
- **Trade-off**: convenience vs manageable `--help`
- **Decision**: keep prompt text in `TOOL_PROMPT`
- **Rationale**: agent-oriented specs are often much longer than normal CLI help

## References

- `src/sspec/templates/skills/write-patch/SKILL.md` — product guidance for patch-based workflows
- `.sspec/changes/26-02-12T01-19_tools/` — original implementation record
- `.sspec/asks/260212013642_tool_interface_spec.md` — interface design rationale
