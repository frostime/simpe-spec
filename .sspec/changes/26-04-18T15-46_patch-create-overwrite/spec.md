---
name: patch-create-overwrite
status: DONE
change-type: single
created: 2026-04-18T15:46:58
reference:
  - source: ".sspec/spec-docs/builtin-tools.md"
    type: "doc"
    note: "Builtin tool contract that documents patch behavior."
  - source: ".sspec/changes/26-04-18T15-46_patch-create-overwrite/revisions/001-shorten-patch-prompt-and-add-installed-skill-reference.md"
    type: "revision"
    note: "Review feedback: shorten patch prompt and add installed write-patch skill reference."
  - source: ".sspec/changes/26-04-18T15-46_patch-create-overwrite/revisions/002-fix-create-idempotence-and-clean-unused-patch-status.md"
    type: "revision"
    note: "Review feedback: normalize CREATE idempotence across newline styles and remove an unused status."
---

# patch-create-overwrite

## Problem Statement

`sspec tool patch` can edit existing files and initialize existing empty files, but one patch bundle cannot explicitly create a missing file or replace an entire existing file. This forces agents to mix `sspec tool patch` with `sspec tool write`/shell file creation for common changes, causing patch artifacts to be less self-contained and harder to review/retry.

The patch format needs two explicit file-level operations: safe new-file creation and full-file overwrite. Both operations must preserve the patch tool's safety posture: no accidental overwrite during creation, no silent creation during overwrite, and no ambiguous empty-SEARCH behavior for missing files.

## Proposed Solution

### Approach

Extend the existing patch grammar with two new block operation markers while keeping the current SEARCH/REPLACE contract and current LRR (line-role-regex) parser architecture intact. The design follows an Occam-style rule: preserve the existing two-phase `lrr_scan() -> PATCH_PATTERN` pipeline, broaden the opening-marker classification just enough to recognize `SEARCH`, `CREATE`, and `OVERWRITE`, and carry the concrete operation on `PatchBlock` instead of replacing the parser with a new grammar engine.

```patch
# path/to/new-file.md
<<<<<<< CREATE
=======
new content
>>>>>>> REPLACE
```

```patch
# path/to/existing-file.md
<<<<<<< OVERWRITE
=======
full file content
>>>>>>> REPLACE
```

`CREATE` and `OVERWRITE` are file-level operations. Their upper section is only a structural placeholder and must contain whitespace only. Their `REPLACE` section is the full target content, including the empty string when the desired output is an empty file. Existing `<<<<<<< SEARCH` blocks continue to use scoped matching, line ranges, loose fallback, and already-applied detection exactly as they do today.

### Key Change

**Feat A: Patch block operation model with LRR-preserving parsing** — Add an operation field to parsed patch blocks with three values: `SEARCH`, `CREATE`, and `OVERWRITE`. Parsing recognizes `<<<<<<< SEARCH`, `<<<<<<< CREATE`, and `<<<<<<< OVERWRITE`, while the delimiter and closing marker remain `=======` and `>>>>>>> REPLACE`. At the LRR layer, the opener stays one schema role so the existing `PATCH_PATTERN` shape remains stable; the concrete operation is decoded from the opener text after block extraction.

**Feat B: Safe CREATE semantics** — `CREATE` creates a missing file and automatically creates missing parent directories. If the file already exists with identical content, the result is `already_applied`; if it exists with different content, the patch fails with a file-exists style status to prevent accidental overwrite. `SEARCH + empty content` remains limited to existing empty files and does not gain missing-file creation semantics.

**Feat C: Explicit OVERWRITE semantics** — `OVERWRITE` replaces the complete contents of an existing file. If the file already has identical content, the result is `no_change_patch`; if the file is missing, the patch fails with `missing_file`. `OVERWRITE` never creates a file.

**Feat D: File-level validation and diagnostics** — `CREATE` and `OVERWRITE` reject line ranges as invalid file-level patch blocks. Their upper section must contain whitespace only. Result display, failed bundle output, and patch previews preserve the original operation marker so users can review and retry failed file-level patches without losing intent.

**Docs E: Prompt and docs synchronization** — Update the built-in `PATCH_PROMPT`, builtin tool spec-doc, and write-patch skill template so users and agents see the CREATE/OVERWRITE grammar, safety rules, examples, and non-goals.

### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/builtin_tools/apply_patch.py` | Extend parser/data model/apply logic/result formatting for `CREATE` and `OVERWRITE`; update built-in `PATCH_PROMPT` |
| `tests/test_apply_patch.py` | Add focused helper tests for create, overwrite, validation errors, idempotence, empty content, and missing/existing-file safety |
| `.sspec/spec-docs/builtin-tools.md` | Document patch CREATE/OVERWRITE operation markers and safety behavior |
| `src/sspec/templates/skills/write-patch/SKILL.md` | Update product skill guidance with file-level patch operations and examples |

### Design Reference

→ Detailed technical design: [design.md](./design.md)
