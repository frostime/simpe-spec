---
name: {{CHANGE_NAME}}
status: PLANNING
type: ""
change-type: single
created: {{TIME}}
reference: null
---

<!-- @RULE: Frontmatter
status: PLANNING | DOING | REVIEW | DONE | BLOCKED
change-type: single | sub
reference?: Array<{source, type: 'request'|'root-change'|'sub-change'|'doc', note?}>
-->

# {{CHANGE_NAME}}

## A. Problem Statement
<!-- @REPLACE -->

<!-- @RULE: Quantify impact. Format: "[metric] causing [impact]".
Simple: single paragraph. Complex: split "Current Situation" + "User Requirement". -->

## B. Proposed Solution
<!-- @REPLACE -->

### Approach
<!-- Core idea (1-3 paragraphs) + why this over alternatives -->

### Key Design
<!-- Interfaces, data models, key logic — scale by complexity:
Simple (≤5 files): inline in Approach, brief mention
Medium (5-15 files): dedicated sub-sections (### Interface, ### Data Model)
Complex (>15 files): detailed design here or in reference/design.md -->
