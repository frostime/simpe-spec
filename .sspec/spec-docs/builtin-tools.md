---
name: builtin-tools
description: "Extensible CLI tool system for cross-project development utilities via sspec tool command"
updated: 2026-02-12
scope:
  - /src/sspec/commands/tool.py
  - /src/sspec/builtin_tools/**
deprecated: false
replacement: ""
---

# Builtin Tools System

Cross-project development utilities accessible via `sspec tool <name>` CLI command.

## Overview

**Purpose**: Provide standardized CLI access to builtin development utilities.

**Design Philosophy**:
- Minimal Interface 1.0 — simple now, extensible later
- Manual registration (current) → auto-discovery (future, 3-line switch)
- Tools are self-contained modules (metadata + CLI + logic)

**Distinct from `sspec cmd`**:
- `cmd` — Data-driven, project-specific commands (YAML registry)
- `tool` — Code-driven, builtin cross-project utilities (hardcoded registration)

## Tool Interface Specification

Every tool module in `/src/sspec/builtin_tools/` must provide:

### Required Exports

```python
# Module: src/sspec/builtin_tools/example_tool.py

# 1. Metadata
TOOL_NAME = "example"
TOOL_DESCRIPTION = "Brief description shown in help"
TOOL_PROMPT = """Detailed specification for LLM consumption.
Include format, usage patterns, examples."""

# 2. Registration function
def register_command(group: click.Group) -> None:
    """Register this tool as a Click subcommand."""
    import click
    from rich.console import Console

    console = Console()

    @group.command(name=TOOL_NAME, help=TOOL_DESCRIPTION)
    @click.argument('input_file', type=click.Path(exists=True, path_type=Path))
    @click.option('--dry-run', is_flag=True, help='Preview without applying')
    @click.option('--prompt', is_flag=True, help='Show specification')
    def example_command(input_file, dry_run, prompt):
        if prompt:
            console.print(TOOL_PROMPT)
            return

        # Tool logic here
        ...
```

### Interface Rationale

**Why these 4 components?**
- `TOOL_NAME` — CLI subcommand name
- `TOOL_DESCRIPTION` — Shows in help, must be concise (<80 chars)
- `TOOL_PROMPT` — Full specification for LLM copy-paste (can be long)
- `register_command()` — Keeps tool self-contained, no separate CLI code

**Why `--prompt` option?**
- Keeps `--help` concise (TOOL_PROMPT can be 100+ lines)
- Enables LLM to access specification: `sspec tool <name> --prompt`
- User can copy spec to external LLM session

## Registration (Current: Manual)

Location: `/src/sspec/commands/tool.py`

```python
"""sspec tool command - builtin development tools."""
import click
from sspec.builtin_tools import apply_patch  # Import tool module

@click.group()
def tool() -> None:
    """Builtin development tools."""
    pass

# Manual registration - explicit and clear
apply_patch.register_command(tool)
```

**Adding a new tool**:
1. Create module in `src/sspec/builtin_tools/new_tool.py`
2. Implement TOOL_NAME, TOOL_DESCRIPTION, TOOL_PROMPT, register_command()
3. Import in `commands/tool.py`
4. Call `new_tool.register_command(tool)`
5. Run `uv pip install -e .`

**Rationale**: Manual = explicit, no magic. Future agents see clear pattern.

## Registration (Future: Auto-Discovery)

When >5 tools exist, switch to auto-discovery (3-line change):

```python
# commands/tool.py
from pathlib import Path
import importlib

@click.group()
def tool() -> None:
    """Builtin development tools."""
    pass

# Auto-discover all tools
tools_dir = Path(__file__).parent.parent / 'builtin_tools'
for module_file in tools_dir.glob('*.py'):
    if module_file.stem.startswith('_'):
        continue
    module = importlib.import_module(f'sspec.builtin_tools.{module_file.stem}')
    if hasattr(module, 'register_command'):
        module.register_command(tool)
```

**Upgrade Path**: Minimal Interface 1.0 supports both patterns.

## Built-in Tools

### `patch` — Apply SEARCH/REPLACE Patches

**Module**: `/src/sspec/builtin_tools/apply_patch.py`

**Usage**: `sspec tool patch [PATCH_FILE] [--file PATH] [--input] [--dry-run] [--yes] [--output-failed DIR] [--prompt]`

**Input rules**:
- Provide exactly one input source:
    - `PATCH_FILE` (positional) OR `--file/-f PATH` OR `--input/-i`
- If no file is provided, defaults to interactive input (`--input`)
- Interactive input is skipped if the submitted text is empty

**Features**:
- Parses SEARCH/REPLACE format patches
- Rich interactive preview (table + confirmation)
- Failed patches auto-saved to `.sspec/tmp/failed-patches/<timestamp>/`
- Line-range support for ambiguity reduction

**Workflow**: Agent generates patch file → User runs `sspec tool patch` → Review results

**See**: `.github/skills/write-patch/SKILL.md` for Agent guidance

## Common Patterns

### Import Management

Import heavy dependencies (rich, click) **inside** register_command():

```python
def register_command(group):
    import click  # Import here, not top-level
    from rich.console import Console

    @group.command(...)
    def cmd(...):
        ...
```

**Why**: Avoids import cycles, keeps module lightweight until registration.

### Path Resolution

When tool needs project root:

```python
from sspec.core import find_sspec_root

sspec_root = find_sspec_root()
if sspec_root:
    project_root = sspec_root.parent  # find_sspec_root() returns .sspec dir
else:
    project_root = Path.cwd()
```

**Gotcha**: `find_sspec_root()` returns `.sspec/` path, not project root.

### Rich Output

Use Rich for enhanced UX:
- `Table` — Preview and results
- `console.print()` — Colored messages
- `click.confirm()` — Interactive prompts

Windows encoding: Set `PYTHONIOENCODING=utf-8` if Unicode chars fail.

## Testing

Test tools in `tmp/test_<tool>/`:

```powershell
cd tmp/test_patch
uv run sspec tool patch test.patch --dry-run
```

Never test in project root to avoid polluting workspace.

## Key Decisions

**Manual registration over auto-discovery (now)**:
- **Trade-off**: Explicit code vs automatic discovery
- **Decision**: Manual for now (only 1 tool)
- **Rationale**: YAGNI principle, simplicity, clear pattern for agents
- **Future**: Auto-discovery when >5 tools (minimal change required)

**Tool interface over Click decorators**:
- **Trade-off**: Self-contained modules vs thin commands/tool.py
- **Decision**: register_command() in tool module
- **Rationale**: Tools are portable, testable independently, no scattered code

**--prompt flag over embedding in help**:
- **Trade-off**: Convenience vs help output length
- **Decision**: Separate flag
- **Rationale**: TOOL_PROMPT can be 100+ lines, --help stays concise

## Extensibility

Future possibilities (not implemented):
- `sspec tool list` — Display all registered tools
- Tool validation — Check TOOL_* attributes exist
- Third-party plugin directory (`~/.sspec-tools/`)
- Tool-specific config in `.sspec/tools.yaml`

Current design supports these without breaking changes.

## References

- **SKILL**: `.github/skills/write-patch/SKILL.md` — Guides Agents to use patch workflow
- **Change**: `.sspec/changes/26-02-12T01-19_tools/` — Implementation record
- **Discussion**: `.sspec/asks/260212013642_tool_interface_spec.md` — Interface design rationale
