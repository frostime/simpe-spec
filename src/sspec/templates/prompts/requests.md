# /requests

Review open user requests and propose actions.

## Workflow

1. **List** open requests:
   ```bash
   sspec request --list
   ```

2. **Read** each open request in `.sspec/requests/`

3. **For each request**, suggest one of:
   - Create a new change: `/propose <name>`
   - Link to existing change: Update request frontmatter
   - Ask clarifying questions
   - Mark as duplicate/invalid

4. **Update** request status as you process them

## Output

```
## Open Requests Review

### 1. add-dark-mode (2025-01-15)
Summary: User wants dark mode with system preference detection
Recommendation: Create new change
Action: /propose dark-mode

### 2. fix-login-bug (2025-01-14)
Summary: Login fails with special characters in password
Recommendation: Link to existing change `auth-improvements`
Action: Update request, add to existing tasks

### 3. improve-performance (2025-01-13)
Summary: [NEEDS CLARIFICATION] Which pages? What metrics?
Action: Ask user for specifics
```
