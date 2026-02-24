# sspec

**S**spec **S**ynthesizes **P**rograms from **E**xplicit **C**ontext

A spec-driven framework for AI-assisted development.

---

## Problem

AI-assisted development suffers from memory loss:
- Session 3: "Why Redis over Postgres for caching?" — AI doesn't remember the decision
- Session 7: "Which file contains auth logic?" — AI suggests multiple conflicting locations
- Session 14: New chat window — AI requires full project re-explanation

**Root cause**: AI lacks cross-session persistence. Each conversation starts from zero context.

**Solution**: Project state lives in files. AI reads context from disk, maintains memory in handover files, uses `@ask` for human checkpoints.

---

## Workflow

### 1. Create Request

```bash
sspec request new forgot-password
```

Edit the generated file.

### 2. Delegate to AI

In AI chat:

```
@change forgot-password
```

AI workflow:

1. **Analyze** — Assess scale (micro/single/multi-change)
2. **Clarify** via `sspec ask`:
   ```bash
   sspec ask create token-storage
   # AI fills question: "Store reset tokens in Redis or DB?"
   # User fills answer in the generated Python file
   sspec ask prompt .sspec/asks/<file>.yml
   # AI receives decision
   ```
3. **Create change** — AI executes `sspec change new --from forgot-password`
4. **Write spec** — AI populates `spec.md`:
   - Section A: Problem (quantified: "50+ tickets/month, $200 cost")
   - Section B: Solution ("Email reset, 15min TTL, bcrypt")
   - Section C: Implementation (file-level breakdown)
5. **Request approval** — AI shows plan via `@ask`
6. **Implement** — Upon approval, AI writes code
7. **Track progress** — AI marks `[x]` in `tasks.md` per completed task
8. **Maintain memory** — AI records decisions in `handover.md`

### 3. Session End

AI automatically executes `@handover` before terminating, updating memory files.

### 4. Session Resume

```
@resume
```

AI reads `handover.md` → restores context → continues work.

---

## Responsibility Matrix

### Human

| Action | Trigger |
|--------|---------|
| `sspec request new <idea>` | Capture idea (3-5 sentences) |
| `@change <n>` | Initiate work on request |
| `@resume` | Resume previous session |
| Answer AI questions | After Agent runs `sspec ask create` |
| Approve plan | Respond to design `@ask` |
| Verify implementation | Review REVIEW-status changes |

### AI

| Responsibility | Replaces |
|----------------|----------|
| Execute `sspec change new` | Manual change creation |
| Populate `spec.md` sections | Writing formal specifications |
| Maintain `tasks.md` | Manual task tracking |
| Update `handover.md` | Re-explaining decisions |
| Execute `sspec ask create` | Deciding when to ask |
| Reference `project.md`, `spec-docs/` | Reminding AI of conventions |
| Archive completed work | Manual organization |

Decision-making remains human-controlled via `@ask` checkpoints. Administrative overhead handled by AI.

---

## Installation

```bash
pip install sspec
# or
uv tool install sspec
```

## Project Setup

```bash
cd project-root
sspec project init
```

Generated structure:

```
project/
├── AGENTS.md                    # AI protocol (auto-loaded by tools)
├── .sspec/
│   ├── project.md               # Identity, conventions, memory
│   ├── spec-docs/               # Architecture docs (AI-generated)
│   ├── changes/                 # Active work (AI-managed)
│   ├── requests/                # Intent captures (human-created)
│   └── asks/                    # AI-to-human queries
└── .xxx/skills/              # AI skill definitions
```

---

## Core Concepts

### Request (Human-Created)

Entry point for work. Describe intent as clearly as possible.

```bash
sspec request new <idea>
```

Reference the request file in conversation and tell Agent "sspec@change from this request".

### Change (AI-Managed)

AI's work unit:

```
.sspec/changes/<timestamp>_<n>/
├── spec.md      # Problem, solution, implementation plan
├── tasks.md     # Checklist, updated during execution
└── handover.md  # Session memory, decisions, references
```

Status flow:
```
PLANNING → DOING → REVIEW → DONE
    ↑       ↓
    └─── BLOCKED
```

Scale assessment (AI-determined):
- **Micro** (≤3 files, ≤30min): No change ceremony, direct execution
- **Single** (1 week, ≤15 files): Standard change
- **Multi** (>1 week, >15 files): Root change + sub-changes

### Handover (AI Memory)

Cross-session persistence mechanism:

- **Background**: Change purpose
- **Accomplished**: Session work
- **Next Steps**: Resumption point
- **References & Memory**:
  - **Key Files**: Critical file paths
  - **Decisions & Rationale**: Design choices and reasoning
  - **Gotchas & Context**: Edge cases, risks, implicit knowledge

Updated during work and at session end. Read-first on `@resume`.

### Spec-doc

Project-level design documents transcending individual changes:

- API standards
- Architecture decisions
- Schema definitions

Tell Agent to create document `sspec@doc`, Agent calls CLI and auto-fills.

### sspec ask (AI-to-Human Query)

Synchronous clarification mechanism.

AI creates:
```bash
sspec ask create <topic>
```

Generates question document, user fills answer in the document.

Agent runs command to get answer:
```bash
sspec ask prompt .sspec/asks/<file>.yml
```

> [!note]
> This process depends on tool call approval
> User should answer before `sspec ask prompt` tool runs

---

## Directives

Chat-based workflow control:

| Directive | Function |
|-----------|----------|
| `@status` | Project overview (active changes, blockers) |
| `@change <n>` | Load change context (handover → tasks → spec) |
| `@resume` | Continue last active change |
| `@handover` | Persist state (auto-executed at session end) |
| `@sync` | Reconcile code changes with tasks.md |
| `@ask` | Suggest AI consultation (AI decides execution) |
| `@argue` | Halt current approach |

---

## CLI Reference

### Human-Executed Commands

```bash
# Capture intent
sspec request new <idea>

# Status check
sspec project status

sspec request archive
sspec change archive
```

### AI-Executed Commands

```bash
# Change management
sspec change new --from <request>
sspec change new <n>
sspec change new --root           # Multi-change
sspec change list
sspec change archive <n>

# Documentation
sspec doc new "<topic>"
sspec doc new "<topic>" --dir
sspec doc list

# Query system
sspec ask create <topic>
sspec ask list

# Request management
sspec request list
sspec request link <req> <change>
```

---

## Compatibility

Works with AI tools supporting file-based context. `AGENTS.md` is created and filled during project init.

---

## License

AGPL-V3.0
