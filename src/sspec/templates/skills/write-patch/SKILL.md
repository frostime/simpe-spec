---
name: write-patch
description: Use patch files + `sspec tool patch` for code modifications instead of direct file edits. Trigger when user requests patch-based workflow.
metadata:
  author: frostime
  version: 1.0.0
---

# Write-Patch Skill

## Workflow

1. Write one or more SEARCH/REPLACE patch blocks
2. Apply with one of:
   - `sspec tool patch PATCH_FILE`
   - `sspec tool patch --file PATCH_FILE`
   - `sspec tool patch --stdin --yes`
3. Verify output, especially `already_applied`, ambiguity, and failed bundle messages
4. If patch application fails, refine the failed markdown bundle and apply it again

### Example Session

```
Agent: I'll create a patch file for these changes.

# fix-imports.patch.md
# src/utils.py
<<<<<<< SEARCH
from typing import List
=======
from typing import List, Dict
>>>>>>> REPLACE

# src/config.py
<<<<<<< SEARCH
DEBUG = True
=======
DEBUG = False
>>>>>>> REPLACE

Agent: Apply with: `sspec tool patch fix-imports.patch.md`
```

### Example via stdin

```bash
cat <<'EOF' | sspec tool patch --stdin --yes
# src/utils.py
<<<<<<< SEARCH
from typing import List
=======
from typing import List, Dict
>>>>>>> REPLACE
EOF
```

## Patch Format

Each patch block consists of:

1. **File path line** (required, precedes SEARCH marker)
2. **SEARCH/REPLACE block** (markers must be alone on their line)

### Simple Patch (No Line Range)

```text
# path/to/file.py
<<<<<<< SEARCH
old_code_here()
=======
new_code_here()
>>>>>>> REPLACE
```

### With Line Range (Reduce Ambiguity)

```text
# src/utils.py:L10-L25
<<<<<<< SEARCH
old_code_here()
=======
new_code_here()
>>>>>>> REPLACE
```

Preferred line range formats:
- `:L10-L25`
- `:L10-`
- `:-L25`

Legacy `:10-25` is still accepted, but do not use it as the default style.

### Multiple Patch Blocks

Multiple patch blocks can be combined in one file or stdin payload.

You may insert explanation text between patch blocks. Each patch block only needs to keep its own format valid.

```text
Notes for the next patch block.

# server.py:L10-L20
<<<<<<< SEARCH
PORT = 8080
=======
PORT = 3000
>>>>>>> REPLACE

This second patch updates logging.

# server.py:L45-L60
<<<<<<< SEARCH
log.info("Starting")
=======
log.info("Server starting on port %d", PORT)
>>>>>>> REPLACE
```

## Critical Rules

1. **Exact Match Required**: SEARCH content must match file exactly (including indentation)
2. **Unique Match**: If SEARCH matches multiple locations → patch fails (use line range)
3. **Non-Empty SEARCH**: Empty SEARCH blocks are rejected (avoid accidental changes)
4. **Path Resolution**: Relative paths resolve from workspace root; absolute paths are allowed
5. **Outside-Workspace Safety**: Absolute paths outside the current workspace require explicit confirmation, or `--unsafe` for automation
6. **Target Files Must Exist**: `sspec tool patch` edits existing files only
7. **Already Applied Is Not Fatal**: If SEARCH is missing but REPLACE exists uniquely in scope, status becomes `already_applied`
8. **Marker Precision**: Markers `<<<<<<< SEARCH`, `=======`, `>>>>>>> REPLACE` must be alone on their line

## Common Patterns

### Adding Code

```text
# src/app.py
<<<<<<< SEARCH
def main():
    setup()
    return 0
=======
def main():
    setup()
    init_logging()    # Added
    return 0
>>>>>>> REPLACE
```

### Removing Code

```text
# config.py
<<<<<<< SEARCH
DEBUG = True
VERBOSE = True
=======
DEBUG = True
>>>>>>> REPLACE
```

### Multiple Changes in One File

Create separate SEARCH/REPLACE blocks:

```text
# server.py:L10-L20
<<<<<<< SEARCH
PORT = 8080
=======
PORT = 3000
>>>>>>> REPLACE

# server.py:L45-L60
<<<<<<< SEARCH
log.info("Starting")
=======
log.info("Server starting on port %d", PORT)
>>>>>>> REPLACE
```

## Matching Behavior

1. **Exact match** (preferred): Whitespace and content match perfectly
2. **Loose match** (fallback): Ignores trailing spaces/tabs, collapses blank lines
3. **Already applied**: SEARCH missing + REPLACE uniquely present → `already_applied`
4. **If multiple matches found**: Patch fails → add line range

## Best Practices

### Use Just-Enough Context

Write the smallest patch that is still precise and stable.

- For a **single-line replacement**, usually include about 1-2 surrounding context lines before and after
- For a **multi-line replacement**, include the changed block and only the extra context needed to make the match unique
- Avoid overly short SEARCH blocks that mismatch easily
- Avoid overly large SEARCH blocks that waste tokens and become brittle

Goal: precise enough to avoid mismatch, small enough to avoid unnecessary token cost

### Include Context Lines

**Bad** (too short, ambiguous):
```text
<<<<<<< SEARCH
return x
=======
return x * 2
>>>>>>> REPLACE
```

**Good** (sufficient context):
```text
<<<<<<< SEARCH
def compute(x):
    result = validate(x)
    return x
=======
def compute(x):
    result = validate(x)
    return x * 2
>>>>>>> REPLACE
```

### Use Line Ranges for Ambiguous Searches

When the same code pattern appears multiple times:
```text
# utils.py:L42-L50
<<<<<<< SEARCH
if value is None:
    return default
=======
if value is None:
    raise ValueError("Value required")
>>>>>>> REPLACE
```

### Preserve Indentation

Match the file's indentation style exactly:
```text
# main.py
<<<<<<< SEARCH
    def process(self):
        data = self.load()
        return data
=======
    def process(self):
        data = self.load()
        validated = self.validate(data)
        return validated
>>>>>>> REPLACE
```

## Anti-Patterns

❌ **Don't use placeholders or ellipsis**:
```text
# BAD
<<<<<<< SEARCH
def foo():
    ... existing code ...
    return result
=======
```

✅ **Include actual code**:
```text
# GOOD
<<<<<<< SEARCH
def foo():
    x = compute()
    y = transform(x)
    return result
=======
```

❌ **Don't mix line endings** (if file uses `\r\n`, SEARCH should too)

## Failure Recovery

- Failed patches are saved into one markdown bundle
- The bundle may contain explanation text outside fenced `patch` blocks
- Those fenced `patch` blocks remain directly reusable as future patch input
- If a patch reports `already_applied`, usually do not regenerate it unless the target is wrong

## Tool Options

```bash
sspec tool patch [PATCH_FILE] [OPTIONS]

--dry-run              # Preview without applying
--stdin                # Read patch text from stdin
--yes                  # Skip confirmation
--unsafe               # Bypass outside-workspace absolute path confirmation
--output-failed PATH   # Custom markdown file or directory for failed patches
--file, -f PATH        # Read patch text from file (alternative to positional PATCH_FILE)
--input, -i            # Enter patch text interactively
--prompt               # Show format specification
```

## See Also

- `sspec tool patch --prompt` — Full specification
- `sspec tool patch --help` — Command options
