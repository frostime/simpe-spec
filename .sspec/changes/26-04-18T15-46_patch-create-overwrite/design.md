---
change: "patch-create-overwrite"
created: 2026-04-18T15:46:58
---

# Design: patch-create-overwrite

## Interface Contract

```python
PatchOperation = Literal['search', 'create', 'overwrite']
PatchOutcomeStatus = Literal[
    'applied',
    'already_applied',
    'search_not_found',
    'search_ambiguous',
    'replace_ambiguous',
    'search_replace_coexist',
    'invalid_path',
    'missing_file',
    'not_a_file',
    'invalid_line_range',
    'invalid_operation_body',
    'file_exists',
    'out_of_range',
    'parse_error',
    'write_error',
    'no_change_patch',
]

@dataclass
class PatchBlock:
    file_path: Path
    display_path: str
    operation: PatchOperation
    line_range: tuple[int | None, int | None] | None
    search_content: str
    replace_content: str
    source_line_start: int
```

Notes:
- `search_content` remains populated for every block so preview/failed-bundle code can reuse one structure.
- `CREATE` / `OVERWRITE` keep `search_content` as the raw upper block text for validation and faithful retry output.
- `invalid_operation_body` covers non-whitespace content between `<<<<<<< CREATE|OVERWRITE` and `=======`.
- `file_exists` distinguishes safe-create conflicts from generic write failures.

## Parsing Model

### LRR Strategy

The current parser already has the right shape:

```text
patch text
  └── lrr_scan()
        ├── classify each line into schema roles
        └── schema string + original lines
              └── PATCH_PATTERN match
                    └── extract one patch block
```

This change keeps that architecture.

Minimal-change strategy:

1. Keep the existing LRR two-phase design (`classify_line` + regex over role schema).
2. Keep one shared opener role for all patch openers so `PATCH_PATTERN` stays structurally the same.
3. Add a tiny opener decoder that maps the raw marker line to `search | create | overwrite` after the block is found.
4. Push operation-specific validation into parse/apply helpers instead of multiplying schema roles or replacing regex parsing.

Result: the parser gains new semantics with a narrow delta in classification, block extraction, and validation code.

### Block Shape

```text
header line
  + operation opener
  + upper block body
  + =======
  + replace body
  + >>>>>>> REPLACE
        │
        └── PatchBlock(operation, search_content, replace_content, line_range)
```

Marker grammar:

```text
<<<<<<< SEARCH
<<<<<<< CREATE
<<<<<<< OVERWRITE
```

### LRR Role Handling

```text
F - file header
S - any supported opening marker
D - =======
R - >>>>>>> REPLACE
B - blank line
C - content line
```

Decoder step:

```python
parse_patch_operation(opener: str) -> Literal['search', 'create', 'overwrite']
```

Design choice:
- `S` continues to mean “patch opener line” in the LRR schema.
- The schema regex stays `F(?P<gap>B*)S(?P<search>[BC]*?)D(?P<replace>[BC]*?)R` or an equivalent same-shape variant.
- `CREATE` and `OVERWRITE` are distinguished from `SEARCH` by inspecting the raw opener text, not by inventing extra schema symbols like `C`/`O` opener roles.

Rules:
1. `SEARCH` keeps existing semantics.
2. `CREATE` / `OVERWRITE` allow whitespace-only upper body.
3. `CREATE` / `OVERWRITE` reject any line range in the header.
4. `CREATE` allows missing file targets; `SEARCH` and `OVERWRITE` require an existing file.
5. Relative path confinement and outside-workspace absolute path confirmation remain unchanged.
6. The LRR extension should stay local to opener recognition and post-match validation; broad parser rewrites are out of scope.

## Apply Flow

```text
parse_patches()
  ├── resolve path
  ├── classify operation
  ├── validate existence rules by operation
  └── return PatchBlock list

apply_patch(block)
  ├── operation == search
  │     └── existing scoped search/replace algorithm
  ├── operation == create
  │     ├── target missing        → mkdir parents → write full content → applied
  │     ├── target exists same    → already_applied
  │     └── target exists diff    → file_exists
  └── operation == overwrite
        ├── target missing        → missing_file
        ├── target exists same    → no_change_patch
        └── target exists diff    → write full content → applied
```

## Behavioral Spec

### SEARCH

```text
existing file
  ├── empty SEARCH + empty file          → initialize existing empty file
  ├── unique SEARCH match                → apply replacement
  ├── SEARCH absent + REPLACE present    → already_applied
  └── ambiguity / bounds issue           → current failure statuses
```

### CREATE

```text
missing file
  ├── whitespace-only upper body         → create file (parents auto-created)
  └── non-whitespace upper body          → invalid_operation_body

existing file
  ├── same full content                  → already_applied
  └── different content                  → file_exists
```

### OVERWRITE

```text
existing file
  ├── same full content                  → no_change_patch
  ├── different full content             → overwrite file
  └── non-whitespace upper body          → invalid_operation_body

missing file                             → missing_file
```

## Preview / Failed Bundle Format

```patch
# docs/new.md
<<<<<<< CREATE
=======
hello
>>>>>>> REPLACE
```

```patch
# src/config.py
<<<<<<< OVERWRITE
=======
FULL = True
>>>>>>> REPLACE
```

Formatting requirement: `_format_patch_preview()` and failed bundle output must emit the original marker (`SEARCH`, `CREATE`, or `OVERWRITE`) so retries preserve the intended operation.

## Prompt Contract Additions

`PATCH_PROMPT` should document:
- the three operation markers
- `CREATE` / `OVERWRITE` as file-level operations
- `CREATE` creates parents automatically
- `CREATE` returns conflict when file exists with different content
- `OVERWRITE` requires an existing file
- line ranges apply only to `SEARCH`
- empty `SEARCH` remains only for existing empty files

## Minimal-Change Principle

```text
Before
  classify opener: SEARCH only
  PATCH_PATTERN: one opener role + body + delimiter + replace
  parse result: PatchBlock without operation
  apply: search-based algorithm only

After
  classify opener: SEARCH | CREATE | OVERWRITE
  PATCH_PATTERN: same shape
  parse result: PatchBlock with operation
  apply: dispatch search/create/overwrite
```

This is the intended Occam boundary:
- preserve `lrr_scan()`
- preserve schema-regex extraction
- add one operation decoder
- add two file-level apply branches
- reuse existing preview/result/failure infrastructure with marker-aware formatting

## Scope Mapping

| File | Design Work |
|------|-------------|
| `src/sspec/builtin_tools/apply_patch.py` | Extend grammar, parse validation, file-level apply branches, preview rendering, and prompt text |
| `tests/test_apply_patch.py` | Encode CREATE/OVERWRITE contract and safety/idempotence edge cases |
| `.sspec/spec-docs/builtin-tools.md` | Publish shipped patch grammar and safety semantics |
| `src/sspec/templates/skills/write-patch/SKILL.md` | Teach agents when to use SEARCH vs CREATE vs OVERWRITE |
