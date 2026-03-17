---
name: write-dim-migration-path
desc: "Design dimension: Migration Path — before/after comparison, migration steps, compatibility strategy."
type: design-dimension
---

# Migration Path

## What It Answers

User's question: "How do we get from here to there?"

## When to Choose

- Schema or format migration (database, config files, frontmatter)
- Refactoring that requires incremental transition
- Breaking changes that need backward compatibility strategy
- Data conversion or file format upgrades
- Any change where the transition itself is the hard part

## How to Write

Show the before/after state clearly, then describe the transition strategy.

**Before/after comparison** — always start here:

```yaml
# Before: howto frontmatter
---
name: resume-change
desc: Resume an in-progress change.
---

# After: howto frontmatter (type field added)
---
name: resume-change
desc: Resume an in-progress change.
type: null                    # NEW: optional, backward compatible
---
```

**Migration strategy** — explain how existing data transitions:

```text
Migration: backward-compatible addition
- New `type` field is optional, defaults to None
- Existing howto files without `type` continue to work unchanged
- No data migration needed — new field is read-only at parse time
- Rollback: simply ignore the field (it's optional)
```

**For breaking migrations**, show the step sequence:

```text
Migration steps:
1. Deploy new code that reads both old and new format
2. Run migration script: convert old records to new format
3. Verify: all records parse correctly in new format
4. Remove old-format reading code in next release
```

**Compatibility matrix** — useful for multi-version transitions:

```text
| Version | Old format | New format |
|---------|-----------|------------|
| v1.5    | read/write | —          |
| v1.6    | read-only  | read/write |
| v1.7    | —          | read/write |
```

## Pairs Well With

- Data Architecture (migration changes the data shape)
- Outcome Preview (shows the target state after migration)
- Scope Summary / What Stays Unchanged blocks (when migration touches specific files or compatibility surfaces)
