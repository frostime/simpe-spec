# Handover Standards

Quality criteria for handover.md — serving both cross-session handover AND intra-session working memory.

---

## Core Fields

| Field | Purpose | ❌ Bad | ✅ Good |
|-------|---------|--------|---------|
| Background | One-sentence overview of this change | "Doing auth" | "JWT+Redis cache: 5s→<1s auth response" |
| Accomplished | This session's concrete work | "Made progress" | "Redis pool + middleware done, tests passing" |
| Current Status | Match spec.md frontmatter status | (missing) | "DOING — 60% complete" |
| Next Steps | 1-3 specific file-level actions | "Continue" | "1. Code `src/auth/jwt.py:refresh_token()`" |

### Background Field Rules

- **Write once** on first session. Update only if scope fundamentally changes.
- Keep to 1-3 sentences. Details belong in spec.md, not here.
- Purpose: instant orientation for any agent loading this change.

---

## References & Memory Fields

These fields serve as the Agent's external working memory — surviving both context compression and session boundaries.

### Key Files

Critical file references for understanding and continuing this change.

**What to include**: Source files being modified, reference docs consulted, sspec ask records that drove decisions, related requests.

**Format**:
```markdown
- `src/auth/jwt.py` — token generation + validation logic
- `asks/260207_auth_approach.md` — confirmed JWT over session-based (user decision)
- `spec-docs/auth-system.md` — overall auth architecture reference
```

**When to write**: Immediately when a critical file is identified or discovered.

### Decisions & Rationale

Important decisions and the **full reasoning chain**. This is the most compression-vulnerable information — conclusions survive in memory but reasoning gets lost.

**Format (simple)**:
```markdown
- **Redis over Memcached**: Need per-key TTL + persistence. Memcached faster but no TTL granularity → stale tokens.
```

**Format (complex)**:
```markdown
#### 1. Why current approach fails?
**Root cause**: Format too strict for model output...
**Evidence**: 3/10 attempts produce valid format...

#### 2. Why SEARCH/REPLACE over alternatives?
**Three advantages**: (1) simpler format (2) model familiarity (3) token savings...
**Tradeoff**: Less precise than line-based diff, acceptable because...
```

**When to write**: Immediately when a non-trivial decision is made.

### Gotchas & Context

Non-obvious findings, edge cases, implicit knowledge from discussions, implementation cautions, risk warnings.

**Key principle**: Things you'd need to re-derive or re-discover if context were lost.

**When to write**: Immediately when discovered.

**Project-wide gotchas**: If a gotcha applies beyond this change → ALSO append to `project.md` Notes.

---

## Depth Guidance

**Thin memory** (simple change, ≤5 files, clear scope):
- 3-5 bullet points total across Key Files / Decisions / Gotchas
- Don't force content where there's nothing to record

**Rich memory** (complex change with many decisions, multi-file, design exploration):
- Organize Decisions into numbered items with sub-structure
- Include evidence and tradeoff analysis
- Cross-reference related ask records

Let content grow organically — don't pre-structure sections you don't need yet.

---

## Update Frequency

| Content | When to Write |
|---------|---------------|
| Key Files | Immediately when a critical file is identified |
| Decisions & Rationale | Immediately when a non-trivial decision is made |
| Gotchas & Context | Immediately when discovered |
| Accomplished & Next Steps | At session end (minimum); mid-session for long sessions |
| Background | Once, on first session |

**Core Rule**: If you'd struggle to reconstruct this information after context compression, write it down NOW.

---

## Quality Tests

Apply these tests at session end:

1. **Cross-session test**: A brand-new Agent reads only handover.md. Can they resume meaningful work within 30 seconds?
2. **Compression test**: If your context window were compressed right now and you lost the last 20 exchanges, could you continue working from handover.md alone?
3. **Decision trace test**: For each major decision in this change, can you find the "why" in handover.md without re-reading ask records?

If any test fails → update before ending session.

---

## Root Change handover.md

Root change handover has different emphasis:

| Standard Field | Root Variant |
|---------------|--------------|
| Background | What this root coordinates (1-3 sentences) |
| Accomplished | Work across sub-changes this session |
| Next Steps | Which sub-change to work on next, coordination needed |

Additional root-specific sections:

- **Sub-Change Status**: Table tracking each sub-change's progress
- **Cross-Phase Decisions**: Decisions affecting multiple sub-changes
- **Coordination Notes**: Shared interfaces, integration points, cross-phase gotchas

---

## Anti-Patterns

| Bad Practice | Correct Approach |
|--------------|------------------|
| Skip `@handover` at session end | **ALWAYS** handover before ending — no exceptions |
| Only update handover at session end | Update References & Memory **during** work |
| Record decision without reasoning | Capture full chain: problem → alternatives → conclusion |
| No file paths in Key Files | List files you'd need to re-find after compression |
| Forget project.md Notes | Append project-level learnings during @handover |
| Put architecture docs in project.md | project.md ≤10s scan; use spec-docs for detailed content |
| Copy entire discussion into handover | Summarize; link to ask record for full discussion |
