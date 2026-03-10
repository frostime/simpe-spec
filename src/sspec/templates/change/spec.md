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

# {{CHANGE_NAME}}

## A. Problem Statement
<!-- @REPLACE -->

<!-- @RULE: Quantify impact. Format: "[metric] causing [impact]".
Simple: single paragraph. Complex: split "Current Situation" + "User Requirement". -->

## B. Proposed Solution
<!-- @REPLACE -->

<!-- @RULE: Accepted review-stage changes belong here as formal design.
If user feedback changes the current change's scope/design and the work still belongs to this change,
update A/B directly instead of leaving the accepted change only in handover.md.
If review history matters, add `### Review Amendments` under B as part of the design. -->

### Approach
<!-- Core idea (1-3 paragraphs) + why this over alternatives -->

### Key Design
<!-- Interfaces, data models, key logic — scale by complexity:
Simple (≤5 files): inline in Approach, brief mention
Medium (5-15 files): dedicated sub-sections (### Interface Design, ### Data Flow, ### Key Logic)
Complex (>15 files): detailed design here or in reference/design.md

Presentation Rules (see SKILL.md for full examples):
Rule 1: interfaces/types → typed code block (not prose)
Rule 2: data flow → ASCII tree (`│ ├── └──` notation) + explanatory text
Rule 3: ≥3 files → Scope Summary Table at end (| File | Change |)
Rule 4: ≥3 independent items → label each (Fix A / Feat B / Refactor C…) -->
