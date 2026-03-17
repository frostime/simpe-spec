---
name: write-dim-data-architecture
desc: "Design dimension: Data Architecture — schemas, data models, storage structures, data pipelines."
type: design-dimension
---

# Data Architecture

## What It Answers

User's question: "What does the data look like and how does it flow?"

## When to Choose

- Introducing or modifying database schemas, data models
- Changing serialization formats (JSON, YAML, frontmatter)
- Building data transformation pipelines
- Storage structure changes (file layout, cache keys, index design)

## How to Write

Data models and schemas MUST appear in fenced typed code blocks, just like
interfaces. Show the shape, not a prose description.

```python
@dataclass
class HowtoInfo:
    name: str
    lookup_key: str
    description: str
    path: Path
    source: HowtoSource
    file: str
    type: str | None = None  # NEW: optional classification
```

For file/record formats, show a concrete example:

```yaml
# HOWTO frontmatter schema
---
name: write-dim-interface-contract
desc: "Design dimension: Interface Contract"
type: design-dimension          # NEW: optional, for filtering
---
```

For data transformation pipelines, combine with an ASCII flow:

```text
Raw YAML frontmatter
  │
  ├── parse_frontmatter()     → dict[str, Any]
  ├── extract name/desc/type  → typed fields
  └── build HowtoInfo         → frozen dataclass
```

When showing schema evolution (before/after), put them side by side or
sequentially with clear labels:

```python
# Before
class HowtoInfo:
    name: str
    description: str

# After
class HowtoInfo:
    name: str
    description: str
    type: str | None = None  # NEW
```

## Pairs Well With

- Interface Contract (data models often surface through interfaces)
- Migration Path (schema changes usually need migration strategy)
- Behavioral Spec (shows how data moves through the system)
