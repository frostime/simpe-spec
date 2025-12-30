# {{CHANGE_NAME}}

STATUS::PLANNING
<!-- STATUS values: PLANNING | IN_PROGRESS | BLOCKED | REVIEW | DONE -->

## Why

<!--
What problem does this solve? Why is it needed?
Write 1-2 sentences MAX — this is the anchor that doesn't change.

❌ Bad:
"Add a feature to improve the system"

✅ Good:
"Users report login timeout after 15 minutes, forcing re-authentication mid-workflow. Need session extension."
-->

## What

<!--
Specific code-level changes. Not abstract goals.

❌ Bad:
- Improve user experience
- Make it faster
- Add security

✅ Good:
- Add `extendSession()` method to AuthService
- Update SessionManager to refresh token 2 minutes before expiry
- Add "Keep me signed in" checkbox to LoginForm
- Store session preference in localStorage
-->

-

## Tasks

<!--
Each task should be:
1. Verifiable (clear "done" state)
2. Small grain (completable in one focused session)
3. Ordered (by dependency)

Mark parallelizable tasks with [P]

❌ Bad:
- [ ] Implement session extension
- [ ] Add UI
- [ ] Test it

✅ Good:
- [ ] 1. Add extendSession() to AuthService (returns Promise<Token>)
- [ ] 2. Add SessionManager class with auto-refresh timer
- [ ] 3. Wire SessionManager to call extendSession() at 13min mark
- [ ] 4. [P] Add "Keep signed in" checkbox to LoginForm UI
- [ ] 5. Test: manually set expiry to 2min, verify auto-refresh
-->

- [ ] 1.
- [ ] 2.
- [ ] 3.

## Progress

<!--
Reverse chronological (latest on top).
Format: [YYYY-MM-DD] What was accomplished (be specific!)

✅ Good examples:
[2025-01-15] Completed SessionManager class, added Jest tests (8/8 passing)
[2025-01-14] Implemented extendSession() in AuthService, returns new JWT
[2025-01-13] Created localStorage utilities: get/setSessionPreference()

❌ Bad examples:
[2025-01-15] Continued working on the feature
[2025-01-14] Fixed some bugs
[2025-01-13] Made progress
-->

## Decisions

<!--
Important decisions with rationale.
Format: [YYYY-MM-DD] Decision — Why

Example:
[2025-01-15] Use localStorage over cookies — Cookies have cross-domain issues, this feature doesn't need server access

**PIVOT format** (direction changes — NEVER DELETE THESE):
[YYYY-MM-DD] PIVOT
- From: [original plan]
- To: [new direction]
- Reason: [why changed]
- What was tried: [optional - what didn't work]

Example:
[2025-01-14] PIVOT
- From: Auto-refresh every 10 minutes
- To: Auto-refresh 2 minutes before expiry
- Reason: Fixed refresh wastes API calls; users with 8hr sessions don't need 48 refreshes
- What was tried: Implemented 10min timer, realized it's inefficient
-->

## Notes

<!--
Temporary scratchpad: research notes, code snippets, links, half-formed ideas.

Clean up at session end:
- Important findings → Move to Decisions or knowledge/
- Useful code → Extract to actual codebase
- Obsolete notes → Delete

This section should NOT accumulate indefinitely.
-->

---

<!--
SPEC.MD USAGE GUIDELINES:

Purpose: Single source of truth for this change.

What belongs in each section:
- Why/What: The unchanging goal and scope
- Tasks: The current plan (adjustable)
- Progress: Historical log of what was done
- Decisions: Key choices and direction changes (PIVOTs)
- Notes: Temporary exploration (clean up regularly)

Don't create separate files for:
- Meeting notes → Summary goes in Decisions
- Research findings → Goes in Notes, then Decisions or knowledge/
- Task breakdown → Goes in Tasks section

Update frequency:
- Tasks: When plan changes
- Progress: After completing each task
- Decisions: When making important choices or PIVOTs
- Notes: During research/exploration
-->
