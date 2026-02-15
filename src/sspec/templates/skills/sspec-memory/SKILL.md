---
name: sspec-memory
description: "Knowledge persistence across sessions — routing, handover quality, long-session memory, project-level notes. Consult when deciding where knowledge goes, performing handover, or managing memory proactively."
metadata:
  author: frostime
  version: 1.0.0
---

# SSPEC Memory Skill

Knowledge persistence and handover management. Where knowledge goes, how it's maintained, when to write it.

## Playbook

| You need to... | Action |
|----------------|--------|
| Decide where knowledge belongs | Knowledge Routing below |
| Fill or review handover.md | Read [handover-standards] |
| Perform end-of-session handover | @handover Procedure below |
| Preserve important info mid-session | Long Session Memory below |
| Promote learning to project level | Memory Lifecycle below |
| Create/update a spec-doc | 📚 Consult `write-spec-doc` SKILL |

---

## Memory Hierarchy

sspec maintains knowledge at four levels. Each has different scope and lifecycle:

| Level | Carrier | Lifecycle | Write Timing | Example |
|-------|---------|-----------|-------------|---------|
| **Record-level** | `requests/` + `asks/` | Permanent audit trail | On creation (CLI-managed) | Why we started this work; what user decided |
| **Change-level** | `handover.md` | Created with change, archived with change | During work + session end | "Redis chosen over Memcached for per-key TTL" |
| **Project-level** | `project.md` Notes & Conventions | Project lifetime | Promoted from handover at session end | "2026-02-10: ruff format breaks multiline strings in templates" |
| **Specification-level** | `spec-docs/` | Survives beyond any single change | On architecture changes | Full auth system design document |

### Record-Level: requests/ and asks/

These are often overlooked but serve critical memory functions:

- **requests/**: The "why" record. When a change is archived, the originating request remains as evidence of user intent. Future agents can trace back: "Why did we build this?" → read the request.
- **asks/**: The decision evidence chain. `handover.md` Decisions & Rationale captures conclusions; the original ask `.md` preserves the full discussion process (question framing, user's exact words, context at time of decision).

**Practical use**: When resuming work or reviewing past decisions, check `asks/` for the discussion record, not just handover.md for the summary.

---

## Knowledge Routing

Where does a piece of knowledge go?

| Test | → Destination |
|------|---------------|
| One-liner, applies across all work | `project.md` **Conventions** |
| Project-wide gotcha, preference, learning | `project.md` **Notes** (append with date) |
| Needs paragraphs, diagrams, or sections | `spec-docs/` → 📚 `write-spec-doc` SKILL |
| File path critical to current work | `handover.md` **Key Files** |
| Non-trivial decision with reasoning | `handover.md` **Decisions & Rationale** |
| Edge case, implicit knowledge, gotcha | `handover.md` **Gotchas & Context** |
| Why we're doing this work at all | Already in `requests/` — just link via reference field |
| User's exact decision on a design question | Already in `asks/` — link in handover Key Files |

**Decision principle**: If unsure between handover and project.md → write to handover first. Promote to project.md at session end if it's truly project-wide.

---

## @handover Procedure

### End-of-Session (Mandatory)

Before ending any session:

1. **Accomplished**: List what got done this session (specific, not "made progress")
2. **Next Steps**: 1-3 specific file-level actions for the next agent
3. **References & Memory**: Review and update all three sub-sections:
   - Key Files — all critical files listed?
   - Decisions & Rationale — non-obvious choices captured with full reasoning?
   - Gotchas & Context — edge cases, risks, implicit knowledge recorded?
4. **Project-level promotion**: Append project-wide learnings to `project.md` Notes
5. **Progress sync**: Verify tasks.md progress percentage matches reality

### Mid-Session (Proactive)

**Trigger** — update handover.md immediately when ANY of:
- Session getting long (>50 exchanges or complex multi-file work)
- Important decision just made with non-trivial reasoning
- Key file discovered that future work depends on
- Design tradeoff resolved after discussion

**Action**: Append to "References & Memory" only. Quick, targeted, no ceremony.

**Principle**: If you'd struggle to reconstruct info after context compression, write it to handover NOW. Context compression is silent — you won't notice lost information until it's too late.

---

## Long Session Memory Management

Context window has hard limits; compression is silent and lossy — Agent won't notice lost context.

### When to Act

- Session feels long (>50 exchanges)
- Multi-file complex work in progress
- Extensive design discussion has occurred
- You're about to switch between files/topics

### What to Do

1. Write key decisions, file refs, and gotchas to handover.md "References & Memory"
2. Continue working — handover.md is the safety net against compression
3. If previously-discussed info seems missing from memory, **re-read handover.md**

### Memory Check

At any point during a long session, quickly verify:

- Any important decision in recent messages not yet in handover?
- Any key file paths discussed but not recorded in Key Files?
- Any design rationale that would be hard to reconstruct?
- Any gotcha or edge case discovered but not written down?

→ If yes to any: update handover.md now. Quick append, no ceremony.

---

## Memory Lifecycle

```
Discovery
    ↓
Write to handover.md immediately
    ↓
At session end: promote project-wide items to project.md
    ↓
Next session start: prune stale handover entries
    ↓
If architecture-level: create/update spec-doc
```

### Promotion Rules

| From | To | Condition |
|------|----|-----------|
| handover.md Gotchas | project.md Notes | Applies beyond this change |
| handover.md Decisions | project.md Conventions | Becomes a project-wide rule |
| handover.md (complex) | spec-docs/ | Needs paragraphs, diagrams, or is referenceable across changes |
| project.md Notes | project.md Conventions | Confirmed as permanent rule |
| project.md Notes | (pruned) | Becomes outdated or irrelevant |

### Session Start Review

When resuming work:

1. Read `project.md` — check Notes for recent additions
2. Read `handover.md` — especially References & Memory
3. Check if any handover entries are now stale (resolved blockers, completed tasks)
4. Clean up stale entries to keep handover focused

---

## handover.md Quality Standards

Full quality criteria in [handover-standards.md](./references/handover-standards.md).

Quick quality test:
1. **Cross-session**: Can a new Agent resume in <30 seconds?
2. **Intra-session**: If context were compressed right now, could you continue from handover.md alone?

If either answer is "no" → update handover immediately.

---

## References

| When | Load |
|------|------|
| Filling or reviewing handover.md | [handover-standards.md](./references/handover-standards.md) |
| Creating or updating spec-docs | 📚 `write-spec-doc` SKILL |
