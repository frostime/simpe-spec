---
name: write-patch
description: Use patch files + `sspec tool patch` for code modifications instead of direct file edits. Trigger when user requests patch-based workflow.
metadata:
  author: sspec-tools
  version: 1.0.0
---

# Write-Patch Skill

## Workflow

1. **Generate patch file** (e.g., `fix-typo.patch.md`)
2. **Apply**: `sspec tool patch fix-typo.patch.md`
3. **Verify**: Check output, inspect failed patches if any

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
# src/utils.py:10-25
<<<<<<< SEARCH
old_code_here()
=======
new_code_here()
>>>>>>> REPLACE
```

Line range formats: `:10-25` or `:L10-L25` (both 1-based, inclusive)

## Critical Rules

1. **Exact Match Required**: SEARCH content must match file exactly (including indentation)
2. **Unique Match**: If SEARCH matches multiple locations → patch fails (use line range)
3. **Non-Empty SEARCH**: Empty SEARCH blocks are rejected (avoid accidental changes)
4. **Relative Paths Only**: Must be relative to project root or absolute path, no `..` traversal
5. **Marker Precision**: Markers `<<<<<<< SEARCH`, `=======`, `>>>>>>> REPLACE` must be alone on their line

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
# server.py:10-20
<<<<<<< SEARCH
PORT = 8080
=======
PORT = 3000
>>>>>>> REPLACE

# server.py:45-60
<<<<<<< SEARCH
log.info("Starting")
=======
log.info("Server starting on port %d", PORT)
>>>>>>> REPLACE
```

## Matching Behavior

1. **Exact match** (preferred): Whitespace and content match perfectly
2. **Loose match** (fallback): Ignores trailing spaces/tabs, collapses blank lines
3. **If multiple matches found**: Patch fails → add line range

## Best Practices

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
# utils.py:42-50
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

## Tool Options

```bash
sspec tool patch <file> [OPTIONS]

--dry-run              # Preview without applying
--yes                  # Skip confirmation
--output-failed DIR    # Custom dir for failed patches
--prompt               # Show format specification
```

## See Also

- `sspec tool patch --prompt` — Full specification
- `sspec tool patch --help` — Command options
