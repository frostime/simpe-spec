---
change: "behavior-contract-verification"
created: 2026-06-24T16:08:56
---

# Design: behavior-contract-verification

## Content Architecture

Single/sub-change `spec.md` target outline:

```text
# {{CHANGE_NAME}}

## Problem Statement

## Proposed Solution

### Approach

### Behavior Contract

### Implementation Changes

### Scope Summary

### Design Reference
```

Root-change `spec.md` target outline:

```text
# {{CHANGE_NAME}}

## Problem Statement

## Proposed Solution

### Overall Approach

### Behavior Contract

### Phase Overview

### Design Reference
```

Root behavior contract is phase-level. It describes cross-phase or final external
behavior boundaries. File-level and implementation-specific behavior contracts stay
in sub-change specs.

## Section Boundaries

| Section | Owns | Does not own |
|---------|------|--------------|
| `Problem Statement` | current problem and impact | implementation direction, tests |
| `Approach` | solution direction and rationale | detailed behavior clauses, task list |
| `Behavior Contract` | externally observable behavior boundaries | test commands, click-by-click verification, internal algorithms |
| `Implementation Changes` | changelog-style implementation items needed to satisfy `BC-*` | detailed design logic, phase progress |
| `Scope Summary` | affected files, change summary, rough effort | acceptance criteria, detailed task decomposition |
| `design.md` | interfaces, data structures, state machines, algorithms, migration strategy | problem restatement, task checklist |
| `tasks.md` | file-level tasks, agent verification, user checks | redefining behavior or design |

## Behavior Contract Pattern

Recommended pattern, not a forced table:

```markdown
### Behavior Contract

<!-- MUST define externally observable behavior boundaries caused by this change.
Use BC-1 / BC-2 labels when multiple behavior contracts exist.

For behavior-changing work, specify as relevant:
- Surface: CLI / UI / API / generated file / persisted data / Agent workflow / template output
- Before: current observable behavior
- After: required observable behavior
- Unchanged / Boundary: what must not change
- Error / compatibility behavior when relevant

Do NOT write test commands or click-by-click verification here.
Those belong in tasks.md Verification / User Check.
-->

**BC-1: <observable behavior title>**

Surface: <entry point the user or external caller can observe>.

Before:
- <current behavior>

After:
- <required behavior>

Unchanged:
- <boundary that must stay stable>
```

Pure internal/refactor-only pattern:

```markdown
**BC-1: External behavior preserved**

Surface: <public CLI/API/UI/workflow affected by the implementation area>.

After:
- No user-visible behavior change.
- Existing <named behavior> remains valid.
- Acceptance is based on regression checks listed in tasks.md.
```

## Implementation Changes Pattern

```markdown
### Implementation Changes

<!-- MUST label each independent implementation item with a unique
`type(scope): title` label.
Use changelog-style types such as feat, fix, refactor, docs, test, chore, build,
perf, or add when that is clearer for the project.
Each item states what implementation surface changes and which Behavior Contract it serves.
tasks.md references these labels.
Do NOT duplicate design.md technical detail here.
-->

**feat(scope): <implementation item>** - <short change summary>.

Serves: BC-1, BC-2.
```

Rationale for renaming from `Key Change`:

| Name | Problem |
|------|---------|
| `Key Change` | ambiguous after behavior contracts exist; could mean behavior or implementation |
| `Code Change` | too narrow for templates, docs, config, tests, generated files |
| `Implementation Changes` | covers code and non-code implementation surfaces; pairs cleanly with `Behavior Contract` |

Label examples:

| Label | Useful for |
|-------|------------|
| `feat(spec-template): Add Behavior Contract` | new template/protocol capability |
| `refactor(skill-design): Rename Key Change references` | structural/terminology cleanup |
| `test(templates): Assert generated headings` | verification-only work |
| `docs(examples): Refresh plan examples` | example or documentation updates |

## Scope Summary Pattern

```markdown
### Scope Summary

<!-- MUST end every single/sub spec with a File | Change | Effort table.
Effort is a rough design-stage estimate, not an acceptance criterion.
Use: XS trivial/local | S localized | M multi-file or coordination needed | L cross-module, risky, or migration-heavy.
-->

| File | Change | Effort |
|------|--------|--------|
| `path/file` | feat(scope): <change summary> | S |
```

Root specs keep phase-level scope. They should not use file-level scope tables unless
the existing root template explicitly requires phase coordination detail.

## tasks.md Verification Pattern

Generated template guidance should allow this shape:

```markdown
**Verification**:
- Agent: <test/build/lint/CLI command and expected result>
- Agent: <additional automated or sandbox check>

**User Check**:
1. BC-1: <user action> -> <expected observable result>
2. BC-2: <user action> -> <expected observable result>
```

Rules:

| Case | Requirement |
|------|-------------|
| User-visible behavior changes | `User Check` SHOULD be present and reference `BC-*` |
| Behavior boundary/default/error/compatibility changes | `User Check` SHOULD be present unless impractical; if omitted, explain why in Verification |
| Pure internal/refactor-only change | `User Check` MAY be omitted when `Behavior Contract` states no user-visible behavior change |
| Root change | milestones carry deliverables; detailed checks live in sub-change tasks |

## Lifecycle Trace

```text
Clarify
  -> success criteria and user-owned constraints
Design
  -> spec.md Behavior Contract (BC-*)
  -> spec.md Implementation Changes (`type(scope): title` labels)
  -> @align gate includes BC-* before planning
Plan
  -> tasks reference BC-* and implementation labels
  -> Verification = agent checks
  -> User Check = black-box review steps
Implement
  -> run verification before marking tasks done
  -> final @align includes verification results and User Check recipe
Review
  -> user feedback that changes BC-* or adds acceptance conditions is amend/revision
```

## Validation and Compatibility

Current code validation only checks that the new spec structure has `## Problem Statement`
and `## Proposed Solution`; it does not parse `### Key Change`. Renaming the section is
therefore a template/test update, not a parser migration.

Required verification:

| Layer | Check |
|-------|-------|
| Template structure | tests assert generated spec includes `### Behavior Contract`, `### Implementation Changes`, and `File | Change | Effort` |
| Skill docs | examples and section-boundary tables no longer reference `Key Change` except in migration/rationale text |
| CLI sandbox | `sspec project init` and `sspec change new` generate the new template structure |
| Self-host sync | after template edit, run `uv pip install -e .` then `uv run sspec project update` per project protocol |
