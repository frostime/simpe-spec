# /propose

Create a new change proposal.

## Arguments

`/propose <change-name>` or `/propose` to discuss first.

## Workflow

1. **Check requests**
   - Look for open requests in `.sspec/requests/`
   - Create new change proposal or attach to existing changs.
   - If creating proposal from a request, link them:
     - Update request frontmatter: `changes: [<change-name>]`
     - Update request status: `in-progress`

2. **Understand** what the user wants to accomplish
   - Ask clarifying questions if requirements are vague
   - Identify scope boundaries early

3. **Check** for conflicts
   ```bash
   sspec list
   ```
   - Ensure no overlapping active changes
   - Consider dependencies on other work

4. **Create** the change directory
   ```bash
   sspec new <name>
   ```

5. **Fill** `proposal.md`
   - **Why**: Problem or opportunity (1-2 sentences)
   - **What**: Specific changes (concrete bullet list)
   - **Success Criteria**: How we know it's done
   - **Impact**: Affected areas, breaking changes
   - **Out of Scope**: What we're explicitly not doing

6. **Draft** `tasks.md`
   - Break into small, verifiable steps
   - Order by dependency
   - Include validation/testing steps
   - Mark parallelizable tasks with `[P]`

7. **Handle ambiguity**
   - Mark unclear requirements: `[NEEDS CLARIFICATION: specific question]`
   - Do NOT guess or make assumptions
   - List open questions in proposal.md

8. **Review** with user before starting implementation

## Skip Proposal For

These can be done directly without formal proposal:
- Bug fixes (restoring intended behavior)
- Typos, formatting, comments
- Simple config changes
- Adding tests for existing code

## Guidelines

- Favor small, focused changes over large ones
- If scope is large, suggest splitting into multiple changes
- Don't start implementation until proposal is approved
- Use `memo.md` for research during exploration phase

## Output

After creating proposal, summarize:
```
Created change: <name>

Why: [1 sentence]
What: [key changes]
Tasks: [count] steps

Ready to review proposal.md and tasks.md?
```
