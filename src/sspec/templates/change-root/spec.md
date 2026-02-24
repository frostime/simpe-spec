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
<!-- @RULE: List phases with goals. Each phase becomes a sub-change.

Format:
- **Phase 1: <name>** — goal, measurable deliverable, scope (subsystems/modules)
- **Phase 2: <name>** — goal, measurable deliverable, dependencies on Phase 1

Coordination Notes:
- Cross-phase dependencies, shared interfaces, integration points -->
