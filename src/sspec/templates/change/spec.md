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
<!-- Scale-aware guidance (see SKILL.md):
- Simple (<=3 files): keep Key Design inline in Approach unless a dedicated sub-section materially helps
- Medium (4-15 files): choose 1-4 predictability dimensions as sub-sections
- Complex (>15 files): keep B as an executive summary; move full detail to `reference/design.md`

Ask: what does the user need to predict to feel in control of this change?
Browse dimensions: `sspec howto list --type design-dimension`
Read the chosen dimension HOWTO(s) before drafting.

Universal rules:
- ≥3 files → end with Scope Summary table (| File | Change |)
- ≥3 independent items → label each (Fix A / Feat B / Refactor C…)
- If scope boundaries are non-obvious, add a short `What Stays Unchanged` block.

Dimension-specific writing norms are in each dimension's howto. -->
