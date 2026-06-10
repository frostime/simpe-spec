---
name: sspec-clarify
description: "Build shared understanding through dialogue and investigation. Produces Problem Statement + direction sketch. Reusable posture, not rigid phase."
metadata:
  author: frostime
  version: 6.2.0
---

# SSPEC Clarify

Clarify excavates the problem space: align user intent with reality before Design. The output is a cheap, faithful proxy: the user can predict the likely design, patch scope, user-visible behavior, and major risks before implementation begins.

Clarify is a **posture**, not a rigid phase. Re-enter it whenever understanding drifts: Review feedback, implementation contradiction, revision, or scope drift.

**No implementation**: dialogue + investigation only. Do NOT modify code/files except notes.

## Core Model

Clarify recursively resolves a MECE decision tree. Each design-shaping node is processed through:

```text
Subjective intent + Objective reality → Synthesis
```

| Concept | Role |
|---|---|
| Subjective | User-owned intent, priority, boundary, external constraint, judgment |
| Objective | Codebase/system/docs/API/trusted-source reality the agent can inspect |
| Synthesis | Current working model, bet, branch classification, next uncertainty |
| Recursive MECE | How the decision tree expands: non-overlapping, no gaps, dependency-aware |
| Socratic questioning | How the agent asks the user to inspect/correct a falsifiable bet |

The format is flexible. Avoid performative status output. Each clarification turn must advance the tree or make clear why it is ready to exit.

## Iteration Protocol

For each unresolved design-shaping node:

1. Identify what user-owned intent/constraint may decide it.
2. Identify what objective facts can be investigated.
3. Investigate facts before asking the user factual questions.
4. Present a concise working model or delta.
5. Ask Socratic question groups for user-owned judgments.
6. Classify the result: blocker / assumption / deferred / irrelevant.

A useful turn does at least one:

- closes a branch
- opens a necessary sub-branch
- revises the framing
- classifies uncertainty
- surfaces a blocker
- proves the current model is ready for Design

Incomplete clarification: surface choices without an inspectable working model, objective reality, or decision-tree consequence.

## Step 1: Subjective — User Intent

User words are raw input, not the requirement itself. Separate goal / symptom / proposed solution.

Socratic questioning is the core interaction model: state a falsifiable framing or recommended bet, then ask the user to confirm, correct, or refine it.

| Pattern | Example |
|---|---|
| Restate | "I think the real problem is X, not Y — correct?" |
| Boundary | "This excludes W — correct?" |
| Priority | "If only one outcome matters, which one? My bet is ..." |
| Unknown | "I am unsure whether Z applies. My current assumption is ..." |
| Challenge | "If this direction is wrong, the alternative framing may be ..." |

Rules:

- State your framing and current bet before asking the user to decide.
- Ask question groups, not isolated trivia: group by dependency.
- Independent branches can be asked together; dependent branches wait for upstream answers.
- Use structured-choice tools if available; otherwise present compact numbered options. Use prose for complex or open-ended judgment.
- Explain impact only when it changes user judgment.

## Step 2: Objective — Reality

Investigate before asking factual questions: if code, docs, commands, logs, tests, project state, or trusted external sources can answer a question, inspect them first.

Read as relevant:

- `project.md`, `spec-docs/`, existing change memory files
- architecture, integration points, existing patterns
- hidden constraints, edge cases, external API/system behavior
- existing changes via `sspec change list` or `sspec change find <name>`
- trusted external sources via available tools/skills when outside reality matters; prefer authoritative pages and cite them

Ask the user for intent, priorities, external constraints, and judgments the system cannot reveal. If tools or sources are unavailable, state that limitation as an assumption.

Feed findings back: "You said X; the system/source shows Y. Does that change the framing?"

## Step 3: Synthesis

When intent and reality have collided enough, sketch a working model.

**Working model** = problem framing + relevant evidence + open decision branches + agent's current bet.

| Part | Content |
|---|---|
| Problem Statement | Actual problem, not surface symptom |
| Direction | Approach that fits intent + reality |
| Evidence map | User intent, system evidence, trusted external-source evidence, user constraints, assumptions |
| Open branches | Classified as blocker / assumption / deferred / irrelevant |

Branch classification:

| Type | Meaning | Action |
|---|---|---|
| Blocker | Could change framing, scope, user-visible behavior, risk, or implementation direction | Resolve before Design |
| Assumption | Safe to proceed if explicit and reviewable | Record |
| Deferred | Intentionally outside current scope/phase | Record boundary |
| Irrelevant | Does not affect Design | Drop |

Design should formalize this sketch, not discover it from scratch.

## Exit Readiness

For a one-confirmation Clarify, the exit gate is implicit: proceed only if no blocker is visible after basic reality inspection.

For formal Clarify, enter Design only when all are true:

- Problem, boundaries, direction, and open questions are articulable by both sides
- Working model cites intent, system evidence, constraints, and assumptions
- No blocker remains unresolved or implicit
- Remaining questions are classified: blocker / assumption / deferred / irrelevant
- Adversarial audit has not exposed a design-changing branch
- Notes record assumptions and open decisions

Adversarial audit probes:

| Probe | Question |
|---|---|
| Alternative framing | If this is the wrong problem, what is the real one? |
| Counter-evidence | What fact would contradict this direction? Can it be checked now? |
| Smaller solution | What narrower change could satisfy the outcome? |
| Failure forecast | What later failure would prove Clarify missed something? |
| Boundary/term attack | Which terms, actors, states, or responsibilities are ambiguous? |

Use subagent review for complex, vague, high-impact, or anchoring-prone Clarify when available. Brief it with only: working model, confirmed facts, stable file/doc pointers, and request to find missing branches, alternative framings, contradictions, or premature-exit risks. Main agent verifies claims and decides.

Then transition to `sspec-design`.

## Minimal Few-shot

Bad:

```text
Questions:
- Which label should the result use?
- Which optional behavior should be included?
User answers → Agent enters Design.
```

Why bad: surface choices only; no working model, reality check, decision-tree consequence, or adversarial pressure.

Better:

```text
Model: desired outcome / proposed change / relevant evidence / current bet
Branches: blocker / assumption / deferred
Questions:
- Framing group — my bet: ...; impact: ...; confirm/correct?
- Boundary group — my bet: ...; impact: ...; confirm/correct?
```

## Memory

- Short Clarify (≤5 exchanges): no artifact needed; carry result into Design.
- Long Clarify (>10 exchanges or research-heavy): create notes with `sspec tmp new clarify_<topic>`; the command adds the timestamp prefix.
- After change creation, move relevant materials to `change/reference/`.
- Key decisions/turning points → memory.md Knowledge during Design.
- Capture reasoning before Design; context compression can erase it.
