# /propose

Create a new change proposal.

## Arguments

`/propose <change-name>` or just `/propose` to discuss first.

## Task

1. **Understand** what the user wants to accomplish
2. **Check** existing changes for conflicts: `sspec list`
3. **Create** the change directory: `sspec new <n>`
4. **Fill** `proposal.md`:
   - Why: Problem or opportunity (1-2 sentences)
   - What: Specific changes (bullet list)
   - Impact: Affected areas, breaking changes
   - Out of Scope: What we're explicitly not doing
5. **Draft** `tasks.md`:
   - Break down into small, verifiable steps
   - Order by dependency
   - Include validation/testing steps
6. **Note** about `memo.md`:
   - Use for research notes, code snippets, and ideas
   - Record findings during code exploration
   - Transfer important insights to `tasks.md` when ready
7. **Review** with user before starting implementation

## Guidelines

- Favor small, focused changes
- If scope is large, suggest splitting into multiple changes
- Ask clarifying questions for vague requirements
- Don't start implementation until proposal is approved
- Use `memo.md` for research notes, code snippets, and ideas during exploration
- Transfer important findings from `memo.md` to `tasks.md` or `knowledge/` when solidified

## Skip Proposal For

- Bug fixes (restore intended behavior)
- Typos, formatting, comments
- Simple config changes
- Adding tests for existing code

These can be done directly without formal proposal.
