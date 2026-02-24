---
name: sspec-handover
description: "Save session state. Update handover.md, project.md, and spec-docs index. MANDATORY at session end, recommended mid-session."
metadata:
  author: frostime
  version: 3.1.0
---

# SSPEC Handover

Persist session knowledge so any agent can resume within 30 seconds.

**Handover is a lifecycle participant, not just cleanup.** It preserves context across sessions, context compressions, and agent switches.

---

## When to Trigger

### End of Session (MANDATORY)

Before ending ANY session, perform the full procedure below. No exceptions.

### Mid-Session (Proactive)

Update handover.md Working Memory when:
- Session is long (>30 exchanges or complex multi-file work)
- Important decision just made with non-trivial reasoning
- Key file discovered that future work depends on
- Design tradeoff resolved after discussion
- About to switch between major phases (e.g. design → plan)

**Rule**: If you'd struggle to reconstruct info after context compression → write it NOW.

## Procedure

### 1. Update handover.md

**This Session → Accomplished**: List specific work done (not "made progress").
**This Session → Next Steps**: 1-3 specific file-level actions for next agent.

**Working Memory**:
- **Key Files**: All critical file paths listed?
- **Decisions**: Non-obvious choices captured with reasoning?
- **Notes**: Edge cases, gotchas, risks recorded?

### 2. Sync tasks.md

Verify tasks.md progress percentage matches reality. All completed tasks marked `[x]`.

### 3. Promote to project.md (if applicable)

Two promotion targets:

**Notes section**: If any discovery applies beyond this change → append with date.
- Format: `- YYYY-MM-DD: <learning>`

**Spec-Docs Index section**: If spec-docs were created or updated during this session → update the index.
- Format: `- [name](spec-docs/<file>) — one-line description`

### 4. Suggest spec-doc update (if applicable)

If the change produced architectural knowledge (new interfaces, data models, patterns):
- `@ask` user: "This change produced knowledge about X. Should I create/update a spec-doc?"
- If yes → use `write-spec-doc` SKILL

### 5. Quick Quality Check

| Test | Pass? |
|------|-------|
| New agent reads only handover.md — can resume in <30s? | |
| If context compressed right now — could you continue from handover.md alone? | |
| For each major decision — can you find the "why" in handover? | |

If any test fails → update handover before ending.

## handover.md Quality

**Thin** (simple change, ≤5 files): 3-5 bullet points across Working Memory sections.
**Rich** (complex change, many decisions): Numbered items with sub-structure, evidence, tradeoff analysis.

Let content grow organically — don't pre-structure sections you don't need yet.

### Anti-Patterns

| Bad | Good |
|-----|------|
| Skip handover at session end | ALWAYS handover — no exceptions |
| Only update at session end | Update Working Memory DURING work |
| Record decision without reasoning | Capture full chain: problem → alternatives → conclusion |
| No file paths in Key Files | List files you'd need to re-find after compression |
| Put architecture docs in project.md | project.md ≤10s scan; use spec-docs for detailed content |
