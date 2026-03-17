---
name: write-dim-structural-blueprint
desc: "Design dimension: Structural Blueprint — module organization, file trees, component hierarchy."
type: design-dimension
---

# Structural Blueprint

## What It Answers

User's question: "How are things organized?"

## When to Choose

- Refactoring that changes module boundaries or file layout
- Introducing a new package, directory, or component hierarchy
- Reorganizing existing code into layers or subsystems
- Template or project structure changes

## How to Write

Use ASCII trees to show the target structure. Annotate each node briefly.

```text
src/sspec/
├── commands/          # CLI layer (thin: validate → call service → format)
│   ├── change.py
│   └── howto.py       # NEW: --type filter
├── services/          # Business logic (no CLI deps)
│   └── howto_service.py  # CHANGED: HowtoInfo.type field
├── howto/             # Builtin HOWTO files
│   ├── resume-change.md
│   └── write-dim-*.md    # NEW: 8 dimension cards
└── templates/
    └── skills/
        └── sspec-design/
            ├── SKILL.md           # CHANGED: dimension menu
            ├── examples-feature.md   # NEW (replaces examples-single.md)
            ├── examples-docs.md      # NEW
            └── examples-refactor.md  # NEW
```

For before/after reorganizations, show both trees side by side or sequentially:

```text
# Before
src/auth.py          (2,400 LOC monolith)

# After
src/auth/
├── __init__.py
├── service.py       # AuthService class
├── jwt.py           # Token handling
└── middleware.py     # Request authentication
```

Keep annotations short — one phrase per node. The tree itself carries most of
the information; annotations clarify intent, not implementation.

## Pairs Well With

- Migration Path (structure shows "where things end up", migration shows "how to get there")
- Impact Map (structure change implies file moves/renames worth listing)
