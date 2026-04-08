---
name: sspec-research
description: "Investigate the problem space, read code, build understanding. Use when starting new work or when context is insufficient."
metadata:
  author: frostime
  version: 3.0.0
---

# SSPEC Research

Explore and investigate before designing. This phase is about **understanding**, not solving.

---

## Stance

- **Curious**: Ask questions that emerge naturally from what you find
- **Thorough**: Read actual code, don't just theorize
- **Grounded**: Follow evidence in the codebase, challenge assumptions
- **No implementation**: Do NOT write code or modify files (except notes)

## Workflow

```
1. Understand intent — what does the user actually want?
2. Align understanding — restate, surface unknowns, confirm boundaries
3. Investigate — read code, map architecture, find affected areas
4. Exit — articulate the problem + scope + possible approaches
```

### Step 1-2: Understand & Align

Before investigating the codebase, first make sure you understand the problem itself.

- Read the request/issue/user message carefully
- Identify what's actually being asked vs the surface description — follow first principles
- Watch for the **XY Problem**: user may describe a solution (means) rather than the real goal. Probe: "Why this? What's the real problem?"

Then **align understanding with the user**:
- **Restate**: "My understanding is we need to solve X, not Y"
- **Unknowns**: "I'm not sure about Z — does it apply here?"
- **Boundary**: "This does NOT include W — correct?"

Even if the user's request seems clear, this step surfaces hidden assumptions. If the task truly needs no alignment, it probably doesn't need a formal change either.

### Step 3: Investigate

With aligned understanding, explore the codebase:
- Map existing architecture relevant to the work
- Find integration points, patterns already in use
- Surface hidden complexity or edge cases
- Read `project.md`, `spec-docs/`, existing change handovers
- To locate changes: `sspec change list` or `sspec change find <name>`

If investigation reveals the problem is different from what was aligned, re-align before continuing.

### Step 4: Exit Criteria

Research is sufficient when you can articulate:
1. What the actual problem is (first principles, not surface symptom)
2. What parts of the codebase are affected
3. What approach(es) could work
4. Which uncertainties are resolved vs still open

Before leaving Research:
- Resolve anything you can by reading code, docs, or existing changes first
- If a remaining uncertainty would materially change the design, clarify it NOW
- Record assumptions and open decisions in notes so Design does not proceed on hidden guesses
- Do not enter Design while a design-shaping uncertainty remains implicit

→ Then transition to `sspec-design` phase.

## Consultation During Research

Research is inherently ambiguous. Don't guess, ask.

- Requirement is ambiguous or contradicts itself → ask
- User intent is unclear — multiple valid interpretations → ask
- Codebase reality diverges from the stated problem → ask
- You lack context only the user can provide → ask

**Posture**: One question now beats a wrong design later.
