# sspec/pivot

Record a direction change when user changes their mind.

## Triggers

User says things like:
- "wait", "actually", "hold on"
- "change of plans", "let's do X instead"
- "forget that, let's..."
- "I changed my mind"

## Workflow

1. **Stop** current work immediately
   - Don't continue with the old plan
   - Don't try to "finish this first"

2. **Confirm** new intent
   - "You want to [new direction], correct?"
   - Ask clarifying questions if new direction is vague
   - Ensure you understand WHY the change

3. **Record** in `tasks.md` under `## Pivot`:
   ```markdown
   ### [timestamp]
   - Previous: [what was planned]
   - New: [new direction]
   - Reason: [user's reasoning]
   ```
   
   Use current timestamp if available, otherwise use "[date unknown]".

4. **Update** the Plan section:
   - Mark abandoned items with `~~strikethrough~~` or remove
   - Add new items for the new direction
   - Reorder priorities as needed

5. **Adjust** Status if appropriate:
   - Major pivot → may need to go back to `PLANNING`
   - Minor adjustment → stay in `IN_PROGRESS`

6. **Acknowledge** the change:
   ```
   Recorded pivot from [old] to [new].
   Updated plan with [N] new tasks.
   Ready to proceed with [first new task]?
   ```

## Guidelines

- **Don't delete history** — pivots are valuable context for future understanding
- **Don't judge** — users change their minds for good reasons
- **Ask questions** if the new direction seems incomplete
- **Consider impact** on other related work or dependencies

## Anti-patterns

❌ Continuing with old plan while "noting" the change
❌ Merging old and new approaches without explicit decision
❌ Deleting the pivot record after completing new direction
❌ Not confirming understanding before proceeding
