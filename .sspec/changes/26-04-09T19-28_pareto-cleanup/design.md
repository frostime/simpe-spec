---
change: "pareto-cleanup"
created: 2026-04-09T19:28:11
---

# Design: pareto-cleanup

## 1. Contract Boundary

| Area | Supported contract | Unsupported after cutover |
|------|--------------------|---------------------------|
| Continuity artifact | `memory.md` | `handover.md` |
| Resume pointer | `## State` | `## Session Log` |
| Root coordination view | `## Coordination` table | `## Sub-Change Status` |
| Historical trail surfaced by CLI | `## Milestones` | legacy session-log summaries |
| Lifecycle naming | `Clarify → Design → Plan → Implement → Review` | `Research` / `Handover` as current phase labels |

**Rule:** source templates, HOWTOs, parser, and status output must all agree on one contract. Old files may remain in the repo, but they are no longer a supported product schema.

---

## 2. Canonical `memory.md` Schema

### Single / Sub Change

```text
# Memory: <change>

**Updated**: <ISO minute>

## Git Baseline (Immutable)
## State
## Key Files
## Knowledge
## Milestones
```

### Root Change

```text
# Memory: <change>

**Updated**: <ISO minute>

## Git Baseline (Immutable)
## Coordination
| Phase | Sub-Change | Status | Blocker |

## State
## Key Files
## Knowledge
## Milestones
```

### Section Semantics

| Section | Meaning | Status priority |
|---------|---------|-----------------|
| `State` | Current focus + next action | **Highest** for resume/status |
| `Key Files` | Critical files not obvious from spec scope | Informational |
| `Knowledge` | Durable decisions / constraints / gotchas | Informational |
| `Milestones` | Append-only factual history, one line per session | Used for latest milestone |
| `Coordination` | Root-only sub-change status table | Root dashboard authority |

**Explicit non-goal:** the new schema does **not** reintroduce `Session Log`, `Working Memory`, or `Durable Memory` sections.

---

## 3. Summary Model

```python
@dataclass(frozen=True, slots=True)
class ChangeStatusSummary:
    name: str
    path: str
    status: str
    change_type: str
    tasks_done: int
    tasks_total: int
    updated: str | None
    linked_requests: list[str]
    memory_exists: bool
    state_lines: list[str]
    latest_milestone: str | None
    coordination_rows: list[dict[str, str]] | None
    source_links: dict[str, str]
```

### Design Choice

- Remove legacy summary fields entirely.
- Add `memory_exists` so the CLI can explicitly say when a change has no supported continuity artifact.
- Keep the model aligned with the one supported contract instead of silently carrying two schemas forever.

---

## 4. Parsing Strategy

### Content Source Selection

```text
change_path
  └─ if memory.md exists → read memory.md
```

### Extraction Pipeline

```text
content
  ├─ extract_updated()
  ├─ extract_state_lines()
  ├─ extract_latest_milestone()
  └─ extract_coordination_rows()
```

### Decision Table

| File shape | `memory_exists` | `state_lines` | `latest_milestone` | `coordination_rows` |
|-----------|------------------|---------------|--------------------|---------------------|
| New single `memory.md` | `True` | parse `## State` | parse last bullet in `## Milestones` | `None` |
| New root `memory.md` | `True` | parse `## State` | parse last bullet in `## Milestones` | parse `## Coordination` table |
| Legacy-only `handover.md` | `False` | `[]` | `None` | `None` |

### Parsing Rules

- Ignore blank lines, headings, and HTML comments when collecting `State` lines.
- `Milestones` uses the **last valid bullet** as the latest milestone.
- `Coordination` parsing follows normal markdown-table parsing rules.
- `handover.md` is ignored by the supported parser path.

---

## 5. `sspec change status` Output Contract

### New-format Single Change

```text
Change Status
  name / status / progress / updated

Source Files
  - spec
  - tasks
  - memory

Current State
  - <state lines>     OR "not recorded"

Latest Milestone
  - <latest milestone> OR "not recorded"
```

### New-format Root Change

```text
Change Status
  ...

Current State
  - ...

Latest Milestone
  - ...

Coordination
| Phase | Sub-Change | Status | Blocker |
```

### Unsupported Legacy Change

```text
Change Status
  ...

Memory
  unsupported / missing

Current State
  not recorded

Latest Milestone
  not recorded
```

### Rendering Rule

```text
render new-format blocks always
if memory_exists is False:
    show explicit unsupported/missing-memory note
```

The CLI is intentionally not a historical-format reader anymore. When users need old context, they read the raw files.

---

## 6. Documentation / Template Closure

### Required wording updates

| File group | Before | After |
|-----------|--------|-------|
| `resume-change.md` | start from `Session Log` | start from `State`; for old changes read raw files directly |
| `write-memory.md` | implicit continuity model | explicit `State` authority + `Milestones` append-only usage |
| `sspec-implement` | "record in Session Log" | "record durable facts in Knowledge, session facts in Milestones" |
| `sspec-design` metadata/examples | `after research`, `Research → ... → Handover` | `after clarify`, `Clarify → ... → Review`, with `memory.md` as continuity artifact |

### Constraint

Keep ordinary English words like "research" when they mean investigation work, but remove them as **phase names** or **lifecycle labels**.

---

## 7. Regression Test Matrix

| Case | Fixture shape | Expected result |
|------|---------------|-----------------|
| New single change summary | `memory.md` with `State` + `Milestones` | service summary returns `state_lines` + latest milestone |
| New root change summary | `memory.md` with `Coordination` table | service summary returns coordination rows |
| Legacy single change summary | `handover.md` only | service summary marks `memory_exists=False` and returns no parsed continuity data |
| Legacy root change summary | `handover.md` only | service summary marks unsupported old shape without coordination rows |
| New single status command | CLI invoke | prints `Current State` / `Latest Milestone` |
| New root status command | CLI invoke | prints `Coordination` table |
| Legacy status command | CLI invoke | prints explicit missing/unsupported memory note, not legacy session-log output |

---

## 8. Verification Flow

```text
edit source files
  → uv pip install -e .
  → uv run pytest tests/test_change_service.py tests/test_change_command.py -q
  → uv run ruff check src/
  → uv run sspec project update
  → tmp sandbox: new single + new root + old-shape status checks
```

**Acceptance bar:** after this flow, source templates, generated self-host copies, CLI rendering, and tests all describe the same post-vnext contract: `memory.md` only.
