# /handover

Generate a handover document for session continuity.

## Context

We've been working on a task through an extended conversation. I'm about to start a new session/chat.

## Task

Write a handover prompt that enables the next AI assistant to resume seamlessly.

## Required Content

```
<background>
Brief context of the overall task/project
</background>

<completed>
What was accomplished this session
</completed>

<current_state>
Exact state right now - what's working, what's not
</current_state>

<next_steps>
Concrete next actions, in priority order
</next_steps>

<conventions>
Key constraints, patterns, or rules to follow
</conventions>
```

## Style

- Optimize for LLM consumption
- High information density
- No filler phrases
- Concrete over abstract
- Include file paths, function names, error messages where relevant

## After Writing

Update the relevant `handover.md` file:
- If working on a specific change: `changes/<n>/handover.md`
- For global state: `.sspec/handover.md`
