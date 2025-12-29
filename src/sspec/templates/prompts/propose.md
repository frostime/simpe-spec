# sspec/propose

Create a new change proposal.

## Arguments

`sspec/propose <change-name>` or `sspec/propose` to discuss first.

## Workflow

1. **Understand** what the user wants to accomplish
   - Ask clarifying questions if requirements are vague
   - Identify scope boundaries early
   - If this comes from a user request, note the source

2. **Check** for conflicts
   ```bash
   sspec list
   ```
   - Ensure no overlapping active changes
   - Consider dependencies on other work

3. **Create** the change directory
   ```bash
   sspec new <name>
   ```

4. **Fill** `proposal.md`
   - **Why**: Problem or opportunity (1-2 sentences)
   - **What**: Specific changes (concrete bullet list)
   - **Success Criteria**: How we know it's done
   - **Impact**: Affected areas, breaking changes
   - **Out of Scope**: What we're explicitly not doing
   - **References**: Link to source request if applicable

5. **Draft** `tasks.md`
   - Break into small, verifiable steps
   - Order by dependency
   - Include validation/testing steps
   - Mark parallelizable tasks with `[P]`

6. **If from a request**: Update request frontmatter
   - `status: in-progress`
   - `change: <change-name>`

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
Source: [request name] / direct conversation

Ready to review proposal.md and tasks.md?
```
