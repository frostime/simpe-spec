---
name: {{CHANGE_NAME}}
status: PLANNING
change-type: root
created: {{TIME}}
reference: null
---

<!-- @RULE: Frontmatter
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
<!-- @REPLACE -->

<!-- Root coordinator — describe the FULL scope across all phases. -->

## Proposed Solution
<!-- @REPLACE -->

### Overall Approach
<!-- High-level strategy. Delivery order, constraints, cross-phase coordination. -->

### Phase Overview
<!-- @RULE: List phases with goals and dependencies. Each phase becomes a sub-change.

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

Note: root spec MUST NOT include file-level detail.
File-level design belongs in each sub-change's own spec.md / design.md. -->

### Design Reference
<!-- 如果需要跨 phase 的架构设计约束，创建 design.md。
大多数 root change 不需要 — 设计在 sub-change 中。 -->
