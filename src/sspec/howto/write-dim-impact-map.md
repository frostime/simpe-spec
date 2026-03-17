---
name: write-dim-impact-map
desc: "Design dimension: Impact Map — scope boundaries, blast radius, what changes and what doesn't."
type: design-dimension
---

# Impact Map

## What It Answers

User's question: "What changes and what doesn't?"

## When to Choose

- Any change affecting 3 or more files
- Changes where the blast radius is non-obvious
- When explicitly stating "what stays unchanged" reduces user anxiety
- When scope boundaries are themselves part of the design decision

## How to Write

**Scope Summary table** — the primary form. Required for changes affecting ≥3 files:

```markdown
| File | Change |
|------|--------|
| `src/sspec/services/howto_service.py` | Add `type` field to `HowtoInfo`; parse in `collect_howtos` |
| `src/sspec/commands/howto.py` | Add `--type` filter to `list_cmd`; type column in output |
| `src/sspec/howto/write-dim-*.md` | New: 8 dimension howto cards |
```

**"What stays unchanged" section** — explicitly list things the user might
worry about but that are NOT being touched:

```markdown
### What Stays Unchanged
- Root change Step 3B (already has its own structure)
- examples-root.md (root scenario unchanged)
- Section A writing norms
- Existing howto files (type is optional, backward compatible)
```

This is not filler — it's a deliberate anxiety reducer. Users reading a
design for a broad change need to know the blast radius has boundaries.

**Item labeling** — for changes with ≥3 independent items, label each:

```markdown
**Change A: Howto type field** — Add optional `type` to HowtoInfo.
**Change B: List filter** — `sspec howto list --type` filters by type.
**Change C: Dimension cards** — 8 new howto files under `src/sspec/howto/`.
```

Labels create stable cross-references for tasks.md:
`- [ ] Implement Change A per spec.md §B`

## Pairs Well With

- A common companion when boundaries matter, but not mandatory.
- Content Outline (for document changes, Impact Map shows which files change)
- Interface Contract (for code changes, Impact Map shows the blast radius)
