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

Edit the generated file (3-5 sentences):

```markdown
## Problem
Users cannot reset passwords. 50+ support tickets/month.

## Initial Direction
Email-based reset link, 15min expiry.
```

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
   # AI fills: "Store reset tokens in Redis or DB?"
   sspec ask prompt .sspec/asks/<file>
   # Human answers → AI receives decision
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
| `sspec ask prompt <file>` | Answer AI questions |
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
└── .claude/skills/              # AI skill definitions
```

Supported tools: Claude Code, Cursor, Windsurf, GitHub Copilot, VS Code Copilot

---

## Core Concepts

### Request (Human-Created)

Entry point for work. 3-5 sentences describing intent.

```bash
sspec request new <idea>
```

Examples:
- "Auth latency 5s, user complaints increasing"
- "OAuth support needed for Google/GitHub"
- "Payment webhooks returning 500, Stripe logs failing"

AI converts requests to changes.

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

Mid-session updates triggered when context window approaches limits (>50 exchanges).

### Spec-doc (AI-Generated)

Project-level design documents for patterns transcending individual changes:

- API standards
- Architecture decisions
- Schema definitions

Created via `sspec doc new` when AI identifies project-wide patterns. Auto-referenced during change execution.

### sspec ask (AI-to-Human Query)

Synchronous clarification mechanism.

AI creates:
```bash
sspec ask create <topic>
```

Human responds:
```bash
sspec ask prompt .sspec/asks/<file>
```

Usage examples:
- Design choice resolution ("Redis vs Postgres caching?")
- Destructive operation confirmation ("Delete test data?")
- Multiple valid approaches ("Auth strategy A vs B?")

Related questions batched in single ask.

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

# Respond to AI queries
sspec ask prompt .sspec/asks/<file>

# Status check
sspec project status
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
sspec request archive <n>
```

---

## Compatibility

Works with AI tools supporting file-based context:

- Claude Code (agentic CLI)
- Cursor (AI-first editor)
- Windsurf (flow-based coding)
- GitHub Copilot (in-editor)
- VS Code Copilot (chat + inline)

Requires `AGENTS.md` at project root (auto-loaded).

---

## When Not to Use

Skip for:
- Typo corrections
- 5-minute bug fixes
- Configuration adjustments

Use for work requiring:
- Multi-session continuity
- Decision documentation
- Cross-file coordination

---

## Usage Examples

### SaaS Development

```
Workflow:
├── sspec request new stripe-integration
├── @change stripe-integration
│   └── AI: design → ask webhook handling → implement
├── @handover (session end)
├── @resume (next session)
└── sspec change archive stripe-integration (completion)

Project structure:
├── project.md: Next.js + Postgres + Railway
├── spec-docs/api-standards.md: REST conventions
└── changes/stripe-integration/: feature history
```

### Open Source Maintenance

```
Workflow:
├── GitHub issue → sspec request new issue-245
├── @change issue-245
├── AI: analyze → ask compatibility → implement
└── REVIEW → verify → archive

Project structure:
├── requests/: issue triage
├── changes/: active work
└── spec-docs/architecture.md: contributor reference
```

### Consulting

```
Workflow:
├── Client requirement → sspec request new payment-fix
├── @change payment-fix
├── AI: design → ask environment → implement
└── handover documents billable work

Project structure:
├── project.md: client conventions, deployment
├── changes/: deliverable tracking
└── handover.md: handoff-ready documentation
```

---

## FAQ

**Spec.md population?**
AI-automated. Human writes 3-5 sentence request.

**When to execute `sspec change new`?**
Rarely manual. AI executes after `@change <request>` directive.

**Handover.md maintenance?**
AI-managed. Updates during work, automatic at `@handover`. Human reads on resume.

**Disagreement handling?**
Issue `@argue` directive for re-planning, or reject approval `@ask`.

**Usage without AI?**
Possible but suboptimal. Framework designed for AI collaboration.

---

## License

MIT

---

## Links

- Repository: [github.com/frostime/sspec](https://github.com/frostime/sspec)
- Issues: [GitHub Issues](https://github.com/frostime/sspec/issues)

---

**Summary**: Requests capture intent, AI implements and maintains memory, humans control via checkpoints.
