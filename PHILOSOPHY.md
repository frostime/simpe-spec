# The Philosophy of sspec

> Why this kind of protocol exists, beneath any particular rule or command.
> This document is implementation-agnostic on purpose. It describes the forces
> that govern human-agent collaboration on building something. The concrete
> names, files, and commands live elsewhere; §7 is the single seam that maps
> these forces onto sspec's vocabulary. Everywhere else, read for the structure,
> not the labels.

Throughout, **user** = the party that holds the intent and final authority;
**agent** = the party that holds cheap, abundant generation. The argument
applies to any setting where one side directs a strong generator.

---

## 1. The asymmetry that forces a protocol

A protocol is needed because of one resource imbalance:

```
user:   holds the intent and final authority — but judgment is scarce and costly
agent:  generation is cheap and unlimited    — but does NOT hold the intent
output: expensive both to produce AND to judge once produced
```

The agent can emit endless plausible output without knowing what is wanted. The
user knows what is wanted but cannot afford to inspect every possibility, and
judging the finished output is the most expensive check of all. Left
unmanaged, this drifts into one of two failures: the user is pushed by a process
they cannot steer, or the agent generates confidently in the wrong direction.

Every other idea here follows from spending the scarce resource — the user's
judgment — as efficiently as possible.

## 2. The target is not each other

It is tempting to picture collaboration as the two parties moving toward each
other. That picture is wrong, and the error is load-bearing.

Both sides converge on a **third anchor**, not on one another:

> the target = **intent ∧ reality** — what is genuinely wanted, *and* what the
> world actually permits.

Neither half alone is the target. Intent without reality is wishful; reality
without intent is aimless. The goal is their intersection.

Reality itself has two sources, and they matter because different parties carry
them:

- **Readable reality** — the existing system: it can be inspected directly, and
  the agent is usually the one who can read it.
- **External reality** — the world the system lives in: domain conventions,
  established practice, platform and business constraints. It often cannot be
  inspected from the artifact at all, and the user is frequently the only one
  who carries it.

This is why the relationship is not the agent yielding to the user. When the
agent brings readable reality, it may correct the user. When the user brings
external reality, they correct the agent. Authority over the final call stays
with the user; the direction of correction does not.

## 3. The core move: verify on a cheap, faithful proxy

Judging the finished output is the most expensive check there is, and it happens
last — when error is most costly to undo. The central move of the protocol is to
avoid this:

> Move *verification* off the final, expensive artifact and onto a **cheap proxy
> representation** produced earlier — and make the proxy faithful enough that
> **judging the proxy ≈ judging the artifact.**

A faithful proxy lets the user predict what the artifact will be *before it
exists*. That predictive power is the whole point of producing a proxy at all;
it is not a documentation byproduct. The more accurately the user can foresee
the outcome from the proxy, the cheaper and earlier their judgment becomes.

The gamble of building the wrong thing never vanishes — but it can be moved. Spent
on finished output, a wrong guess is discovered late and re-rolled by
regenerating: expensive, and the user is not steering. Spent on a cheap faithful
proxy, the same guess is caught early, re-rolling is nearly free, and the user
holds the wheel. Fidelity is what makes the relocation legitimate; an
unfaithful proxy moves the check to a place where it no longer means anything.

## 4. The four boundary operators

Across the boundary between user and agent, only four kinds of crossing exist.
They are not chosen — they are forced by two orthogonal axes:

- **who initiates** — user or agent
- **what is at stake** — the *problem space* (what is wanted, why, and its
  bounds) or the *solution space* (how it will be done)

```
                 problem space                  solution space
user-initiated   seed the raw intent            push back on the proposal
agent-initiated  excavate the real problem      expose the working model
```

Four cells, filled exactly once each — no overlap, no gap. There are precisely
four operators because the grid is 2×2; the count is forced, not assembled.

The diagonals are two request-response pairs:

- **Problem pair** — the user seeds a raw, partial intent; the agent takes on the
  hard, unglamorous work of excavating the usable problem: the real goal behind
  the stated one, the boundaries, and the reality on both sides. Together they
  build a shared *problem*.
- **Solution pair** — the holder of the evolving artifact exposes its current
  model for inspection; the other side either lets it stand or pushes back.
  Together they converge on a shared *solution*.

Note what is absent: the acts of *producing* the artifact — designing, building —
are not on this grid. Those happen inside the agent, between crossings. This
grid is the communication boundary, the feedback channel — not the workflow.

## 5. Dynamics: initiative follows information ownership

The grid is not static. Which side moves first flips between the two spaces,
and the flip is not arbitrary:

```
problem space:   the user moves first
solution space:  the agent moves first
```

**Whoever holds the decisive information at that moment moves first.** At the
start only the user holds the intent, so they must seed it before the agent can
excavate. During production only the agent holds the evolving artifact, so the
agent must expose it before the other side can react.

This collapses the four operators into two request-response pairs. Each pair has
a default response: when the artifact is exposed, **silence is assent** — pushing
back is the negative branch, not a required step. Progress proceeds unless a
judgment is actively withheld.

## 6. Modes, not phases

The four operators are **modes**, defined by their triggering condition, not
**phases** laid out on a timeline. A mode fires whenever its condition holds,
regardless of when.

Two consequences:

- **Excavating the problem recurs.** It is not a one-time opening step. Any time
  a contradiction with reality surfaces — mid-production, during inspection — the
  problem is no longer settled, and that mode fires again.
- **A deep enough pushback re-opens the problem.** Most pushback lives in the
  solution space ("this approach is wrong"). But some really means "you
  misread what I wanted" — that is a problem-space objection, and it throws the
  work back into excavation. The grid's purity has this one seam; the
  modes-not-phases nature is exactly what absorbs it.

Orthogonal to all four operators runs a posture the agent occupies *within* any
of them: **construct** (no baseline yet — generate the shared understanding;
divergent, then convergent) versus **verify** (a baseline exists — check the
product against it; convergent, confirmatory). Excavating the problem is
construct; exposing the model for inspection is verify. The same questioning
technique that builds understanding can later be reused to re-open it — because
at that moment the posture has switched back to construct.

---

## 7. How sspec names this

The sections above describe forces, not sspec. This is the single seam where
they meet sspec's vocabulary. The forces do not depend on these names — sspec is
*one* implementation of them.

| Force (concept) | sspec calls it | and carries it as |
|---|---|---|
| user seeds the raw intent | **Request** | a recorded intent entry |
| agent excavates the real problem | **Clarify** | a reusable investigation posture |
| agent exposes the working model | **Align** | a structured checkpoint with the user |
| user pushes back on the proposal | **Argue** | an explicit objection that halts and redirects |
| the cheap faithful proxy (§3) | the spec / design artifacts | files the user reads to predict the code |
| the target = intent ∧ reality | the principle that the user can predict the outcome | enforced at every checkpoint |

Which side carries which reality (§2) also shows up directly: the agent supplies
readable system reality while excavating; the user most often injects external
reality at the moment of pushback, since the agent cannot read it.

## 8. The invariant, and the litmus

> Collaboration gathers intent and reality — scattered across the user, the
> agent, and the world — and aligns them on the cheapest faithful proxy, at the
> least judgment cost, converging on **intent ∧ reality** before committing to
> the expensive artifact.

When a rule is silent or two rules pull against each other, do not guess from
the letter of the protocol. Ask of any rule or action:

- does it **lower the cost** of the user's judgment?
- does it **raise the fidelity** of the proxy?
- does it **move verification earlier**?

If yes, it is in the spirit. If it makes the agent generate more while the user
understands less, it is against it — whatever the rules happen to say.
