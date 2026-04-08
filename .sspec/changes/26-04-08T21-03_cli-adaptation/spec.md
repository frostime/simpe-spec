---
name: cli-adaptation
status: DONE
change-type: sub
created: 2026-04-08T21:03
reference:
  - source: ".sspec/changes/26-04-08T17-37_sspec-vnext"
    type: "root-change"
    note: "Phase 4: CLI Adaptation"
---

# cli-adaptation

## Problem Statement

`change new` creates 3 files (spec+tasks+handover) upfront. Per D3 decision, only spec.md + handover.md should be base files. Agent needs a way to lazy-create tasks.md, design.md, and revision files with proper template variables and @RULE guidance.

Additionally, `validate_change()` checks for old spec structure (`## A.` / `## B.` / `## C.`) which no longer exists in the new template.

## Proposed Solution

### Approach

Add `sspec change scaffold` subcommand for lazy file creation. Modify `change new` to create only base files by default, with `--scaffold` option for additional files at creation time.

### Key Change

**Adapt A: Minimal base creation** — `change new` creates only spec.md + handover.md by default.

**Adapt B: `--scaffold` option** — `change new --scaffold tasks,design` adds files at creation time.

**Adapt C: `scaffold` subcommand** — `sspec change scaffold <type> <change>` for lazy creation. Types: spec, tasks, design, revision. Prevents overwrite. Root changes reject design/revision.

**Adapt D: validate update** — Replace `## A.`/`## B.`/`## C.` checks with new spec structure. Make tasks.md optional.

**Adapt E: Output messages** — Update `new` command output to reflect minimal creation.

### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/core.py` | Replace `CHANGE_TEMPLATE_FILES` with `CHANGE_BASE_FILES` + scaffold constants |
| `src/sspec/services/change_service.py` | Modify `create_change()`, add `scaffold_change_file()`, update `validate_change()` |
| `src/sspec/commands/change.py` | Add `scaffold` subcommand, add `--scaffold` to `new`, update output |
| `src/sspec/templates/skills/sspec-plan/SKILL.md` | Add scaffold command reference |
| `src/sspec/templates/skills/sspec-design/SKILL.md` | Add scaffold command reference |
| `src/sspec/templates/skills/sspec-review/SKILL.md` | Add scaffold command reference |
