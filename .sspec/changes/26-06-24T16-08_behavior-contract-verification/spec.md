---
name: behavior-contract-verification
status: DOING
change-type: single
created: 2026-06-24T16:08:56
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

# behavior-contract-verification

## Problem Statement

Current sspec design requires the user to predict outcome before implementation, and
`tasks.md` requires phase-level verification. The protocol does not define a stable
place for external behavior boundaries or a separate user black-box review path. As
a result, behavior-changing work can reach Review with tests listed but without a
clear answer to: "what surface changed, what stayed unchanged, and how can the user
check the final result?"

## Proposed Solution

### Approach

Introduce a lightweight behavior contract into the change specification. The
contract defines externally observable behavior boundaries: before/after behavior,
unchanged boundaries, compatibility and error behavior when relevant. Keep concrete
test commands and click-by-click checks in `tasks.md`, under verification and user
check sections.

Use the target spec order:

```text
Problem Statement
Proposed Solution
  Approach
  Behavior Contract
  Implementation Changes
  Scope Summary
  Design Reference
```

Rename `Key Change` to `Implementation Changes`. After `Behavior Contract` exists,
`Key Change` becomes ambiguous: it could mean behavior change or implementation
change. `Implementation Changes` states the intended role directly and still covers
code, templates, docs, config, tests, and other implementation surfaces.

Implementation items use changelog-style labels: `type(scope): title`. Examples:
`feat(spec-template): Add Behavior Contract`, `refactor(skill-design): Rename Key
Change references`, `test(templates): Assert generated headings`. The label must be
unique inside the spec and stable enough for `tasks.md` references.

### Behavior Contract

**BC-1: Change specs define behavior boundaries before implementation**

Surface: generated single/sub-change `spec.md`.

After:
- `spec.md` contains `### Behavior Contract` after `### Approach`.
- The section defines external behavior boundaries, not test commands or user
  operation steps.
- Behavior-changing work uses labeled `BC-*` entries when more than one boundary
  exists.
- Internal/refactor-only work states that user-visible behavior is unchanged and
  names the external behavior scope that must be preserved.

**BC-2: Design alignment shows the user-visible contract**

Surface: `sspec-design` hard gate.

After:
- The design gate presents the behavior contract alongside problem, approach,
  implementation changes, scope, and risks.
- The user can reject or revise expected behavior before task planning begins.

**BC-3: Planning separates agent verification from user checks**

Surface: generated `tasks.md` and `sspec-plan`.

After:
- Phase verification states agent-run checks such as tests, lint, build, CLI
  sandbox commands, and expected outputs.
- Behavior-changing work also includes `User Check` steps that reference `BC-*`
  entries and state user action plus expected observable result.
- Pure internal changes may omit `User Check` when the behavior contract explicitly
  states no user-visible behavior change.

**BC-4: Implementation completion gives a review recipe**

Surface: `sspec-implement` exit gate.

After:
- The implementation-complete align message includes agent verification results.
- If `tasks.md` contains `User Check`, the align message includes the user review
  steps and expected observable results.

**BC-5: Scope summaries expose rough implementation cost**

Surface: single/sub-change `spec.md` scope summary.

After:
- Scope summary uses `File | Change | Effort`.
- `Effort` is a rough design-stage estimate, not an acceptance criterion.
- Allowed values are `XS`, `S`, `M`, `L`.

### Implementation Changes

**feat(spec-template): Add Behavior Contract structure** - Update single/sub-change
`spec.md` template to add `Behavior Contract`, rename `Key Change` to
`Implementation Changes`, and add `Effort` to `Scope Summary`. Update root spec
with a root-level behavior contract that stays phase-level, not file-level.

Serves: BC-1, BC-5.

**feat(skill-design): Require behavior contract alignment** - Update `sspec-design`
to define the new spec sections, require behavior contract presentation at the
design gate, and update the spec/design/tasks boundary table.

Serves: BC-1, BC-2.

**feat(plan): Split verification from user checks** - Update `sspec-plan` and
`tasks.md` template so phase verification can distinguish agent checks from user
black-box checks and reference `BC-*` plus implementation labels.

Serves: BC-3.

**feat(implement): Include review recipe at completion** - Update `sspec-implement`
so the final align includes verification results and user review steps. Update
`sspec-review` classification examples so new acceptance conditions or user-visible
behavior still trigger amend/revision.

Serves: BC-4.

**test(examples): Demonstrate and assert the new structure** - Update design/plan
examples and template tests so the new structure is demonstrated and mechanically
checked.

Serves: BC-1, BC-2, BC-3, BC-5.

### Scope Summary

| File | Change | Effort |
|------|--------|--------|
| `src/sspec/templates/change/spec.md` | feat(spec-template): add `Behavior Contract`; rename `Key Change`; add `Effort` column guidance | S |
| `src/sspec/templates/change-root/spec.md` | feat(spec-template): add root-level behavior contract guidance without file-level detail | S |
| `src/sspec/templates/change/tasks.md` | feat(plan): add optional `User Check` guidance and clarify verification semantics | S |
| `src/sspec/templates/skills/sspec-design/SKILL.md` | feat(skill-design): update spec section contract, boundaries, design gate requirements | M |
| `src/sspec/templates/skills/sspec-plan/SKILL.md` | feat(plan): distinguish agent verification and user checks | S |
| `src/sspec/templates/skills/sspec-implement/SKILL.md` | feat(implement): require final review recipe at implementation-complete gate | S |
| `src/sspec/templates/skills/sspec-review/SKILL.md` | feat(implement): keep acceptance-condition/user-visible feedback classified as amend | XS |
| `src/sspec/templates/skills/sspec-design/examples-*.md` | test(examples): update examples from `Key Change` to behavior contract + implementation changes | M |
| `src/sspec/templates/skills/sspec-plan/examples.md` | test(examples): show `Verification` plus `User Check` mapping to `BC-*` | M |
| `tests/` | test(templates): update template structure assertions and add coverage for new headings/table | S |

### Design Reference

See [design.md](./design.md).
