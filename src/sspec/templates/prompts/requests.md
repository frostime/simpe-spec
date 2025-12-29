# sspec/request

Process a user-submitted request.

## Purpose

The user has written a structured request and is asking you to read it.

**Important**: You do NOT proactively scan the requests folder. The user will tell you when they have a request.

## When User Says

- "看一下我写的 request"
- "Read my request about X"
- "处理一下 requests/xxx"
- "I wrote a request for the dark mode feature"

## Workflow

1. **Read** the specified request
   - If user names it: `.sspec/requests/<name>.md`
   - If unclear, ask: "Which request should I read?"

2. **Understand** the request
   - What does the user want?
   - Are there ambiguities to clarify?

3. **Decide** action:
   - Create new change → `sspec/propose <name>`
   - Link to existing change
   - Ask clarifying questions
   - Mark as invalid (explain why)

4. **Link** if creating change:
   - In `proposal.md` References: link to the request
   - Update request frontmatter: `status: in-progress`, `change: <name>`

## What requests/ Is For

requests/ is an **input channel**, not a **status hub**:
- User writes structured feature requests (like GitHub issue templates)
- User edits in their preferred editor with good UX
- User explicitly submits to agent when ready
- Agent processes and creates change, referencing the request

**Not a queue to check** — user drives when requests are processed.

## Output

```
## Request: <name>

**Summary**: [one sentence]
**My Understanding**: [what you think user wants]

**Questions** (if any):
- [clarification needed]

**Action**: Create change `sspec/propose <suggested-name>`

Proceed?
```
