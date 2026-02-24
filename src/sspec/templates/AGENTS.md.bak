<!-- SSPEC:START -->
# .sspec Agent Protocol

SSPEC_SCHEMA::{{SCHEMA_VERSION}}

## 0. Overview

SSPEC is a document-driven AI collaboration framework. All planning, tracking, and handover lives in `.sspec/`.

**Goal**: Any Agent resumes work within 30 seconds by reading `.sspec/` files.

```
.sspec/
├── project.md     # Identity, conventions, notes
├── spec-docs/     # Formal specs (architecture, APIs)
├── changes/<n>/   # spec.md | tasks.md | handover.md [+ reference/]
├── requests/      # User intent records
├── tmp/           # Informal drafts for review
└── asks/          # Q&A decision evidence
```

---

## 1. Agent Procedure

`read(project.md)` → classify input → dispatch:

```
DISPATCH(input):
  directive(d)    → exec(d)                # → Shortcuts 4.3
  request(r)      → scale(r) → workflow(r) # → Change 2.1; includes attached request files
  resume(change)  → load(change) → continue
  micro(≤3f,≤30m,obvious) → do_directly
  new_work        → scale(input) → workflow # → Change 2.1

load(change):
  read(handover→tasks→spec) → output(status, progress, next_3_actions)

scale(input):
  micro  → do_directly | track_in_request
  single → create_change(standard)
  multi(>1w|>15f|>20t) → create_root

BACKGROUND (always active during session):
  discovery    → persist(handover.md)    # → Memory 2.3
  long_session → checkpoint(handover.md) # compression is silent
  uncertain    → @ask                    # → Consult 2.2; 30s < rework
  session_end  → handover_full()         # → Memory 2.3; MANDATORY
  user_rejects → STOP → assess_scope    # → Reactive 3
```

Unfamiliar subsystem? → read `spec-docs/` | `project.md` | `<change>/handover.md` first

---

## 2. Core Workflows

### 2.1 Change Lifecycle

Changes live in `.sspec/changes/<n>/` (dir name: `<time>_<change-name>`).

| File | Contains |
|------|----------|
| spec.md | Problem (A), Solution (B), Implementation plan (C), Blockers (D) |
| tasks.md | Task checklist `[ ]`/`[x]` + progress tracking |
| handover.md | Session memory + agent working memory across sessions |

**Request → Change Workflow** (most common path):

1. **Assess scale** → Micro (≤3 files, ≤30min: do directly) / Single (standard) / Multi (>1 week OR >15 files OR >20 tasks: `--root` + sub-changes)
2. **Create**: `sspec change new --from <request>` (auto-links + derives name) or `sspec change new <name>`
3. **Research**: First-principles — find the real problem, not the surface ask. Read project.md + relevant code. Unclear → use `@ask`. Wrong direction costs more than extra questions.
4. **Design**: Fill spec.md A/B/C. Complex → `@ask` about splitting
5. **Confirm**: `@ask` to present plan. Wait for approval before executing
6. **Execute**: Implement. Update tasks.md after **each** task — not in batches

**Locate**: `sspec change find <name>` (fuzzy) | `sspec change list` | read `.sspec/changes/`

**Status transitions**:

| From | Trigger | To |
|------|---------|-----|
| PLANNING | user approves | DOING |
| DOING | all tasks `[x]` | REVIEW |
| DOING | missing info | BLOCKED |
| DOING | scope changed | PLANNING |
| BLOCKED | resolved | DOING |
| REVIEW | accepted | DONE |
| REVIEW | needs changes | DOING |

**FORBIDDEN**: PLANNING→DONE, DOING→DONE, BLOCKED→DONE — never skip REVIEW.

📚 `sspec-change` SKILL (MUST consult): doc standards, CLI ref, multi-change, edge cases.

### 2.2 Consultation (@ask)

When Agent needs user input, route by archival need:

| Need persistent record? | Tool | Use when |
|--------------------------|------|----------|
| Yes | `sspec ask create <topic>` → fill → `sspec ask prompt <file>` | Plan approval, architecture choice, direction decision |
| No | Agent env question tool | Session-end check, quick yes/no |

**Default to sspec ask** when uncertain — record > no record. Batch related questions in one ask.
Long content MUST NOT go in ASK file → write in `.sspec/tmp/`, reference in QUESTION.

**Mandatory ask points** (when user specified `@sspec-ask`): plan completion before execution, tool call rejected (ask reason), all tasks complete before ending.

📚 Triggers, patterns, error handling: `sspec-ask` SKILL

### 2.3 Memory & Handover

Knowledge persists at four levels:

| Level | Carrier | Write timing |
|-------|---------|-------------|
| Record | `requests/` + `asks/` | On creation (CLI-managed) |
| Change | `handover.md` | During work + session end |
| Project | `project.md` Notes | Promoted from handover at session end |
| Spec | `spec-docs/` | On architecture changes → `sspec doc new` |

**End-of-session handover (mandatory)**:
1. Update handover.md: Accomplished, Next Steps, References & Memory
2. Promote project-wide learnings to `project.md` Notes
3. Verify tasks.md progress matches reality

**Mid-session** (proactive): Important decision, key file discovered, session long (>50 exchanges) → append to handover.md References & Memory immediately. Self-check: "Would I struggle to reconstruct this after context compression?" → if yes, write it NOW.

📚 Knowledge routing, handover quality, memory lifecycle: `sspec-memory` SKILL

---

## 3. Rejection Protocol

When user disagrees (`@argue` or equivalent) — **STOP immediately**. Assess scope:

| Rejection scope | Action |
|----------------|--------|
| Implementation detail | Update tasks.md only |
| Design decision | Revise spec.md B + regenerate tasks.md |
| Requirement itself | Revise spec.md A, mark PIVOT in D, transition DOING→PLANNING |

📚 Edge cases and assessment guidance: `sspec-change` SKILL

---

## 4. Reference

### Template Markers in `<change>` template files

| Marker | Meaning | Action |
|--------|---------|--------|
| `<!-- @RULE: ... -->` | Inline standards reminder | Read and follow. DO NOT delete |
| `<!-- @REPLACE -->` | Anchor for first edit | Replace with content |
| `[ ]` / `[x]` | Task todo / done | Update as work progresses |

**Authority**: SKILLs are source of truth. @RULE markers are quick reminders.

### Scope Quick Reference

| Scope | Location | Key actions |
|-------|----------|-------------|
| Changes | `.sspec/changes/<n>/` | `sspec change new/find/list/archive/validate` |
| Requests | `.sspec/requests/` | `sspec request new/find/link`. Request = "I want X" → Change = "Here's how we do X". Micro → track in request directly |
| Spec-Docs | `.sspec/spec-docs/` | `sspec doc new "<name>"`. For knowledge too complex for project.md AND surviving beyond any single change. 📚 `write-spec-doc` SKILL |
| Asks | `.sspec/asks/` | `sspec ask create/prompt/list`. Decision evidence chain |

### Directive Shortcuts

Optional convenience shortcuts. Agent MUST respond to equivalent natural language identically.

| Shortcut | Equivalent intent | Procedure |
|----------|-------------------|-----------|
| `@change <n>` | "Work on change N" | **Existing**: load per procedure §1. **New**: create via §2.1 |
| `@resume` | "Continue last work" | Same as `@change` for current active change |
| `@handover` | "Save progress, end session" | Execute handover (Section 2.3) |
| `@sync` | "I coded without tracking, update status" | Identify changes → update tasks.md/handover.md → suggest REVIEW if complete |
| `@argue` | "I disagree" | **STOP immediately** → assess rejection scope (Reactive Rules Section 3) |

---

## 5. SKILL System

SSPEC core SKILLs: `sspec-change`, `sspec-memory`, `sspec-ask`, `sspec-mdtoc`, `write-spec-doc`, `write-patch`

**Progressive disclosure**: `SKILL.md` is the entry point; reference subfiles contain detailed standards and examples.

```
<skills-dir>/<name>/
├── SKILL.md     ← Read this first
└── references/  ← Contains detailed standards, examples, patterns
```

**Critical**: When `SKILL.md` instructs to read a reference file (e.g. "read [doc-standards](./references/doc-standards.md)") → you **MUST** read it. Stopping at `SKILL.md` alone misses essential standards.
For large md, use `sspec-mdtoc` for pre-scanning.
<!-- SSPEC:END -->
