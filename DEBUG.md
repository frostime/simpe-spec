# sspec Debug Setup Guide

## Overview

This debug setup allows you to breakpoint-debug any sspec command directly in VS Code using the native Python debugger.

## Components

### 1. Debug Runner Script (`scripts/debug_runner.py`)
- Entry point for debugger
- Handles command-line arguments: `python scripts/debug_runner.py <sspec-command> [--cwd <dir>]`
- Manages working directory changes
- Delegates to `sspec.cli.main()`

### 2. VS Code Debug Configuration (`.vscode/launch.json`)
Two built-in debug configurations:
- **"Debug sspec command"**: Simple mode, debug in project root
- **"Debug sspec command (custom cwd)"**: Advanced mode, specify working directory

## Quick Start

### Method 1: Simple Command (Project Root)

1. Press **Ctrl+Shift+D** (or click Debug icon in sidebar)
2. Select **"Debug sspec command"** from dropdown
3. Click **F5** or press play button
4. Enter sspec command when prompted:
   - Simple: `project status`, `skill list`
   - With options: `change new`, `ask create test`, `project update --dry-run`
   - With flags: `change new --from test-a`, `ask create myask --force`
5. Set breakpoints in editor, debugger will stop when hit

**Input format**: Enter the complete command as you would in the shell (spaces between args, dash-prefixed flags), e.g.:
```
change new --from existing-request
ask prompt .sspec/asks/example.py
request list --archive
```

### Method 2: Custom Working Directory

Use when debugging commands in a sandbox (e.g., `tmp/test-project`):

1. Press **Ctrl+Shift+D**
2. Select **"Debug sspec command (custom cwd)"**
3. Click **F5** or press play button
4. Enter sspec command (e.g., `change new`)
5. Enter working directory (e.g., `${workspaceFolder}/tmp/test-project` or just `./tmp/test-project`)
6. Set breakpoints and debug normally

## Common Debug Scenarios

### Scenario A: Debug `sspec change new`

```
Command: change new
Working directory: ./tmp/test-project
```

Then set breakpoints in:
- `src/sspec/commands/change.py` (CLI layer)
- `src/sspec/services/change_service.py` (business logic)

Press F5 and step through the code.

### Scenario B: Debug `sspec ask create test`

```
Command: ask create test
Working directory: . (or leave blank)
```

View call stack in Debug panel to trace execution through:
- Click command handler
- Ask service logic

### Scenario C: Debug with file arguments

```
Command: ask prompt .sspec/asks/example.py
Working directory: .
```

### Scenario D: Debug project update with dry-run

```
Command: project update --dry-run
Working directory: ./tmp/demo-project
```

## Debug Panel Features

Once stopped at a breakpoint:

- **Step Into (F11)**: Enter function
- **Step Over (F10)**: Execute line without entering
- **Step Out (Shift+F11)**: Exit current function
- **Continue (F5)**: Resume execution
- **Variables Panel**: Inspect local/global variables
- **Watch Panel**: Monitor expression values
- **Call Stack**: See function call hierarchy

## Environment Variables

The debug runner respects:
- `PYTHONPATH`: Automatically set to include `src/`
- `DEBUG_CWD`: Alternative to `--cwd` flag (if set, overrides prompt)

## Troubleshooting

### "Python not found" or module import errors
- Ensure you're using Python 3.10+
- Check `.venv` is active: run `uv sync` first
- Verify `PYTHONPATH` includes `src/`

### Breakpoints not triggering
- Confirm **justMyCode** is **true** in launch.json (skips stdlib)
- Some Click decorators may require stepping into library code (set `justMyCode` to `false`)

### Command parsing error
- Verify command syntax: `uv run sspec <command>` should work first
- Check whitespace and quoting in prompt input

### Working directory not changing
- Use absolute path or `${workspaceFolder}/...` in prompt
- Check file system permissions

## Tips & Tricks

1. **Preset Commands**: Create custom launch configs for frequently-debugged commands:
   ```json
   {
       "name": "Debug change new",
       "type": "python",
       "request": "launch",
       "program": "${workspaceFolder}/scripts/debug_runner.py",
       "args": ["change", "new"],
       "cwd": "${workspaceFolder}/tmp/test"
   }
   ```

2. **Multi-session Debugging**: Can run multiple debug sessions in parallel
   - Open another VS Code window with same workspace
   - Start second debug session (will use different port)

3. **Debug Tests**: Use pytest debug config alongside CLI debugging:
   ```bash
   uv run pytest tests/test_change_service.py -v
   ```
   Then set breakpoints in service code and debug from there

4. **Trace Argument Parsing**: Set breakpoint in `click` decorator to see how Click parses your command

## Related Documentation

- `.sspec/project.md`: Project structure and conventions
- `src/sspec/cli.py`: CLI entry point and command registration
- `src/sspec/commands/`: Command implementations
- `src/sspec/services/`: Business logic (where most debugging happens)
