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

### Approach
<!-- @RULE: Core idea (1-3 paragraphs) + why this over alternatives -->

### Key Changes
<!-- @RULE: List major changes: modules, interfaces, dependencies -->

## C. Implementation Strategy
<!-- @REPLACE -->

<!-- @RULE: File-level breakdown. Format:
### Phase N: <n>
- `path/file.py` — create|modify, <what>

### Risks & Dependencies
- <external deps, risks, mitigation>
📚 Standards: sspec-change SKILL → doc-standards.md -->

## D. Blockers & Feedback
<!-- @REPLACE -->

<!-- @RULE: Record with dates. Format:
### Blocker (YYYY-MM-DD)
**Blocked**: <what> | **Needed**: <to unblock>

### PIVOT (YYYY-MM-DD)
<direction change and reason>
-->
