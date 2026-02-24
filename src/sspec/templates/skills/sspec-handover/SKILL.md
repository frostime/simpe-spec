---
name: sspec-handover
description: "Save session state. Update handover.md and project.md Notes. Use at session end or when context is getting long."
metadata:
  author: frostime
  version: 2.0.0
---

# SSPEC Handover

Persist session knowledge so any agent can resume within 30 seconds.

---

## When to Trigger

### End of Session (MANDATORY)

Before ending ANY session, perform the full procedure below.

### Mid-Session (Proactive)

Update handover.md Working Memory when:
- Session is long (>50 exchanges or complex multi-file work)
- Important decision just made with non-trivial reasoning
- Key file discovered that future work depends on
- Design tradeoff resolved after discussion
- About to switch between files/topics

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

If any discovery applies beyond this change:
- Append to `project.md` Notes section with date
- Format: `- YYYY-MM-DD: <learning>`

### 4. Quick Quality Check

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
