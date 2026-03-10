---
name: handover-memory-structure
status: REVIEW
type: "refactor"
change-type: single
created: 2026-03-10T20:00:36
reference:
  - source: .sspec/changes/archive/26-03-06T00-34_handover-template-v2
    type: prev-change
    note: This change follows up the prior handover template redesign by refining the
      durable-memory structure after real-world usage exposed overlap between Working
      Memory and Session Log.
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

# handover-memory-structure

## A. Problem Statement

### Current Situation

The current handover template separates durable memory into `Decisions (Timestamped)` and
`Notes (Timestamped)`, while keeping volatile progress in `Session Log (Append-Only)`. That
stable-vs-volatile split is directionally correct, but real handovers now show repeated overlap:

- Memory `Notes` often capture next actions, review reminders, validation results, or one-off
  implementation outcomes that already belong in `Session Log`
- Memory `Decisions` sometimes capture phase or workflow transitions instead of lasting change
  knowledge
- both sections use similar timestamped bullet shapes, making promotion boundaries unclear during
  writing

This creates a "same fact written twice" pattern that slows resume, weakens scannability, and
turns `Notes` into a catch-all bucket.

### User Requirement

Replace the split `Decisions` / `Notes` memory structure with one merged durable-memory section.
Entries should use a typed format such as `[time] [type] [content]`, with a recommended canonical
type set for consistency, while still allowing rare custom types when a special case is clearer.
The redesign should reduce duplication without weakening the existing `Session Log` resume flow.

<!-- @RULE: Quantify impact. Format: "[metric] causing [impact]".
Simple: single paragraph. Complex: split "Current Situation" + "User Requirement". -->

## B. Proposed Solution

Replace the current two-bucket memory structure with a single typed durable-memory section while
leaving `Session Log` unchanged. This keeps the successful stable-vs-volatile split, but removes
the most ambiguous internal boundary inside Working Memory.

The new model is:

- `Key Files` stays as-is
- `Durable Memory (Typed, Timestamped)` becomes the only long-lived knowledge bucket
- `Session Log (Append-Only)` remains the single source of truth for current batch progress and
  next action
- recommended memory types differ between single-change and root-change handovers

This is preferred over a simple `Notes` rename because the problem is broader than naming: agents
currently need to decide whether something is a "decision" or a "note" before deciding whether it
is durable at all. A single typed bucket changes the primary question to the more useful one:
"Is this worth preserving across sessions?"

### Approach

Refactor both handover templates so durable memory uses one section with a compact, typed entry
format. Recommended types are scope-aware: single-change handovers get implementation-oriented
types, while root-change handovers get coordination-oriented types. An escape hatch still allows
agent-defined labels in rare cases.

Also split handover HOWTO guidance by job instead of keeping one HOWTO that repeats the SKILL.
`sspec-handover` remains the lifecycle contract, while focused HOWTOs cover the concrete sub-jobs:
writing `Session Log`, writing `Durable Memory`, and handling obsolete memory. The legacy
`write-handover` HOWTO becomes a lightweight router that points agents to the right focused HOWTO.

Keep `Session Log` headings, ordering, and `Next` semantics unchanged. This preserves current
resume/dashboard behavior and limits the change to template semantics plus writing guidance rather
than service logic.

### Key Design

### Interface Design

**Refactor A: Typed durable-memory section**

```markdown
## Working Memory (Stable)

### Key Files
- `path/file` - what it contains, why it matters

### Durable Memory (Typed, Timestamped)
- [2026-03-10T20:12] [Alignment] User prefers recommended canonical types with rare custom exceptions.
- [2026-03-10T20:12] [VitalFinding] Real duplication mostly comes from the old `Notes` bucket.
- [2026-03-10T20:12] [Constraint] `Session Log` structure must stay compatible with resume parsing.
```

**Recommended canonical types for single/sub changes**

```markdown
Alignment
Decision
VitalFinding
Constraint
Risk
VerificationShortcut
```

Type policy:

- prefer canonical types first
- allow custom types only when none of the recommended labels are clear enough
- custom labels must stay short, concrete, and rare

**Refactor B: Root handover uses the same typed memory model**

```markdown
## Working Memory (Stable)

### Key Sub-Changes
- `changes/<sub-name>/` - what this sub-change covers

### Key Files
- `path/file` - what it contains, why it matters

### Durable Memory (Typed, Timestamped)
- [2026-03-10T20:12] [Alignment] User approved the current phase split.
- [2026-03-10T20:12] [CoordinationDecision] Phase 2 depends on Phase 1 schema stabilization.
- [2026-03-10T20:12] [Dependency] Archive root only after all sub-changes are done.
```

**Recommended canonical types for root changes**

```markdown
Alignment
CoordinationDecision
Dependency
CrossChangeFinding
Constraint
Risk
VerificationShortcut
```

Root-specific intent:

- `CoordinationDecision` records durable orchestration choices across phases/sub-changes
- `Dependency` records ordering or coupling future agents must preserve
- `CrossChangeFinding` records findings that matter across more than one sub-change
- `Constraint`, `Risk`, and `VerificationShortcut` stay available because root changes still need them

**Refactor C: Guidance teaches promotion instead of category-splitting**

```markdown
Promote into Durable Memory only if the fact is still useful after the current batch ends.

Keep in Session Log:
- what happened this batch
- current next action
- review-round outcomes
- temporary reminders

Promote into Durable Memory:
- approved direction changes
- lasting constraints or caveats
- resume-critical findings
- enduring verification shortcuts
```

**Refactor D: HOWTOs become task-focused instead of SKILL-overlapping**

```text
sspec-handover SKILL
  ├── when to trigger handover
  ├── full procedure (handover/tasks/project/spec-doc)
  └── quality checks

write-handover HOWTO
  ├── short router / entry point
  ├── points to write-handover-log
  ├── points to write-handover-memory
  └── points to handle-obsolete-memory
```

Focused HOWTO roles:

- `write-handover-log` = atomic batch log format, what belongs in `Accomplished` / `Next` / log notes
- `write-handover-memory` = durable-memory promotion rules, single-vs-root type choice, concise examples
- `handle-obsolete-memory` = when to mark obsolete vs when deletion is acceptable

### Data Flow

```
New information appears during work
  │
  ├── Current-batch progress / next step / review outcome
  │     └── write to `Session Log`
  │
  ├── Cross-session durable knowledge
  │     └── write to `Durable Memory (Typed, Timestamped)`
  │
  └── Project-wide learning beyond this change
        ├── write to `Durable Memory` if change-specific
        └── ALSO append to `.sspec/project.md` if repo-wide
```

**Note**: The important behavioral change is the first triage question. Agents should decide
"durable or batch-local?" before choosing a type label.

### Key Logic

- `Session Log` remains the only place that must carry the real immediate `Next` action.
- Durable memory entries use one-line typed bullets by default; continuation lines are allowed only
  when the rationale or caveat is not understandable in one line.
- When durable memory becomes obsolete, default to marking it obsolete with a timestamp; delete only
  obvious noise, duplicates, or placeholder residue with no historical value.
- Existing `Decision` / `Notes` content in older handovers is not migrated automatically; the new
  format applies to newly generated templates and future edits.
- Root handovers and single/sub handovers share the same section shape but not the same recommended
  type vocabulary.
- HOWTOs should add detail only where the SKILL deliberately stays compact; they should not become a
  second copy of the full handover phase contract.
- No parser change is required unless a later enhancement wants machine-readable durable-memory
  summaries.

### Scope Summary
| File | Change |
|------|--------|
| `src/sspec/templates/change/handover.md` | Replace `Decisions` + `Notes` with one typed durable-memory section and updated inline examples |
| `src/sspec/templates/change-root/handover.md` | Apply the same typed memory model while preserving root-only coordination sections |
| `src/sspec/templates/skills/sspec-handover/SKILL.md` | Rewrite handover guidance around durable-vs-batch triage, canonical types, and rare custom labels |
| `src/sspec/howto/write-handover.md` | Convert to a lightweight router that points to focused handover HOWTOs |
| `src/sspec/howto/write-handover-log.md` | Add focused HOWTO for `Session Log` writing |
| `src/sspec/howto/write-handover-memory.md` | Add focused HOWTO for durable-memory writing |
| `src/sspec/howto/handle-obsolete-memory.md` | Add focused HOWTO for obsolete-memory handling |
