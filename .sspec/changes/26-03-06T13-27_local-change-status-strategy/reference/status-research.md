# Research: local change status strategy

## Context

Question: should sspec add a richer `change status` view, and if so, how should it work without pulling sspec toward openspec-style global schema orchestration?

## Current reality

- `sspec project status` exists and prints a coarse active-change overview.
- `sspec change find <name>` exists and is mainly a locator + metadata view.
- `sspec change status` is commented out in `src/sspec/commands/change.py`, but `_show_change_detail()` still exists.
- Current change truth lives in local markdown files:
  - `spec.md` frontmatter + Section A/B
  - `tasks.md` checkboxes + Progress section
  - `handover.md` stable memory + newest-first Session Log

## Observations

### 1. sspec and openspec have different centers of gravity

openspec centers the CLI/schema as the runtime controller.
sspec centers the change directory as the local collaboration unit.

If sspec adopts a global workflow YAML just to enable `status --json`, it weakens one of its clearest product boundaries: open a change folder, read the files, understand the work.

### 2. `find` and `status` serve different questions

- `find`: Where is this change? Which file paths should I open?
- `status`: What is the current state? What should happen next?

That means the commands are complementary rather than duplicates.

### 3. Markdown parsing is only dangerous when parsing free prose

Full semantic parsing of arbitrary markdown is brittle.
Bounded extraction from stable anchors is acceptable.

Low-risk anchors already exist or can be kept stable:

- `spec.md` frontmatter `status`
- `tasks.md` checkbox counts
- `tasks.md` Progress summary
- `handover.md` `Updated`
- newest Session Log header + `Next`
- root `Sub-Change Status` table

## Option comparison

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A | Keep only `find` + open files manually | Minimal, no new parsing | No quick dashboard; old `change status` references stay misleading |
| B | Restore human-readable `change status [name]` as read-only local summary | Fits sspec philosophy; useful for both user and agent; no new source of truth | Needs bounded markdown extraction |
| C | Add `change status --json` now | Good for automation/subagents | Premature for current scale; invites pressure for more machine API surface |
| D | Add local `.state.yaml/.json` per change | Very easy machine reads later | Introduces dual-truth drift unless carefully synchronized |
| E | Add openspec-style global schema/instructions engine | Powerful runtime orchestration | Pulls sspec away from doc-driven local change model |

## Recommendation

Recommend **Option B now**, explicitly reject **Option E**, and defer **C/D**.

Design principle:

> Documents remain the source of truth. CLI status is a read-only projection over a small, stable subset of those documents.

That gives sspec a local dashboard without converting the CLI into a workflow controller.

## Suggested staged roadmap

### Stage 1: Human-readable local dashboard

Add/restore:

```bash
sspec change status <name>
```

Possible fields:

- name / path
- status
- progress (`done/total`)
- linked request(s)
- updated timestamp
- latest Session Log title/tags
- latest `Next`
- root-only: sub-change snapshot

### Stage 2: Optional JSON only when justified

Only add:

```bash
sspec change status <name> --json
```

if there is real demand from IDE integration, subagent automation, dashboards, or scripted validation.

### Stage 3: Derived local cache only if needed

If performance or tooling ever requires it, a per-change `.state.json` can be added as a derived cache, not as the authoritative source.

## Design constraints for any implementation

1. No global schema/controller file.
2. No parsing of arbitrary prose for semantic meaning.
3. Status output must be reconstructible from local change files.
4. `find` remains the path-oriented command; `status` remains the state-oriented command.
5. Missing optional sections should degrade gracefully.
6. Status output should include relative links back to source files so agents can open the real detail view.

## Follow-up adjustments after user review

- Include source file links in status output to encourage jumping to original details.
- If implemented, add only a short hint in `AGENTS.md` / relevant SKILLs; avoid turning it into a new mandatory workflow step.
- Keep this change well-referenced so later agents understand why openspec / `--json` / `.state.yaml` came up in the discussion.
