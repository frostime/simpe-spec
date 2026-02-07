---
name: {{CHANGE_NAME}}
status: PLANNING
type: ""
change-type: root
created: {{TIME}}
reference: null
---

<!-- @RULE: Frontmatter Type
status: PLANNING | DOING | REVIEW | DONE | BLOCKED;
change-type: root (coordinator for sub-changes);
reference?: Array<{source: str; type: RefType; note?}>;
type RefType: 'request' | 'root-change' | 'sub-change' | 'doc';
 -->

# {{CHANGE_NAME}}

## A. Problem Statement
<!-- @REPLACE -->

<!-- @RULE: Quantify overall impact. This is the root coordinator — describe the full scope, not a single module. -->

## B. Proposed Solution
<!-- @REPLACE -->

### Overall Approach
<!-- @RULE: High-level strategy. How will this be broken into phases? What's the delivery order? -->

### Phase Overview
<!-- @RULE: List phases with goals, not file-level details. Format:
- **Phase 1: <name>** — <goal, measurable deliverable>
- **Phase 2: <name>** — <goal, measurable deliverable>
-->

## C. Phased Approach
<!-- @REPLACE -->

<!-- @RULE: Phase-level breakdown. Each phase becomes a sub-change. Format:

### Phase 1: <name>
- **Sub-change**: <will be filled when sub-change created>
- **Goal**: <measurable deliverable>
- **Dependencies**: <what must complete before this phase>
- **Scope**: <which subsystems / modules affected>

### Coordination Notes
- <cross-phase dependencies, shared interfaces, integration points>
-->

## D. Blockers & Feedback
<!-- @REPLACE -->

<!-- @RULE: Record with dates. Format:
### Blocker (YYYY-MM-DD)
**Blocked**: <what> | **Needed**: <to unblock>

### PIVOT (YYYY-MM-DD)
<direction change and reason>
-->
