---
name: sspec-change
description: "Change lifecycle — scale assessment, document standards, status transitions, multi-change coordination. Consult when creating, filling, reviewing, or transitioning changes."
metadata:
  author: frostime
  version: 1.0.0
---

# SSPEC Change Skill

Change lifecycle management. From scale assessment to archiving.

## Playbook

| You need to... | Action |
|----------------|--------|
| Decide if this needs a change | Assess Scale below |
| Create and fill spec.md / tasks.md | Read [doc-standards] |
| Set up multi-change structure | Read [multi-change] |
| Handle blockers, rejection, design loops | Edge Cases below |
| Check before PLANNING→DOING | Pre-Execution Checklist below |
| Check before DOING→REVIEW | Pre-Review Checklist below |
| Update handover.md during/after work | 📚 Consult `sspec-memory` SKILL |

---

## Assess Scale

**Micro** — ALL of: ≤3 files, ≤30min, no design decisions, trivially reversible.
→ Do directly or track in request file (`## Plan` / `## Done`). No change needed.

**Single** — ALL of: ≤1 week, ≤15 files in one subsystem, ≤20 tasks, low risk.
→ Standard change workflow. Fill spec.md / tasks.md / handover.md.

**Multi** — ANY of: >1 week, >15 files across subsystems, >20 tasks, high risk.
→ Root change (`--root`) + sub-changes. Read [multi-change](./references/multi-change.md) first.

**Uncertain?** Use `@ask` (`sspec ask create`) to consult user on splitting.

---

## Request → Change Flow

This is the most common workflow. Steps:

1. **Link**: `sspec change new --from <request>` (auto-links and derives name)
2. **Understand**: First-principles — find the real problem, not the surface ask
3. **Research**: Read `project.md` + relevant code + `spec-docs/`. If unclear → **`sspec ask create`**
4. **Design**:
   - Simple: Draft spec.md mentally, fill directly
   - Complex (multi-scale): **`sspec ask create`** about splitting → `sspec change new <n> --root`
   - Finalize: Distill into spec.md A/B/C. Follow [doc-standards](./references/doc-standards.md).
5. **Confirm**: **`sspec ask create`** to present plan. Wait for user approval.
6. **Execute**: Implement tasks. Update tasks.md after **each** task, not in batches.

**Principle**: Understand before acting. Wrong direction costs more than extra questions.

### CLI Commands (Agent-Driven)

These commands are designed for Agent autonomous execution:

| Command | When | Input Notes |
|---------|------|-------------|
| `sspec change new <name>` | Creating a new change | `<name>` is a slug, e.g. `auth-refactor` |
| `sspec change new --from <request>` | Creating from a request | `<request>` accepts name (fuzzy) or file path |
| `sspec change new <name> --root` | Multi-change root | Generates root templates (milestones, not file-tasks) |
| `sspec change find <name>` | Locating a change | Fuzzy match; returns path(s) |
| `sspec change list` | When can't locate change | Lists all active changes with status |
| `sspec change status` | Check progress | Auto-calculates from tasks.md checkboxes |

**Ergonomics**: `--from` is the most common path — Agent typically has a request to start from. The name derivation means Agent doesn't need to invent a name.

---

## Document Standards Summary

Templates use `@RULE` markers as inline reminders. The authoritative standards live in [doc-standards.md](./references/doc-standards.md).

### spec.md Quick Reference

| Section | Key Requirement |
|---------|----------------|
| A. Problem | Quantify impact: "[metric] causing [impact]" |
| B. Solution | Approach + rationale (why this over alternatives) |
| C. Implementation | File-level tasks with `path/file.py` — create\|modify, what |
| D. Blockers | Dated entries: "Blocker (YYYY-MM-DD): what \| needed" |

**Frontmatter**: `status` (PLANNING\|DOING\|REVIEW\|DONE\|BLOCKED), `change-type` (single\|sub\|root), `reference` (array of links to request/root/doc).

**Simple vs Complex**: For simple changes (≤5 files, clear scope), Section A can be a single paragraph, Section C can be a flat list. Don't over-structure small work.

### tasks.md Quick Reference

| Criterion | Standard |
|-----------|----------|
| Granularity | Each task <2h, independently testable |
| Verification | Each task/phase has explicit pass criteria |
| Progress | Update after completing **EACH** task |
| Phase Emoji | 🚧 in progress, ✅ done, ⏳ pending |

### handover.md

handover.md standards are owned by `sspec-memory` SKILL. But as a change author, remember:
- Fill Background on first session (write-once unless scope changes)
- Update "Accomplished" and "Next Steps" at minimum at session end
- Update "References & Memory" proactively during work
- 📚 Full handover quality guidance: Consult `sspec-memory` SKILL

---

## Edge Cases

### Partial Blockers

- Blocked tasks are dependencies for remaining → BLOCKED, document in spec.md D
- Blocked tasks are non-critical → Continue others, note in spec.md D
- Ambiguous → `@ask` or split into two changes

### REVIEW Across Sessions

Keep status REVIEW. Note "Awaiting review since \<date\>" in handover. Can start other work. Next session: prompt user for review first.

### Rejection (@argue)

AGENTS.md says STOP. Then assess scope of rejection:
- Implementation detail → update tasks.md only
- Design decision → revise spec.md B + regenerate tasks.md
- Requirement itself → revise spec.md A, mark PIVOT in D, transition DOING→PLANNING

### Multiple Active Changes

≤2 in DOING simultaneously. Switch: `@handover` current → `@change <other>` → read other's handover.

### Design Iteration Loop

spec.md keeps being revised → Archive current to `reference/spec-v1.md` → Brainstorm in `reference/` → Iterate via `@ask` → Write final to spec.md.

---

## Pre-Execution Checklist

Before transitioning PLANNING → DOING (user has approved):

- [ ] spec.md A: problem quantified?
- [ ] spec.md B: approach + rationale present?
- [ ] spec.md C: file-level tasks listed (single/sub) or phases listed (root)?
- [ ] tasks.md: each task <2h with pass criteria?
- [ ] spec.md reference field: linked to originating request?
- [ ] If sub-change: linked to root via `type: "root-change"`?

## Pre-Review Checklist

Before transitioning DOING → REVIEW:

- [ ] All tasks `[x]` in tasks.md?
- [ ] Verification criteria met per task?
- [ ] spec.md D: no undocumented blockers?
- [ ] Code tested and passing?
- [ ] Architecture change? → spec-doc updated?
- [ ] handover.md reflects completion state?
- [ ] tasks.md progress shows 100%?

---

## Anti-Patterns

| Bad | Correct |
|-----|---------|
| Skip spec.md, jump to coding | Fill A/B/C first — even brief is better than nothing |
| Mark `[x]` without testing | Done = coded **AND** verified |
| No file paths in spec.md C | List specific `path/file:function()` per task |
| Stay DOING when blocked | BLOCKED immediately + document in D |
| Skip REVIEW status | DOING → REVIEW → DONE, no shortcuts |
| Batch progress updates | Update tasks.md after **each** task |
| Create change for trivial fix | Micro: do directly or track in request |
| Start coding before `@ask` approval | Confirm plan first — wrong direction costs more |

---

## References

| When | Load |
|------|------|
| Filling or reviewing spec.md / tasks.md | [doc-standards.md](./references/doc-standards.md) |
| Setting up multi-change structure | [multi-change.md](./references/multi-change.md) |
| Filling or reviewing handover.md | 📚 `sspec-memory` SKILL |
