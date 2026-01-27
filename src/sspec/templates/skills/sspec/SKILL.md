---
skill: sspec
version: 2.0.0
description: |
  Deep reference for SSPEC workflow: status definitions, transition rules,
  quality standards, and edge case handling. Consult when AGENTS.md Quick
  Reference is insufficient—especially for status ambiguity, blocked scenarios,
  or handover quality issues.
---

# SSPEC Skill

**When to read this SKILL**:
- Uncertain which status a change should be in
- Transition seems ambiguous (e.g., "partially blocked")
- Writing handover and unsure what quality bar to hit
- Handling unusual scenarios not covered in AGENTS.md

For everyday workflow, AGENTS.md suffices. This SKILL is the deep reference.

---

## Status Definitions (Detailed)

### PLANNING

**What it means**: Scope and approach are being defined. No implementation yet.

**Entry conditions**:
- New change created via `sspec change new <name>`
- Major pivot from any other status (direction fundamentally changed)

**Agent responsibilities**:
1. Fill spec.md sections:
   - **A. Problem Statement**: What problem? Why now? What's the impact?
   - **B. Proposed Solution**: High-level approach, key design decisions
   - **C. Implementation Strategy**: Phases, risks, dependencies
2. Break down into tasks in tasks.md:
   - Each task < 2 hours
   - Include verification criteria
3. **Wait for explicit user approval** before transitioning

**Exit criteria** (ALL must be true):
- [ ] spec.md sections A, B, C are complete
- [ ] tasks.md has executable tasks with verification criteria
- [ ] User explicitly says "approved" / "looks good" / "let's proceed"

**Common mistake**: Starting implementation before user approves plan.

---

### DOING

**What it means**: Active implementation in progress.

**Entry conditions**:
- User approved plan (from PLANNING)
- Blocker resolved (from BLOCKED)
- Changes requested (from REVIEW)

**Agent responsibilities**:
1. Execute tasks sequentially (unless parallelizable)
2. Mark tasks `[x]` **immediately** when done—not in batches
3. Update handover.md at every session end
4. If scope creep detected, pause and discuss with user

**Exit criteria** (one of):
- All tasks complete → **REVIEW**
- External dependency blocks progress → **BLOCKED**
- User requests fundamental pivot → **PLANNING**

**Common mistakes**:
- Marking multiple tasks done at once (loses granularity)
- Continuing when blocked instead of stopping
- Skipping handover because "almost done"

---

### BLOCKED

**What it means**: Cannot proceed without external input or resolution.

**Entry conditions**:
- Missing information only user can provide
- Waiting on external system/API/approval
- Technical issue requiring investigation beyond current scope

**Agent responsibilities**:
1. **STOP implementation** (do not attempt workarounds without permission)
2. Document clearly in spec.md section D:
   - What is blocked
   - Why it's blocked
   - What's needed to unblock
3. Update handover.md with blocker status
4. Suggest alternatives if any exist

**Exit criteria**:
- Blocker resolved → **DOING**
- User decides to pivot → **PLANNING**

**Quality standard for blocker documentation**:

❌ **Bad**: "Blocked on API"

✅ **Good**: "Blocked on payment API credentials. Need: 1) Stripe test API key, 2) Webhook secret. Without these, cannot test checkout flow. Workaround: mock API responses (loses integration coverage)."

---

### REVIEW

**What it means**: Implementation complete, awaiting user verification.

**Entry conditions**:
- All planned tasks marked `[x]`

**Agent responsibilities**:
1. Summarize what was accomplished
2. Provide verification steps (how user can test)
3. Note any known limitations or follow-up items
4. Update handover.md

**Exit criteria**:
- User accepts → **DONE** (then `sspec change archive <name>`)
- User requests changes → **DOING**

**Important**: Status stays REVIEW until user explicitly responds. Do not auto-proceed.

---

### DONE

**What it means**: Completed and verified.

**Entry conditions**:
- User accepted in REVIEW

**Next action**: User runs `sspec change archive <name>` to move to archive.

---

## Transition Rules

### Allowed Transitions

```
PLANNING → DOING       # User approves plan
DOING    → BLOCKED     # Hit external blocker
DOING    → REVIEW      # All tasks complete
DOING    → PLANNING    # Major pivot (user requests)
BLOCKED  → DOING       # Blocker resolved
BLOCKED  → PLANNING    # Pivot while blocked
REVIEW   → DONE        # User accepts
REVIEW   → DOING       # User requests changes
Any      → PLANNING    # Major pivot at any time
```

### Forbidden Transitions (and why)

| Forbidden | Reason |
|-----------|--------|
| PLANNING → REVIEW | Can't review without implementation |
| PLANNING → DONE | Can't complete without work |
| DOING → DONE | Must go through REVIEW (verification matters) |
| BLOCKED → DONE | Can't finish with unresolved blocker |
| BLOCKED → REVIEW | Unblocking means more work, not review |

---

## Quality Standards

### Handover Quality

The handover is the **only memory** between sessions. Quality directly impacts next session's efficiency.

**The 30-Second Test**: Can the next Agent start productive work within 30 seconds of reading handover.md?

#### Comparison

❌ **Failing handover**:
```markdown
## Session 3
Worked on auth. Made some progress. Still have stuff to do.
```
Problems: No specifics, no file references, no next steps.

✅ **Passing handover**:
```markdown
## Session 3 - 2026-01-27 14:30

### Background
Implementing JWT-based authentication for the API (change: auth-system).

### Accomplished
- Completed JWT validation middleware in `src/auth/jwt.py`
- Added token refresh endpoint at `/api/auth/refresh`
- Unit tests pass (12/12)

### Current Status
DOING - 7/10 tasks complete (70%)

### Next Steps
1. Implement logout (token blacklist) in `src/auth/logout.py`
2. Add rate limiting to auth endpoints
3. Write integration tests for full auth flow

### Conventions
- All auth errors return 401 with `{"error": "...", "code": "AUTH_XXX"}`
- Tokens expire in 15min (access) / 7d (refresh)
```

---

### Task Granularity

Each task MUST be:
- **Completable in < 2 hours**: If longer, break it down
- **Verifiable**: Include how to know it's done
- **Atomic**: Can be marked done independently

#### Examples

❌ **Too large**: "Implement authentication system"

✅ **Properly granular**:
```markdown
- [ ] Create JWT validation middleware (verify: unit test passes)
- [ ] Add login endpoint POST /auth/login (verify: returns token)
- [ ] Add token refresh endpoint (verify: extends session)
- [ ] Implement logout with token blacklist (verify: old token rejected)
```

---

### PIVOT Handling

When user fundamentally changes direction mid-implementation:

1. **Add PIVOT marker** in spec.md:
   ```markdown
   <!-- PIVOT: 2026-01-27 - Changed from REST to GraphQL per user request -->
   ```

2. **Regenerate tasks.md**: Old tasks may be invalid

3. **Document in handover.md**: Why the pivot happened, what was salvaged

4. **Reset status to PLANNING** if scope changed significantly

---

## Edge Cases

### Multiple Changes in DOING

**Problem**: Only one change should be DOING at a time—context switching causes errors.

**Solution**:
1. Before switching, run `@handover` on current change
2. Use `@change <other>` to switch explicitly
3. System should warn if multiple DOING detected

### Partially BLOCKED

**Problem**: Part of change is blocked, but other parts can continue.

**Solutions** (choose based on situation):
1. **Split the change**: Create new change for unblocked work, keep blocked portion as BLOCKED
2. **Reorder tasks**: If blocked task isn't critical path, move to end and continue
3. **Document and continue**: If block is minor, note in spec.md and proceed with workaround

### REVIEW Spans Multiple Sessions

**Problem**: User needs days to verify; Agent sessions happen in between.

**Solution**:
- Status stays REVIEW
- Handover notes: "Awaiting user verification since <date>"
- Agent does NOT proceed until user responds
- Can work on other changes in meantime

### User Wants to Skip REVIEW

**Problem**: User trusts implementation, wants to go directly to DONE.

**Solution**:
- Acceptable for **small, low-risk changes** only
- Document in handover: "User approved without formal review"
- Still run `sspec change archive <name>` to complete lifecycle

### Disagreement During Implementation

**Problem**: User says "that's not what I wanted" mid-implementation.

**Solution**:
1. STOP immediately (don't continue hoping to fix later)
2. Use `@argue` flow to clarify scope
3. Update spec.md/tasks.md based on clarification
4. Get explicit approval before resuming

---

## Request Lifecycle

Requests are lightweight incoming work items, tracked separately from changes.

| Status | Meaning | Transition |
|--------|---------|------------|
| **OPEN** | New request, not started | Triage and prioritize |
| **DOING** | Linked to active change | `sspec request <name> --link <change>` |
| **DONE** | Delivered | When linked change is archived |

**Best practice**: Convert requests to changes for anything taking >2 hours.

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Correct Approach |
|--------------|--------------|------------------|
| Skipping handover "because session was short" | Next session has no context | Always handover, even if brief |
| Marking tasks done without testing | False progress, bugs later | "Done" means complete AND verified |
| Staying in DOING when blocked | Wastes time on workarounds | Transition to BLOCKED, document clearly |
| Auto-transitioning to DONE | Skips user verification | Always go through REVIEW |
| Multiple changes in DOING | Context confusion | Handover first change before switching |
| Vague spec.md | Tasks become unclear | Invest time in clear problem/solution |

---

## Quick Diagnostic

**"What status should this be?"**

```
Is scope/approach still being defined? → PLANNING
Are you actively implementing? → DOING
Are you waiting on something external? → BLOCKED
Is all planned work complete? → REVIEW
Did user accept and archive? → DONE
```

**"Should I transition status?"**

```
Can you make progress right now without user input?
  YES → Stay in DOING
  NO, need clarification → Stay in DOING, ask user
  NO, need external resource → BLOCKED

Are ALL tasks done?
  YES → REVIEW
  NO → Stay in DOING
```
