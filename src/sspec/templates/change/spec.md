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

### Behavior Contract
<!-- MUST define externally observable behavior boundaries caused by this change.
Use BC-1 / BC-2 labels when multiple behavior contracts exist.

For behavior-changing work, specify as relevant:
- Surface: CLI / UI / API / generated file / persisted data / Agent workflow / template output
- Before: current observable behavior
- After: required observable behavior
- Unchanged / Boundary: what must not change
- Error / compatibility behavior when relevant

For internal/refactor-only work, state that user-visible behavior is unchanged and name the external behavior scope to preserve.
Do NOT write test commands or click-by-click verification here. Those belong in tasks.md Verification / User Check.
Fence nesting: when showing content containing ```, outer fence MUST use more backticks (outer > inner). -->

### Implementation Changes
<!-- MUST label each independent implementation item with a unique `type(scope): title` label.
Examples: **feat(cli): Add tag filter** / **fix(parser): Handle empty frontmatter** / **refactor(service): Extract cache adapter**.
Allowed type vocabulary is project-local; common types include feat, fix, refactor, docs, test, chore, build, perf, add.
Each item states what implementation surface changes and which Behavior Contract it serves.
tasks.md references these labels — MUST NOT copy the design description.
If scope boundary is unclear, add a "What Stays Unchanged" block after Scope Summary. -->

### Scope Summary
<!-- MUST end every single/sub spec with a File | Change | Effort table.
Effort is a rough design-stage estimate, not an acceptance criterion.
Use: XS trivial/local | S localized | M multi-file or coordination needed | L cross-module, risky, or migration-heavy. -->

### Design Reference
<!-- MUST create design.md when the change involves new interfaces, data model changes,
or architectural logic changes. Link here: See [design.md](./design.md)
Simple changes MAY delete this section and describe the technical approach inline. -->
