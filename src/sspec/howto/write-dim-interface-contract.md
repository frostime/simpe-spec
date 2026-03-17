---
name: write-dim-interface-contract
desc: "Design dimension: Interface Contract — function signatures, API contracts, type definitions."
type: design-dimension
---

# Interface Contract

## What It Answers

User's question: "What are the boundaries and contracts?"

## When to Choose

- Adding or modifying function signatures, class methods
- Defining or changing API endpoints
- Introducing new types, dataclasses, or schemas
- Configuration format changes with structured shape

## How to Write

Interfaces and type definitions MUST appear in fenced typed code blocks.
Prose is supplementary only — never describe a signature in words when you can show it.

```python
# Good — concrete, typed, annotatable
@dataclass
class ChangeRef:
    source: str             # workspace-relative path, no leading ./
    type: RefType           # 'request' | 'root-change' | 'sub-change' | 'doc'
    note: str | None = None  # NEW: optional annotation
```

```
# Bad — reader must mentally reconstruct the shape
Add an optional `note` field to ChangeRef. It's a string for annotation purposes.
```

For modified interfaces, use `# NEW` or `# CHANGED` inline comments to highlight
what is different from the current code. This lets the reviewer scan diffs mentally.

```python
def create_change(
    name: str,
    root: bool = False,
    from_request: str | None = None,
    tags: list[str] | None = None,   # NEW
) -> ChangePaths: ...
```

## Pairs Well With

- Behavioral Spec (interfaces define "what exists", behavior defines "how it's used")
- Data Architecture (when the interface exposes or consumes data models)
- Scope Summary / What Stays Unchanged blocks (when interface blast radius needs explicit boundaries)
