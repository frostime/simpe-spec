---
name: sspec-clarify
description: "Build shared understanding through dialogue and investigation. Produces Problem Statement + direction sketch. Reusable posture, not rigid phase."
metadata:
  author: frostime
  version: 6.1.3
---

# SSPEC Clarify

Clarify excavates the problem space: combine user intent + system reality until Design can be a cheap, faithful proxy the user can judge before implementation.

Clarify is a **posture**, not a rigid phase. Re-enter it whenever understanding drifts: Review feedback, implementation contradiction, revision, or scope drift.

**No implementation**: dialogue + investigation only. Do NOT modify code/files except notes.

## Workflow

```text
Subjective intent ↔ Objective reality → Synthesis → Adversarial audit → Design readiness
```

Subjective and Objective interleave. Gather whichever side is currently missing.

## Multi-round Decision-tree Clarify

For non-trivial work, use visible rounds. Small obvious fixes may need one short round; vague, architectural, or high-risk requests need multiple rounds.

Each clarification turn MUST:

- Start with `Clarify Round <n>`
- Provide enough working model for the user to judge the questions: current framing + relevant evidence + decision-tree status
- After Round 1, prefer delta-only unless framing changed or audit is needed
- Show decision-tree status relevant to the current question group: closed / opened / revised / classified branches
- Group questions by dependency: independent branches together; dependent branches across rounds
- Include the agent's recommended answer or current bet for each question group
- Explain impact when non-obvious

Incomplete round: asks surface choices without enough working model or decision-tree context for the user to judge them.

Decision tree inputs:

- User intent and priorities
- Readable system reality: code, docs, project state
- Trusted external-source reality when relevant: official docs, standards, deprecations, common practice, or current web sources
- User-supplied external constraints
- Contradictions between intent, system facts, external sources, and user constraints

### Branch Severity

| Type | Meaning | Action |
|---|---|---|
| Blocker | Could change problem framing, scope, user-visible behavior, risk, or implementation direction | Resolve before Design |
| Assumption | Safe to proceed if explicit and reviewable | Record |
| Deferred | Intentionally out of current scope/phase | Record boundary |
| Irrelevant | Does not affect Design | Drop |

## Step 1: Subjective — User Intent

User words are raw input, not the requirement itself.

Do:

- Separate goal / symptom / proposed solution
- Watch for XY problem: user may describe means rather than goal
- Surface boundaries, priorities, unknowns, and success criteria
- State your framing first so the user can correct it

Socratic patterns:

| Pattern | Example |
|---|---|
| Restate | "My understanding is we need X, not Y — correct?" |
| Boundary | "This excludes W — correct?" |
| Priority | "If only one outcome matters, which one?" |
| Unknown | "I am unsure whether Z applies — does it?" |

Recursive MECE:

- Branches at each layer are non-overlapping and no-gaps
- Each answered branch narrows the tree and may expose sub-branches
- Continue until no open branch would materially change Design
- Scale depth to task complexity

## Step 2: Objective — Codebase/System Reality

Investigate facts the user should not need to answer.

Read as relevant:

- `project.md`, `spec-docs/`, existing change memory files
- Architecture, integration points, existing patterns
- Hidden constraints, edge cases, and external API/system behavior
- Trusted external sources via available tools/skills when current outside reality matters; prefer authoritative source pages and cite them
- Existing changes via `sspec change list` or `sspec change find <name>`

Rule: if code/docs/system state can answer a question, investigate instead of asking. Ask the user for intent, priorities, external constraints, and judgments the system cannot reveal.

Feed findings into dialogue: "You said X; the system shows Y. Does that change the framing?"

## Step 3: Synthesis

When intent and reality have collided enough, sketch:

1. **Problem Statement** — actual problem, not surface symptom
2. **Direction** — approach that fits intent + reality
3. **Open questions** — classified by Branch Severity

Evidence map:

- User-confirmed intent
- Codebase/system evidence
- Trusted external-source evidence when used
- User-supplied external constraints
- Explicit assumptions

Design should formalize this sketch, not discover it from scratch.

## Adversarial Audit

Before Design for non-trivial work, challenge the framing.

| Probe | Question |
|---|---|
| Alternative framing | If this is the wrong problem, what is the real one? |
| Counter-evidence | What fact would contradict this direction? Can it be checked now? |
| Smaller solution | What narrower change could satisfy the outcome? |
| Failure forecast | What later failure would prove Clarify missed something? |
| Boundary/term attack | Which terms, actors, states, or responsibilities are ambiguous? |

If the audit opens a blocker, continue Clarify.

## Optional Subagent Review

Use for complex, vague, high-impact, or anchoring-prone Clarify when the environment supports a subagent: an isolated secondary agent/context that receives a limited brief.

Brief the subagent with only: working model, confirmed facts, stable file/doc pointers, and request to find missing branches, alternative framings, contradictions, or premature-exit risks. Subagent critiques; main agent verifies claims and decides.

## Minimal Few-shot: Incomplete Clarify

Schematic only; replace placeholders with task facts.

Bad:

```text
Clarify Round 1:
Questions:
- Which label should the result use?
- Which optional behavior should be included?
- Which result format should be used?

User answers → Agent enters Design.
```

Why bad: surface choices only; no working model, decision tree, adversarial check, or open-question classification.

Better:

```text
Clarify Round 1:
Model: desired outcome / proposed change / known reality / possible mismatch
Tree: closed / opened / revised / classified branches
Questions:
- Framing group — my bet: ...; impact: ...; confirm/correct?
- Boundary group — my bet: ...; impact: ...; confirm/correct?
```

## Memory Management

- Short Clarify (≤5 exchanges): no artifact needed; carry result into Design.
- Long Clarify (>10 exchanges or research-heavy): create notes with `sspec tmp new clarify_<topic>`; the command adds the timestamp prefix.
- After change creation, move relevant materials to `change/reference/`.
- Key decisions/turning points → memory.md Knowledge during Design.
- Capture reasoning before Design; context compression can erase it.

## Exit Gate

Enter Design only when all are true:

- Problem, boundaries, direction, and open questions are articulable by both sides
- Working model cites intent, system evidence, constraints, and assumptions
- No blocker remains unresolved or implicit
- Remaining questions are classified: blocker / assumption / deferred / irrelevant
- Adversarial audit has not exposed a design-changing branch
- Notes record assumptions and open decisions

Usually exit with `Clarify Round <n> — Audit`, then transition to `sspec-design`.
