---
name: howto-integration-optimize
status: REVIEW
type: ''
change-type: single
created: 2026-03-10T14:16:30
reference:
- source: .sspec/changes/26-03-09T23-41_add-howto-cli
  type: prev-change
  note: This change follows up the howto CLI introduced in add-howto-cli, integrating
    it into the AGENTS.md protocol and built-in SKILL files.
---

<!-- @RULE: Frontmatter
status: PLANNING | DOING | REVIEW | DONE | BLOCKED
change-type: single | sub
reference?: Array<{source, type: 'request'|'root-change'|'sub-change'|'prev-change' |'doc', note?}>

Sub-change MUST link root:
reference:
  - source: ".sspec/changes/<root-change-dir>"
    type: "root-change"
    note: "Phase <n>: <phase-name>"

Single-change common reference:
reference:
  - source: ".sspec/requests/<request-file>.md"
    type: "request"
  - source: ".sspec/changes/<change-dir>"
    type: "prev-change"
    note: "This change is a follow-up to <change-name> which introduced <feature/bug>. This change addresses <issue> with that feature/bug."
-->

# howto-integration-optimize

## A. Problem Statement

### Current Situation

sspec's knowledge architecture currently has two tiers: a dense `AGENTS.md` protocol (~220 lines, always in managed context) and heavyweight SKILL files (~50-150 lines, loaded per phase). There is no middle tier for short, targeted operational procedures. This causes:

- **Token waste**: an agent mid-task must scan AGENTS.md or reload a full SKILL to find a 5-line answer (e.g., the change status state machine, or how to invoke `sspec ask`).
- **Stale duplication**: AGENTS.md §1/§3 contain inline rules that now duplicate content in HOWTOs (`use-sspec-ask`, `get-current-time`, `find-change`), with no pointer tying them together.
- **Invisible HOWTOs**: the `howto` CLI was introduced in `add-howto-cli` but is not referenced from AGENTS.md, SKILLs, or any workflow document. Agents using sspec will not discover it unless they already know it exists.

### User Requirement

Make HOWTOs a first-class citizen in the sspec workflow by:
1. Referencing the HOWTO system from AGENTS.md so agents can discover and use it
2. Adding point-of-need HOWTO pointers at the key decision moments in AGENTS.md where inline rules are too brief to be actionable
3. Extending built-in SKILL files to delegate to specific HOWTOs for common sub-procedures
4. Adding two missing high-value HOWTOs (`resume-change`, `write-handover`) that fill documented gaps in the current builtin set

## B. Proposed Solution

Integrate HOWTO into the three-tier knowledge architecture so it becomes a visible, navigable middle tier between `AGENTS.md` (overview) and SKILLs (phase contracts). All changes are additive — no existing behavior is removed. The goal is to reduce token cost for targeted lookups and eliminate duplicate inline rules that now have better HOWTO counterparts.

### Approach

Three parallel tracks:

**Track A — AGENTS.md template updates**: Add a `### HOWTO System` discovery block to §5 Reference; insert HOWTO pointers at three key decision points in §1 Background rules and §3 Alignment; add `sspec howto list` to the CLI Quick Reference table. Wherever a HOWTO replaces an inline rule, shrink the inline text to a one-liner and forward to the HOWTO.

**Track B — New builtin HOWTOs**: Add `resume-change` (exact read-order procedure for resuming a change from handover.md) and `write-handover` (how to write effective Session Log + Working Memory entries). These cover the two most common agent micro-tasks that currently have no dedicated HOWTO but appear repeatedly in protocol text.

**Track C — SKILL file integration**: Add targeted HOWTO delegation lines in `sspec-research`, `sspec-implement`, and `sspec-handover`. Each change is ≤2-3 lines and points to an existing or new HOWTO; no SKILL content is removed.

### Key Design

**Three-tier knowledge architecture (target state)**:

```
AGENTS.md               ← workflow navigator (overview, phase flow, shortcuts)
    ↓ references
HOWTO docs              ← targeted procedures (single-job, ≤50 lines)
    ↑ mentioned by
SKILL files             ← full lifecycle phase contracts (examples, criteria)
```

**Feat A: AGENTS.md HOWTO discovery block** (§5 Reference, after SKILL System section)

```markdown
### HOWTO System
Targeted operational micro-guides. Shorter than SKILLs; more specific than AGENTS.md.
- Discover: `sspec howto list`
- Read: `sspec howto <name>` (or batch: `sspec howto n1 n2`)
- Project HOWTOs: `sspec howto new <name>` → `.sspec/howto/`
```

**Feat B: AGENTS.md point-of-need references** — three inline rules become HOWTO pointers:

| Location | Current text | Replacement |
|---|---|---|
| §1 Background rules | "Current date/time uncertain → use sspec tool now" | same + `(→ sspec howto get-current-time)` |
| §1 Background rules | "Uncertain → @align" | same + `(→ sspec howto use-sspec-ask)` |
| §3 Alignment tool choice | "sspec ask CLI tool" decision tree | thin + `📚 Full flow: sspec howto use-sspec-ask` |

**Feat C: New builtin HOWTOs**

`resume-change` content outline:
- Read order: newest Session Log entry → tasks.md unchecked items → spec.md context
- Practical `sspec` commands to locate and verify the change
- Edge case: multiple active changes → `sspec howto find-change` first

`write-handover` content outline:
- Session Log format rules (append-only, newest-first, timestamped, tags)
- Working Memory update rules (Key Files, Decisions, Notes)
- When to promote to project.md Notes
- Anti-patterns (e.g., deleting old entries, writing future tense)

**Feat D: SKILL delegation lines** — brief additions only:

| SKILL | Addition |
|---|---|
| `sspec-research` | After "Resume tip" → `→ sspec howto find-change` and `→ sspec howto read-long-mdfile` |
| `sspec-implement` | After status update guidance → `→ sspec howto update-change-status` |
| `sspec-handover` | After timestamp rule → `→ sspec howto get-current-time` and `→ sspec howto write-handover` (new) |

### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/templates/AGENTS.md` | Add HOWTO System block; point-of-need references in §1 + §3 + §5 |
| `src/sspec/howto/resume-change.md` | New builtin HOWTO |
| `src/sspec/howto/write-handover.md` | New builtin HOWTO |
| `src/sspec/templates/skills/sspec-research/SKILL.md` | Add HOWTO delegation refs |
| `src/sspec/templates/skills/sspec-implement/SKILL.md` | Add HOWTO delegation ref |
| `src/sspec/templates/skills/sspec-handover/SKILL.md` | Add HOWTO delegation refs |
| `uv run sspec project update` | Sync managed AGENTS.md block and SKILL copies |
