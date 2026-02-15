---
name: {{CHANGE_NAME}}
status: PLANNING
type: ""
change-type: single
created: {{TIME}}
reference: null
---

<!-- @RULE: Frontmatter Schema
status: PLANNING | DOING | REVIEW | DONE | BLOCKED;
change-type: single | sub (sub if part of a root change);
reference?: Array<{source: str; type: RefType; note?}>;
type RefType: 'request' | 'root-change' | 'sub-change' | 'doc';
📚 Full schema details: sspec-change SKILL → doc-standards.md
 -->

# {{CHANGE_NAME}}

## A. Problem Statement
<!-- @REPLACE -->

<!-- @RULE: Quantify pain. Format: "[metric] causing [impact]".
Simple changes: single paragraph. Complex: split "Current Situation" + "User Requirement".
📚 Standards: sspec-change SKILL → doc-standards.md -->

## B. Proposed Solution
<!-- @REPLACE -->

<!-- @RULE: Design document — What & Why. Include interface design, data models, key logic.

Required:
- Approach: Core idea (1-3 paragraphs) + why this over alternatives
- Key Changes: Major modules/subsystems affected

Optional Sub-sections (use when applicable):
- ### Interface Design: Function signatures, class structures, API contracts
- ### Data Model: Core data types, state machines, data flow
- ### Key Logic: Pseudocode, edge cases, critical decision points

Complexity Scaling: Consult sspec-change SKILL

📚 Standards: sspec-change SKILL → doc-standards.md
-->

### Approach
<!-- Core idea + why this way -->

### Key Changes
<!-- Major modules, interfaces, dependencies -->

## C. Implementation Strategy
<!-- @REPLACE -->

<!-- @RULE: Execution plan — How to organize phases. Reference Section B's design, don't repeat it.

Content:
- Phase division: Break work into logical phases
- File scope per phase: Which files affected + brief what (not detailed how — that's tasks.md)
- Dependencies: What must complete first (if applicable)
- Risks & Mitigations: Technical risks + mitigation strategies

Format:
### Phase N: <name>
- `path/file.py` — create|modify, brief what
- Reference Section B design ("implement interface per B")

### Risks & Dependencies
- <external deps, risks, mitigation>

Complexity:
- single/sub: File-level mentions + brief what
- root: Milestone-level (one phase per sub-change, goal/scope/deps)

📚 Standards: sspec-change SKILL → doc-standards.md
-->

## D. Blockers & Feedback
<!-- @REPLACE -->

<!-- @RULE: Record with dates. Format:
### Blocker (YYYY-MM-DD)
**Blocked**: <what> | **Needed**: <to unblock>

### PIVOT (YYYY-MM-DD)
<direction change and reason>
-->
