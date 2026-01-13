---
skill: sspec
version: 1.0.0
description: SSPEC workflow, status definitions, and best practices
---

# SSPEC Skill

## Purpose

Provide a single skill that explains how to run sspec workflows, manage status transitions, and maintain high-quality handovers.

## Workflow Guide

### Session Start Patterns

#### Pattern 1: Resume Existing Work
```
User: @resume
Agent:

1. Identifies active change (e.g., "add-dark-mode")
2. Reads handover.md → tasks.md → spec.md
3. Outputs: "Resuming add-dark-mode. Status: DOING. Progress: 3/7 tasks.
   Last session: Implemented toggle component.
   Next: Add theme persistence to localStorage."

```

#### Pattern 2: Switch Context
```
User: @change payment-refactor
Agent:

1. If exists → loads context
2. If not → creates change, prompts user to fill spec.md
3. Outputs context summary

```

### During Session

#### Task Execution
- Work through tasks.md sequentially
- Mark `[x]` only when fully complete and verified
- Add discovered tasks as `[ ]` immediately

#### When User Says `@argue`
**Scenario**: User objects to implementation approach

**Agent response**:
1. STOP coding immediately
2. Ask clarifying questions:
   - "Is this about implementation detail, design approach, or requirement misunderstanding?"
3. Analyze scope:
   - **Detail-level**: Update tasks.md, continue
   - **Design-level**: Update spec.md B/C, regenerate tasks.md
   - **Requirement-level**: Update spec.md A, may need full replanning
4. If major pivot → add `<!-- PIVOT: <date> <reason> -->` in spec.md
5. Get user confirmation before proceeding

### Session End

#### Handover Checklist
```
User: @handover
Agent updates:
✓ handover.md: Done / Now / Next / Key Files / Commands
✓ tasks.md: Mark completed, add discovered
✓ spec.md: Update status if changed (e.g., DOING → REVIEW)

Output: "Handover written. Status: REVIEW. 5/7 tasks done. Next session: final testing."
```

### After Autonomous Coding

**Scenario**: User used Claude Code / Copilot to implement features outside this session.
```

User: @sync
Agent:

1. Scans: git diff HEAD~5..HEAD (or file timestamps)
2. Identifies: which tasks were completed
3. Updates:
   - tasks.md: mark relevant tasks [x]
   - spec.md: update status if appropriate
   - handover.md: summarize what was done
4. Outputs: "Synced. Marked 3 tasks complete. Status unchanged (DOING)."

```

### Best Practices

#### Handover Quality
- **Bad**: "Worked on auth. Some progress."
- **Good**: "Implemented JWT validation middleware. Tests pass. Next: add refresh token logic."

#### Task Granularity
- Each task should be **<2 hours**
- Each task should have **verification criteria**
- Break down large tasks immediately

#### Status Transitions
- Only update status when milestone reached
- Document blockers in spec.md section D before setting BLOCKED
- Set REVIEW only when implementation complete and ready for user verification

#### PIVOT Handling
- Mark pivots explicitly in spec.md: `<!-- PIVOT: 2025-01-03 User changed auth from JWT to OAuth -->`
- Regenerate tasks.md after pivot
- Update handover.md with pivot reasoning

## Status Guide

### Change Status Definitions

#### PLANNING
**Meaning**: Defining scope, approach, and creating task plan.

**Agent actions**:
- Fill spec.md sections A, B, C
- Break down into tasks in tasks.md
- Get user approval before moving to DOING

**Exit criteria**:
- spec.md sections A-C complete
- tasks.md has executable tasks with verification
- User approves plan

---

#### DOING
**Meaning**: Implementation in progress.

**Agent actions**:
- Execute tasks from tasks.md
- Update progress regularly
- Update handover.md at session end

**Exit criteria**:
- All tasks marked `[x]`, OR
- Hit blocker → BLOCKED, OR
- Implementation complete → REVIEW

---

#### BLOCKED
**Meaning**: Waiting on external dependency or unresolved issue.

**Agent actions**:
- Document blocker in spec.md section D with:
  - What's blocked
  - Why (missing info, external dependency, technical limitation)
  - What's needed to unblock
- Do NOT continue implementation
- Update handover.md with blocker status

**Exit criteria**:
- Blocker resolved → back to DOING
- User decides to pivot → back to PLANNING

---

#### REVIEW
**Meaning**: Implementation complete, awaiting user verification.

**Agent actions**:
- Prepare demo or summary of changes
- Update handover.md with:
  - What was accomplished
  - How to verify
  - Known limitations

**Exit criteria**:
- User accepts → DONE
- User requests changes → back to DOING

---

#### DONE
**Meaning**: Completed and verified by user.

**Agent actions**:
- Final handover.md update
- Ready for complete the change

**Exit criteria**:
- User runs `sspec change archive <name>`

### Status Transitions

#### Allowed Transitions
```

PLANNING → DOING (plan approved)
DOING → BLOCKED (hit blocker)
DOING → REVIEW (implementation complete)
BLOCKED → DOING (blocker resolved)
BLOCKED → PLANNING (pivot needed)
REVIEW → DONE (user accepts)
REVIEW → DOING (user requests changes)
Any → PLANNING (major pivot)

```

#### Forbidden Transitions

- PLANNING → REVIEW (skip implementation)
- PLANNING → DONE (skip implementation + review)
- DOING → DONE (skip review)
- BLOCKED → DONE (unresolved blocker)

### Request Status

| Status | Meaning | Typical Action |
|--------|---------|----------------|
| OPEN | New request, not started | Triage, decide if/when to work |
| DOING | Linked to active change | Update via `sspec request <name> --link <change>` |
| DONE | Completed and delivered | Mark when change archived |

### Edge Cases

#### Multiple Changes in DOING
**Problem**: Context switching confusion.

**Solution**: Use `@change <name>` to explicitly switch. Update handover for previous change before switching.

#### BLOCKED but Can Work on Other Parts
**Problem**: Only part of change is blocked.

**Solution**: Break into separate changes. Keep blocked part as BLOCKED, move unblocked to new change.

#### REVIEW Takes Multiple Sessions
**Problem**: User needs time to verify.

**Solution**: Status stays REVIEW. Handover should note "Awaiting user verification" in Now section.

#### User Wants to Skip REVIEW
**Problem**: User trusts implementation, wants to mark DONE immediately.

**Solution**: Acceptable for small changes. Agent should still update handover with "User approved without formal review" note.
