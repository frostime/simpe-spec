---
name: write-patch
description: Use patch files + `sspec tool patch` for code modifications instead of direct file edits. Trigger when user requests patch-based workflow.
metadata:
  author: frostime
  version: 1.1.0
---

# Write-Patch Skill

> Format reference: `sspec tool patch --prompt`

## Workflow

1. Write one or more SEARCH/REPLACE patch blocks
2. Apply with one of:
   - `sspec tool patch PATCH_FILE`
   - `sspec tool patch --file PATCH_FILE`
   - `sspec tool patch --stdin --yes`
3. Verify output — watch for `already_applied`, ambiguity warnings, and failed bundle messages
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

## Quick Format Reference

```text
# <path>[:<range>]
<<<<<<< SEARCH
old content
=======
new content
>>>>>>> REPLACE
```

Line range examples: `:L10-L25`, `:L10-`, `:-L25`. Multiple blocks and interleaved text are allowed.

For full format specification (markers, matching behavior, path rules), run `sspec tool patch --prompt`.

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

Use separate blocks with line ranges to avoid ambiguity:

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

## Best Practices

### Size Your SEARCH Block Right

Write the smallest patch that matches uniquely.

- **Single-line change**: include ~1–2 surrounding context lines
- **Multi-line change**: include only the extra context needed for a unique match
- Too short → ambiguous match or false positive
- Too large → wastes tokens and breaks when unrelated lines change

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

### Use Line Ranges for Repeated Patterns

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

### Preserve Indentation Exactly

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

❌ **Placeholders or ellipsis** — SEARCH must contain actual file content:
```text
# BAD
<<<<<<< SEARCH
def foo():
    ... existing code ...
    return result
```

❌ **Mixed line endings** — if the file uses `\r\n`, SEARCH content should match

## Failure Recovery

- Failed patches are saved into one markdown bundle
- Fenced `patch` blocks in the bundle are directly reusable as future patch input
- `already_applied` status usually means the change is already in place — do not regenerate unless the target is wrong
