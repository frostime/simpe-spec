---
name: sspec-clarify
description: "Build shared understanding through dialogue and investigation. Produces Problem Statement + direction sketch. Reusable posture, not rigid phase."
metadata:
  author: frostime
  version: 5.0.0
---

# SSPEC Clarify

Synthesize the user's intent and codebase reality into a shared understanding of the problem. This phase produces the raw material for Design — not through dialogue or investigation alone, but through the collision of both.

Clarify is a **posture**, not a rigid phase. It's the recommended entry point for new work, but can be re-entered whenever understanding drifts — during Review revision, when implementation hits a contradiction, or when a new requirement surfaces.

---

## Stance

- **Socratic**: Extract the user's real intent through questions, not assumptions
- **Grounded**: Verify against codebase reality — intent without evidence is speculation
- **Synthesizing**: Merge subjective intent and objective reality into a coherent problem definition
- **No implementation**: Do NOT write code or modify files (except notes)

## Workflow

```
1. Subjective — understand the user's real intent
2. Objective — understand the codebase/system reality
3. Synthesis — merge into Problem Statement + direction
```

Steps 1 and 2 interleave naturally. Don't force a strict sequence.

### Step 1: Subjective — User Intent

The user's words are a starting point, not the requirement itself. Work from first principles to understand what they actually need.

- Read the request/issue/user message carefully
- Identify what's actually being asked vs the surface description
- Watch for the **XY Problem**: user may describe means rather than goals. Probe: "Why this? What's the real problem?"
- Use Socratic questioning to surface their mental model:
  - **Restate**: "My understanding is we need to solve X, not Y"
  - **Boundary**: "This does NOT include W — correct?"
  - **Priority**: "If we could only fix one thing, which matters most?"
  - **Unknowns**: "I'm not sure about Z — does it apply here?"
- Decompose open-ended requirements into atomic choice/confirmation questions — reduce user response cost

Scale with complexity: a clear bugfix needs one confirmation, a vague feature request needs deeper probing.

### Step 2: Objective — Codebase Reality

The system has its own truth. Investigate to ground the dialogue.

- Map existing architecture relevant to the work
- Find integration points, patterns already in use
- Surface hidden complexity, edge cases, or constraints
- Read `project.md`, `spec-docs/`, existing change memory files
- If the user's request involves external APIs/systems, understand how they actually work (not how the user assumes they work)
- To locate existing changes: `sspec change list` or `sspec change find <name>`

Feed findings back into dialogue: "You mentioned X, but the code actually does Y — does that change your thinking?"

### Step 3: Synthesis

When subjective intent and objective reality have collided enough, a shared understanding emerges. At this point you should be able to sketch:

1. **Problem Statement** — what's actually wrong, grounded in evidence
2. **Direction** — which approach makes sense given both intent and reality
3. **Open questions** — what remains uncertain (if anything)

This sketch is informal — it becomes formal in Design (spec.md). But the thinking should already be clear enough that Design is formalization, not discovery.

## Reusable Posture

Clarify is not limited to the start of a change. Re-enter Clarify posture when:

- **Review feedback** reveals a misunderstanding about what was needed
- **Implementation** hits a contradiction between design and reality
- **Revision** is needed — understand what changed and why before writing `revisions/NNN-*.md`
- **Scope drift** — the problem has shifted since the original Clarify

In re-entry mode, the process is lighter: focus on the specific point of confusion, re-sync with the user, then return to the current phase.

## Memory Management

**Short Clarify** (≤5 exchanges): no artifact needed. Product flows directly into spec.md during Design.

**Long Clarify** (>10 exchanges or involving research/investigation):
- Investigation materials → `.sspec/tmp/clarify_<YY-MM-DDTHH-MM>_<topic>.md`
- Naming follows the change timestamp format — sortable, greppable
- After change creation (early Design), move relevant materials to `change/reference/`
- Key decisions and turning points → write into memory.md Knowledge during Design
- Don't wait until Design to write things down — context compression can erase the reasoning behind your conclusions

## Exit Criteria

Clarify is complete when **both sides** can articulate:
1. What the actual problem is (first principles, not surface symptom)
2. What the boundaries are (what's in scope, what's not)
3. What direction to go (not full design — just enough to enter Design)
4. Which uncertainties are resolved vs still open

Before leaving Clarify:
- If a remaining uncertainty would materially change the design, resolve it NOW
- Record assumptions and open decisions in notes
- Do not enter Design while a design-shaping uncertainty remains implicit

→ Then transition to `sspec-design` phase.

## When to Ask

This phase IS dialogue. Asking is the default posture, not the exception. If you're unsure about intent, priority, constraint, or feasibility — ask.

**Posture**: One question now beats a wrong design later.
