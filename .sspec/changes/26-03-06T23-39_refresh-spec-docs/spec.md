---
name: refresh-spec-docs
status: DONE
type: ""
change-type: single
created: 2026-03-06T23:39:00
reference:
  - source: ".sspec/changes/26-03-06T23-39_refresh-spec-docs/reference/doc-audit.md"
    type: "doc"
    note: "Initial audit of stale project context and missing spec-doc coverage"
---

<!-- @RULE: Frontmatter
status: PLANNING | DOING | REVIEW | DONE | BLOCKED
change-type: single | sub
reference?: Array<{source, type: 'request'|'root-change'|'sub-change'|'prev-change' |'doc', note?}>

Sub-change MUST link root:
reference:
  - source: ".sspec/changes/<root-change-dir>"
    type: "root-change"
    note: "Phase <n>: <phase-name>"

Single-change common reference:
reference:
  - source: ".sspec/requests/<request-file>.md"
    type: "request"
  - source: ".sspec/changes/<change-dir>"
    type: "prev-change"
    note: "This change is a follow-up to <change-name> which introduced <feature/bug>. This change addresses <issue> with that feature/bug."
-->

# refresh-spec-docs

## A. Problem Statement

Current self-hosted docs have drifted behind the repo in multiple places: at least 4 existing docs now describe outdated paths, field names, tool inventory, or platform behavior. That drift causes future agents to follow stale guidance when they read `.sspec/project.md` or use `.sspec/spec-docs/` as architectural truth.

User requirement: open a dedicated SSPEC change that refreshes the current project context and spec-doc set, not by ad hoc edits, but by a bounded documentation transaction that first fixes factual mismatches and then fills the highest-value missing long-lived contracts.

<!-- @RULE: Quantify impact. Format: "[metric] causing [impact]".
Simple: single paragraph. Complex: split "Current Situation" + "User Requirement". -->

## B. Proposed Solution

### Approach

Treat this as a single documentation change over the current self-hosted `.sspec/` docs.
The work happens in two layers:

1. Repair factual drift in the existing docs so nothing actively misleads future work.
2. Add a small set of new spec-docs for stable contracts that currently live only in code: change lifecycle, request/ask records, command registry, and root `AGENTS.md` sync.

Why this approach over a narrow one-file fix: the problem is not isolated to one document. The project context, spec-doc index, and contract docs are cross-linked, so partial edits would still leave the doc set internally inconsistent.

### Key Design

#### Interface Design

```python
from typing import Literal, TypedDict


DocAction = Literal['correct-existing', 'add-new', 'reindex']


class DocTarget(TypedDict):
    path: str
    action: DocAction
    purpose: str


EXISTING_DOC_FIXES: list[DocTarget] = [
    {
        'path': '.sspec/project.md',
        'action': 'correct-existing',
        'purpose': 'Refresh stable project context to match the live repo surface.',
    },
    {
        'path': '.sspec/spec-docs/skill-installation.md',
        'action': 'correct-existing',
        'purpose': 'Align install/sync behavior with current workspace locations and link policy.',
    },
    {
        'path': '.sspec/spec-docs/builtin-tools.md',
        'action': 'correct-existing',
        'purpose': 'Document the current builtin tool inventory and registration model.',
    },
]

NEW_SPEC_DOCS: list[DocTarget] = [
    {
        'path': '.sspec/spec-docs/change-lifecycle.md',
        'action': 'add-new',
        'purpose': 'Capture change directory structure, status parsing, and archive semantics.',
    },
    {
        'path': '.sspec/spec-docs/interaction-records.md',
        'action': 'add-new',
        'purpose': 'Capture request/ask file schemas plus link/archive behavior.',
    },
    {
        'path': '.sspec/spec-docs/cmd-registry.md',
        'action': 'add-new',
        'purpose': 'Capture `.sspec/commands/registry.yaml` and script strategy rules.',
    },
    {
        'path': '.sspec/spec-docs/agents-sync.md',
        'action': 'add-new',
        'purpose': 'Capture root `AGENTS.md` managed block ownership and update behavior.',
    },
]
```

#### Data Flow

```text
Project doc audit
  │
  ├── classify drifted docs            → fix wrong paths, field names, and behavior claims first
  ├── map stable runtime contracts     → choose missing contracts worth long-lived spec-docs
  ├── write/update `.sspec` docs       → apply write-spec-doc frontmatter and concrete scope lists
  ├── rebuild indexes and cross-links  → sync `.sspec/project.md` and `.sspec/spec-docs/README.md`
  └── verify doc set                   → check headings, frontmatter, and code/doc consistency
```

The verification step stays documentation-focused: compare each changed statement against the current code paths and ensure every new spec-doc is discoverable from the existing indexes.

#### Key Logic

**Fix A: Project context refresh** — Update `.sspec/project.md` so the stable identity layer matches the actual stack, command surface, builtin tools, and current platform behavior.

**Fix B: Existing spec-doc drift repair** — Correct stale facts in `.sspec/spec-docs/README.md`, `.sspec/spec-docs/skill-installation.md`, `.sspec/spec-docs/builtin-tools.md`, and `.sspec/spec-docs/testing-standards.md` before adding new docs.

**Doc C: Change lifecycle contract** — Add a spec-doc for `.sspec/changes/<timestamp>_<name>/`, status parsing, archive moves, and reference rewrite behavior so future work does not depend on rediscovering `change_service.py`.

**Doc D: Interaction record contracts** — Add a spec-doc for request and ask artifacts, covering creation format, linking, answer persistence, and archive rewrite behavior.

**Doc E: Command registry contract** — Add a spec-doc for `.sspec/commands/registry.yaml`, script storage, and `copy` / `move` / `ref` strategy semantics.

**Doc F: Root AGENTS sync contract** — Add a spec-doc for the managed `SSPEC:START/END` block so future template or self-hosting work knows what is auto-managed versus user-owned.

#### Scope Summary

| File | Change |
|------|--------|
| `.sspec/project.md` | Refresh stack, key paths, conventions, and spec-doc index hints to match current repo behavior |
| `.sspec/spec-docs/README.md` | Expand the index and make the spec-doc set navigable |
| `.sspec/spec-docs/skill-installation.md` | Correct workspace location names and current Windows link behavior |
| `.sspec/spec-docs/builtin-tools.md` | Document the current four builtin tools and update registration rationale |
| `.sspec/spec-docs/testing-standards.md` | Remove dead modules and align expectations with current tests/modules |
| `.sspec/spec-docs/change-lifecycle.md` | Add change directory, status, archive, and reference rewrite contract |
| `.sspec/spec-docs/interaction-records.md` | Add request/ask file format and lifecycle contract |
| `.sspec/spec-docs/cmd-registry.md` | Add command registry and script strategy contract |
| `.sspec/spec-docs/agents-sync.md` | Add root `AGENTS.md` managed block sync contract |
