---
name: write-dim-behavioral-spec
desc: "Design dimension: Behavioral Spec — call chains, state machines, algorithm flows."
type: design-dimension
---

# Behavioral Spec

## What It Answers

User's question: "How does the system behave?"

## When to Choose

- Adding or changing a multi-step process or workflow
- Implementing algorithms with branching logic
- State machines or lifecycle transitions
- Call chains across multiple modules

## How to Write

Use ASCII trees or flowcharts with `│ ├── └──` notation. Always pair the
diagram with a short explanatory text — the diagram shows structure, the text
explains intent and edge cases.

```text
sspec change new <name> --from <request>
  │
  ├── parse_request(req_path)       → read frontmatter, extract name
  ├── create_change_dir(name)       → mkdir .sspec/changes/<ts>_<name>/
  ├── copy_templates()              → spec.md, tasks.md, memory.md
  └── link_request(req, change)     → bidirectional reference update

The link_request step writes to both files: request gets `attach-change`,
spec.md gets a `type: request` reference entry.
```

For state machines, show states and transitions:

```text
PLANNING ──→ DOING ──→ REVIEW ──→ DONE
    │                     │
    └── BLOCKED ←─────────┘
         │
         └──→ DOING (when unblocked)
```

**Bad** — text-only narration without visual structure:

```text
When creating a change from a request, the system reads the request,
creates a directory, copies templates, then links them bidirectionally.
```

The diagram is the primary artifact. If you can't draw it, the behavior
may not be well-understood enough to design.

## Pairs Well With

- Interface Contract (behavior shows "how it runs", interfaces show "what it exposes")
- Outcome Preview (behavior shows the process, outcome shows the result)
- Structural Blueprint (behavior shows how things interact, structure shows where they live)
