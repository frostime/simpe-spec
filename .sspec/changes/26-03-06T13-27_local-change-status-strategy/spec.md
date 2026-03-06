---
name: local-change-status-strategy
status: DONE
type: ""
change-type: single
created: 2026-03-06T13:27:19
reference:
  - source: "wip/analysis-report.md"
    type: "doc"
    note: "Original openspec vs sspec comparison; source of status/json/state-file suggestions"
  - source: ".sspec/tmp/gpt对report的解释.md"
    type: "doc"
    note: "Prior discussion interpreting report suggestions and tradeoffs"
  - source: "src/sspec/commands/change.py"
    type: "doc"
    note: "Current find command, commented status skeleton, and detail helper"
  - source: "src/sspec/services/change_service.py"
    type: "doc"
    note: "Current bounded change parsing and progress extraction logic"
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

# local-change-status-strategy

## A. Problem Statement
sspec currently has a coarse `project status` view and a path-oriented `change find <name>` view,
but no dedicated local dashboard for a single change. A commented-out `change status` skeleton still
exists in code, which indicates unresolved design tension rather than a purely missing feature.

The unresolved question is not just "should we add a status command", but:

- what information belongs in local change files versus CLI output
- whether status should be human-readable only or machine-readable too
- how to avoid pushing sspec toward openspec-style global schema orchestration

User requirement: keep the change as the local, cohesive unit of truth; avoid a global YAML/controller;
avoid brittle full-markdown parsing; and clarify whether a richer status view is actually worth adding.

<!-- @RULE: Quantify impact. Format: "[metric] causing [impact]".
Simple: single paragraph. Complex: split "Current Situation" + "User Requirement". -->

## B. Proposed Solution
### Approach

Do not adopt openspec's global schema/controller model.

Instead, formalize a **local change dashboard** concept:

- change documents remain the source of truth
- `find` stays path-oriented (where is the change?)
- `status` becomes state-oriented (what is the current state / next action?)
- CLI remains a read-only projection over a bounded set of stable markdown anchors

This yields a useful status view without turning sspec into a runtime workflow orchestrator.

Recommended rollout:

1. Restore/implement a human-readable `sspec change status <name>` first
2. Defer `--json` until there is real machine-consumption demand
3. Defer any local `.state.json/.yaml` cache until performance/tooling requires it

### Key Design

**Fix A: Clarify the product boundary**

Reject openspec-style global workflow YAML for sspec status. The status system should read from the
current change directory, not from a centralized controller file.

**Feat B: Define `change status` as a local dashboard**

`find` and `status` answer different questions:

- `find`: locate the change and show file paths / coarse metadata
- `status`: summarize current execution state and next action

The recommended human-readable status output should focus on a compact, resume-friendly summary:

```python
from dataclasses import dataclass


@dataclass
class SessionLogSummary:
    timestamp: str | None
    tags: list[str]
    title: str | None
    next_items: list[str]


@dataclass
class ChangeStatusSummary:
    name: str
    path: str
    status: str
    change_type: str
    tasks_done: int
    tasks_total: int
    updated: str | None
    linked_requests: list[str]
    latest_log: SessionLogSummary | None
    root_snapshot_rows: list[dict[str, str]] | None
    source_links: dict[str, str]
```

`source_links` should point agents back to original detail files instead of pretending the summary is sufficient:

- `spec`: change `spec.md`
- `tasks`: change `tasks.md`
- `handover`: change `handover.md`
- `research` (optional): design/reference note if it exists

**Feat C: Use bounded extraction, not prose interpretation**

Data flow for status generation:

```
sspec change status <name>
  │
  ├── resolve change path            -> existing fuzzy match logic
  ├── parse spec.md frontmatter      -> status, change type, references
  ├── parse tasks.md checkboxes      -> done / total
  ├── parse handover.md stable keys  -> Updated
  ├── parse newest Session Log entry -> title / tags / Next
  └── (root only) parse snapshot     -> Sub-Change Status rows
```

Rules:
- Parse only stable anchors (frontmatter, checkboxes, known headings, known table)
- Never attempt full semantic extraction from arbitrary prose
- Missing sections degrade to `None` / empty list instead of erroring
- Always show relative source paths so the agent can jump to the original detail view

**Refactor D: Add only light protocol guidance**

If `change status` is implemented, add a short hint in `src/sspec/templates/AGENTS.md` and/or the relevant SKILLs.
Keep it short: this is workflow sugar, not a new required phase.

Good level of guidance:
- mention that `change status <name>` is a quick local dashboard
- mention that agents should still open the source files when they need detail

Avoid turning SKILLs into long command manuals.

**Refactor E: Stage machine-readable output later, not now**

`--json` is a possible future extension, but not the default design target. It only becomes worthwhile
once sspec has recurring subagent / IDE / automation needs.

If JSON is later added, it should expose a summary of local change state rather than a new workflow graph.

### Scope Summary
| File | Change |
|------|--------|
| `src/sspec/commands/change.py` | Restore/add `change status` as a dedicated command |
| `src/sspec/services/change_service.py` | Add bounded extraction helpers for status summary |
| `src/sspec/core.py` | Optional summary type(s) if shared typing is useful |
| `src/sspec/templates/AGENTS.md` | Optional one-line hint for quick local dashboard usage |
| `src/sspec/templates/change/handover.md` | Keep stable anchors parse-friendly (already improved) |
| `src/sspec/templates/change-root/handover.md` | Keep root snapshot parse-friendly (already improved) |

See research notes: `reference/status-research.md`

