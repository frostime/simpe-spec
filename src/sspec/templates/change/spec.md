---
name: {{CHANGE_NAME}}
status: PLANNING
change-type: single
created: {{TIME}}
reference: null
---

<!-- MUST follow frontmatter schema:
status: PLANNING | DOING | REVIEW | DONE | BLOCKED
change-type: single | sub
reference?: Array<{source, type: 'request'|'root-change'|'sub-change'|'prev-change'|'doc'|'revision', note?}>

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
    note: "Follow-up to <change-name>."
-->

# {{CHANGE_NAME}}

## Problem Statement

<!-- Quantify impact. Format: "[metric] causing [impact]".
Simple: single paragraph. Complex: split into "Current state" + "User need". -->

## Proposed Solution

### Approach
<!-- Core solution (1-3 paragraphs) + why this approach over alternatives -->

### Key Change
<!-- MUST label each independent change item as **Type Label: Title**.
Examples: **Fix A: Request linking** / **Feat B: Cache TTL jitter**
tasks.md references these labels — MUST NOT copy the design description.
If scope boundary is unclear, add a "What Stays Unchanged" block after Scope Summary.
Fence nesting: when showing content containing ```, outer fence MUST use more backticks (outer > inner). -->

### Scope Summary
<!-- MUST end every spec with a File | Change table. -->

### Design Reference
<!-- MUST create design.md when the change involves new interfaces, data model changes,
or architectural logic changes. Link here: → See [design.md](./design.md)
Simple changes MAY delete this section and describe the technical approach inline. -->
