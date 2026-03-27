---
name: {{CHANGE_NAME}}
status: PLANNING
type: ""
change-type: root
created: {{TIME}}
reference: null
---

<!-- @RULE: Frontmatter
status: PLANNING | DOING | REVIEW | DONE | BLOCKED
change-type: root (coordinator for sub-changes)
reference?: Array<{source, type: 'request'|'root-change'|'sub-change'|'doc', note?}>

Root reference rules:
- If created from a request, include a `type: request` entry.
- For every created sub-change, append one `type: sub-change` entry.

Example:
reference:
  - source: ".sspec/requests/<request-file>.md"
    type: "request"
  - source: ".sspec/changes/<sub-change-dir>"
    type: "sub-change"
    note: "Phase <n>: <phase-name>"
-->

# {{CHANGE_NAME}}

## A. Problem Statement
<!-- @REPLACE -->

<!-- @RULE: Overall impact. This is the root coordinator — describe the FULL scope. -->

## B. Proposed Solution
<!-- @REPLACE -->

### Overall Approach
<!-- High-level strategy. How will this be broken into phases? Delivery order? -->

### Phase Overview
<!-- @RULE: List phases with goals and dependencies. Each phase becomes a sub-change.

Format (≤3 phases): dependency-annotated list + ASCII dependency tree
- **Phase 1: <name>** — goal, measurable deliverable, scope (subsystems/modules)
- **Phase 2: <name>** — goal, measurable deliverable, dependencies on Phase 1

Dependency tree:
Phase 1: <name>
  ├── Phase 2: <name>  (depends on Phase 1)
  └── Phase 3: <name>  (depends on Phase 1, independent of Phase 2)

Format (≥4 phases): use a dependency table
| Phase | Goal | Depends On | Scope |
|-------|------|-----------|-------|
| Phase 1: <name> | measurable goal | — | subsystems/modules |
| Phase 2: <name> | measurable goal | Phase 1 | subsystems/modules |

Coordination Notes:
- Cross-phase constraints, shared interfaces, integration handoffs
- Which phases can run in parallel

When a sub-change is created, the agent MUST sync references in BOTH directions:
- Root `spec.md` adds `type: sub-change` entry for the sub-change
- Sub `spec.md` adds `type: root-change` entry back to this root

Note: root spec MUST NOT include file-level interface/data-model detail.
File-level design belongs in each sub-change's own spec.md Section B. -->
