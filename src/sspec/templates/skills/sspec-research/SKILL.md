---
name: sspec-research
description: "Investigate the problem space, read code, build understanding. Use when starting new work or when context is insufficient."
metadata:
  author: frostime
  version: 2.0.1
---

# SSPEC Research

Explore and investigate before designing. This phase is about **understanding**, not solving.

---

## When to Use

- Starting work on a new request/change
- Context is insufficient to make design decisions
- Unclear problem boundary or multiple possible interpretations
- Need to understand existing code before modifying

## Stance

- **Curious**: Ask questions that emerge naturally from what you find
- **Thorough**: Read actual code, don't just theorize
- **Visual**: Use diagrams when they clarify thinking
- **Grounded**: Follow evidence in the codebase, challenge assumptions
- **No implementation**: Do NOT write code or modify files (except notes)

## What to Do

**Explore the problem space**:
- Read request/issue description carefully
- Identify what's actually being asked vs surface description, follows First Principle
- Challenge assumptions — find the real problem

**Investigate the codebase**:
- Map existing architecture relevant to the work
- Find integration points, patterns already in use
- Surface hidden complexity or edge cases
- Read `project.md`, `spec-docs/`, existing change handovers
- To locate the change to resume, use `sspec change list` or `sspec change find <name>`
- To read long Markdown files efficiently: `sspec howto read-long-mdfile`

**Compare approaches** (if multiple paths visible):
- Brainstorm options, build comparison tables
- Sketch tradeoffs with ASCII diagrams
- Identify risks and unknowns

## Outputs

Research findings go to:

| Output | Where |
|--------|-------|
| Research notes, analysis | `<change>/reference/` or `.sspec/tmp/` |
| Key file discoveries | `handover.md` Working Memory → Key Files |
| Important realizations | `handover.md` Working Memory → Notes |

## Exit Criteria

Research is sufficient when you can articulate:
1. What the actual problem is (first principles, not surface symptom)
2. What parts of the codebase are affected
3. What approach(es) could work

→ Then transition to `sspec-design` phase.

If uncertain whether research is complete → `@align` user: "Here's my understanding. Is this sufficient to proceed to design?"

---

## Consultation During Research

Research is inherently ambiguous — requirements are often unclear, intent can drift, context may be missing.

**When to ask mid-research** (don't guess, ask):
- Requirement is ambiguous or contradicts itself
- User intent is unclear — multiple valid interpretations exist
- You lack context only the user can provide (preference, priorities, constraints)
- Codebase reality diverges from the stated problem

**How to ask**:
- Use `question` tool for quick in-flight clarifications (don't block research for simple things)
- Batch non-blocking questions and ask them at a natural checkpoint
- **Never defer a critical ambiguity to design** — clarify it now, or your research points at the wrong target

**Posture**: One question now beats a wrong design later.
