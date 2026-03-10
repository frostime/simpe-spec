# Howto Integration — Research Analysis
*Created: 2026-03-10T14:17*

---

## 1. Current State Overview

### Three Knowledge Layers (as-is)

| Layer | Format | Load cost | Scope |
|-------|--------|-----------|-------|
| `AGENTS.md` | ~220-line protocol | Always in context (managed block) | Full workflow + shortcuts + rules |
| SKILL files | ~50-150 lines each | On-demand (read before phase) | Full lifecycle phase contract |
| HOWTO docs | ~15-30 lines each | On-demand (via CLI) | **Single concrete procedure** |

### Current HOWTO Inventory (8 built-in HOWTOs)

| Name | Purpose |
|------|---------|
| `find-change` | Locate the right change directory |
| `get-current-time` | Use `sspec tool now` when timestamps matter |
| `make-subagent-audit` | Subagent-based code review with git diff |
| `read-long-mdfile` | Use `mdtoc` before reading large markdown |
| `update-change-status` | State machine for `spec.md` status transitions |
| `use-sspec-ask` | Record decisions with `sspec ask` correctly |
| `use-sspec-cli` | Common sspec CLI command reference |
| `write-howto` | Write directive, agent-facing HOWTO docs |

### How AGENTS.md currently embeds rules

AGENTS.md is a **monolithic protocol** that inlines everything:
- Phase workflow with lifecycle diagram
- Background rules (timestamps, handover triggers, etc.)
- @align decision tree (which tool for which question)
- Directive shortcuts table
- CLI Quick Reference table
- SKILL references list

This works, but creates two tensions:
1. **Token cost**: Agents must re-read the full managed block every session even for simple tasks
2. **Stale rules**: Inline rules like "use `sspec tool now` instead of guessing" duplicate what HOWTOs already express more precisely

---

## 2. Q1: Can HOWTO optimize sspec agent efficiency?

**Answer: Yes, strongly — in four distinct ways.**

### 2.1 Token Budget Reduction
Approximate token cost comparison for targeted tasks:

| Task | Current path | Approx tokens consumed | With HOWTO |
|------|-------------|------------------------|------------|
| Find a change | Read AGENTS.md + reasoning | ~300 tokens | `sspec howto find-change` → ~60 tokens |
| Update status | Parse §2 Status Guardrails in AGENTS.md | ~150 tokens | `sspec howto update-change-status` → ~80 tokens |
| Use `sspec ask` | Parse §3 Alignment section | ~200 tokens | `sspec howto use-sspec-ask` → ~60 tokens |
| Get timestamp | Parse Background rules bullet | ~300 tokens | `sspec howto get-current-time` → ~40 tokens |

For an agent mid-task who already has AGENTS.md compressed out of context, HOWTOs
provide **direct surgical retrieval** instead of forcing a full re-read.

### 2.2 Lazy/On-Demand Knowledge Loading
Current SKILL loading pattern: Agent loads full SKILL file at phase start, gaining
~500-1000 tokens that are ~60-80% irrelevant to the specific sub-task at hand.

HOWTO enables **composable, just-in-time guidance**:
```
Agent mid-implementation:
  "I need to update the status" → sspec howto update-change-status (80 tokens)
  "I need to ask user about X" → sspec howto use-sspec-ask (60 tokens)
```
vs. loading sspec-implement (500+ tokens) to find those answers.

### 2.3 Discovery vs. Memorization
Current AGENTS.md CLI Quick Reference is a static table agents must memorize
or re-read. `sspec howto list` provides a **dynamic, self-describing** discovery
surface that works even as new HOWTOs are added.

Agent doesn't need to know HOWTOs exist up front — `sspec howto list` serves as
a browse-able knowledge index for operational procedures.

### 2.4 Agent-First Design Alignment
HOWTOs were designed with agent-friendly plain text output from day one. The
`===== HOWTO/<name> =====` separator format enables multi-read batching:
```
sspec howto find-change use-sspec-cli update-change-status
# Returns three docs with clear separator boundaries in one CLI call
```
This is more token-efficient than separate tool calls or reading from AGENTS.md.

---

## 3. Q2: Can HOWTO integrate with AGENTS.md + built-in SKILLs?

**Answer: Yes — with well-defined integration patterns.**

### 3.1 Integration Pattern: Point-of-Need References in AGENTS.md

Replace inline rule prose with HOWTO references at exact decision moments:

| AGENTS.md location | Current inline text | HOWTO integration |
|---|---|---|
| §1 Background rules | "Current date/time uncertain → use sspec tool now" | → `sspec howto get-current-time` |
| §1 Background rules | "Uncertain → `@align`" | → `sspec howto use-sspec-ask` |
| §1 Resume tip | Handover read order | → `sspec howto find-change` (for resume scenario) |
| §3 Alignment | Full @align decision tree | Slim prose + "→ `sspec howto use-sspec-ask` for recording decisions" |
| §5 CLI Reference | Full table | Keep for overview, add `sspec howto list` row |

This pattern keeps AGENTS.md as a **workflow navigator** while HOWTOs hold the
**operational details**.

### 3.2 Integration Pattern: HOWTO System Discovery Block

AGENTS.md currently has no mention of HOWTOs. Adding a dedicated discovery
reference in §5 Reference would make agents aware of the system:

```markdown
### HOWTO System
Targeted operational guides — shorter than SKILLs, more specific than AGENTS.md.
- Discover all: `sspec howto list`
- Read one: `sspec howto <name>`
- Create project HOWTO: `sspec howto new <name>`
```

### 3.3 Integration Pattern: SKILL → HOWTO Delegation

SKILL files currently carry some content that HOWTOs also cover, or could cover:

| SKILL file | Overlapping/delegatable content | HOWTO to reference |
|---|---|---|
| `sspec-research` | How to find the change to resume | `find-change` |
| `sspec-research` | How to read large markdown files | `read-long-mdfile` |
| `sspec-implement` | How to update change status | `update-change-status` |
| `sspec-handover` | How to use sspec tool now for timestamps | `get-current-time` |
| `sspec-handover` | How to create sspec ask decisions | `use-sspec-ask` |
| `sspec-align` | When to use sspec ask and how | `use-sspec-ask` |

Rather than duplicating instructions, SKILLs can say:
`"→ For the exact procedure, read: sspec howto <name>"`

### 3.4 Gap Analysis: Missing HOWTOs

Comparing AGENTS.md §1/§2/§5 and SKILL content reveals procedures that exist
as prose rules but lack HOWTO documents:

| Missing HOWTO | Source | Priority |
|---|---|---|
| `resume-change` | AGENTS.md §1 resume tip + Session Log pattern | High |
| `write-handover` | sspec-handover SKILL procedure | High |
| `do-align` | AGENTS.md §3 + sspec-align SKILL | Medium |
| `scale-assessment` | AGENTS.md §2 Scale Assessment table | Medium |
| `write-request` | sspec-research: request file creation | Low |

---

## 4. Proposed Change Scope

### Tier 1: AGENTS.md Template Updates (High Value)
1. Add `### HOWTO System` section to §5 Reference — one discovery block
2. Inline HOWTO pointers at 3-5 key decision points in §1 + §3
3. Add `sspec howto list` entry to CLI Quick Reference table

### Tier 2: New Builtin HOWTOs (Fill Critical Gaps)
4. `resume-change.md` — Exact 30-second resume procedure from handover.md
5. `write-handover.md` — How to write effective handover entries

### Tier 3: SKILL File Integration (Medium Value)
6. `sspec-research` SKILL: reference `find-change` and `read-long-mdfile`
7. `sspec-handover` SKILL: reference `get-current-time` and `write-handover` (new)
8. `sspec-implement` SKILL: reference `update-change-status`

### Scale Assessment
- Files touched: ~8-10 (AGENTS.md, 2 new HOWTOs, 3 SKILL files, spec.md templates)
- Effort: ≤1 week
- Change type: **Single**
- Risk: Low — all additive/reference changes, no logic changes

---

## 5. Anti-Patterns to Avoid

1. **Over-reference**: Don't add HOWTO pointers to every sentence in AGENTS.md. Only point to HOWTOs where the inline explanation was too brief to be actionable on its own.
2. **HOWTO sprawl**: Don't create HOWTOs for things that belong in AGENTS.md (workflow phases, status machine) or SKILLs (full lifecycle contracts). HOWTOs are for single concrete procedures.
3. **Duplication**: If adding a HOWTO reference in AGENTS.md, remove or shrink the inline text it replaces. Net cognitive load should decrease.
4. **SKILL weakening**: SKILLs should still be complete standalone documents. HOWTO references in SKILLs are supplementary, not replacements.
