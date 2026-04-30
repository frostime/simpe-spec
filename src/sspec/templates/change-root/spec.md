---
name: {{CHANGE_NAME}}
status: PLANNING
change-type: root
created: {{TIME}}
reference: null
---

<!-- MUST follow frontmatter schema:
status: PLANNING | DOING | REVIEW | DONE | BLOCKED
change-type: root (coordinator for sub-changes)
reference?: Array<{source, type: 'request'|'sub-change'|'doc', note?}>

Root reference rules:
- If created from a request, include a `type: request` entry.
- For every created sub-change, append one `type: sub-change` entry.

Example:
reference:
  - source: ".sspec/changes/<sub-change-dir>"
    type: "sub-change"
    note: "Phase <n>: <phase-name>"
-->

# {{CHANGE_NAME}}

## Problem Statement

<!-- Root coordinator — describe the FULL scope across all phases. -->

## Proposed Solution

### Overall Approach
<!-- High-level strategy. Delivery order, constraints, cross-phase coordination. -->

### Phase Overview
<!-- MUST list phases with goals and dependencies. Each phase becomes a sub-change.

Format (≤3 phases): dependency-annotated list + ASCII dependency tree
Format (≥4 phases): dependency table

| Phase | Goal | Depends On | Scope |
|-------|------|-----------|-------|
| Phase 1: <name> | measurable goal | — | subsystems/modules |
| Phase 2: <name> | measurable goal | Phase 1 | subsystems/modules |

Coordination Notes:
- Cross-phase constraints, shared interfaces, integration handoffs
- Which phases can run in parallel

When a sub-change is created, sync references in BOTH directions:
- Root spec.md adds `type: sub-change` entry
- Sub spec.md adds `type: root-change` entry back

Root spec MUST NOT include file-level detail.
File-level design belongs in each sub-change's own spec.md / design.md. -->

### Design Reference
<!-- SHOULD create design.md only when cross-phase architectural constraints exist.
Most root changes don't need it — design lives in sub-changes. -->
