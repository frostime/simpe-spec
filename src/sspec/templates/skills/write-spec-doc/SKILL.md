---
name: write-spec-doc
description: Create and maintain spec-docs — knowledge that code alone cannot adequately convey.
metadata:
  author: frostime
  version: 4.0.0
---

# Write Spec-Doc

## §1 Decision: When to Create

Code is the local ground truth. Spec-docs reduce the cost of recovering that ground truth for agents.

Two categories of knowledge that justify a spec-doc:

**A) In code, but scattered or implicit** — Cross-module architecture (call chains, data flows, layer relationships) distributed across many files; implicit specifications (state machines, invariants, schema contracts) that are implemented but never declared; design norms embedded in implementation choices; deliberate trade-offs whose rationale is invisible from outcomes alone. Reconstructing any of these demands expensive multi-file traversal and inference.

**B) Outside code entirely** — Platform rules, API quirks, business constraints, deployment assumptions. Code reflects these as outcomes, but the constraints themselves cannot be inferred from it. Example: a SQLite-over-Postgres choice is invisible without knowing the single-machine deployment constraint.

**Write-gate**: "If an agent read only the code (including comments), could they obtain this information — fully and without excessive effort?" Yes → don't create. No → create.

**Don't create** when:
- Code comments and type signatures adequately capture the design
- The topic is a single-file implementation detail
- The information duplicates framework/library documentation
- A one-liner in `project.md` Conventions or Notes is sufficient

## §2 Creation & Structure

### CLI

| Command | Use |
|---------|-----|
| `sspec doc new "<name>"` | Create single-file spec-doc from template |
| `sspec doc new "<name>" --dir` | Create multi-file spec-doc (directory + `index.md`) |
| `sspec doc list` | List all spec-docs with metadata |

Always use CLI to create — it scaffolds from template with correct frontmatter. Do not hand-create spec-doc files.

### Frontmatter

All fields required:

```yaml
---
name: Authentication System
description: JWT-based auth with refresh tokens and rate limiting
updated: 2026-01-27
scope:
  - /src/auth/**
  - /src/middleware/auth.ts
---
```

`scope` lists file paths (glob patterns) this spec-doc covers. Agents use it to locate relevant code. Include primary implementation and tests; omit generic utilities.

### Body

Start with `## Overview`. Beyond that, invent sections that fit the content. Example structures:

- **Architecture**: Overview → Architecture (diagram) → Components → Key Decisions
- **External constraints**: Overview → Constraints → Implications for Code → References
- **Design norms**: Overview → Principles → Rules (with examples) → Exceptions
- **Implicit spec**: Overview → Specification (state machine / invariants) → Implementation Notes

**Self-check for every section**: Would removing this force an agent into expensive reconstruction — multi-file traversal, cross-reference inference, external research, or guessing? If the agent could reach the same understanding from code alone at comparable cost, the section is redundant — cut it.

**Representation**: Complex relationships — call chains, state transitions, data flows, hierarchies — are more precisely conveyed through diagrams, pseudocode, or tables than through prose. Prefer semi-formal representations; they are easier for both agents and humans to verify and navigate.

### Registration

After creating a spec-doc, add an entry to `project.md` **Spec-Docs Index**. This is the agent's responsibility — the CLI does not automate it.

Format: `- [Name](spec-docs/<filename>.md) — one-sentence description`

### Linking from Changes

When a change creates or heavily depends on a spec-doc, add to the change's `spec.md` frontmatter:

```yaml
reference:
  - source: "spec-docs/<name>.md"
    type: "doc"
```

## §3 Traceability

Spec-docs are navigable knowledge graphs, not dead-end prose.

Every named entity — symbol, concept, external reference — MUST be traceable to its source (file path, URL, or another spec-doc). Establish the reference on **first mention**; subsequent uses within the same document need not repeat the link when the referent is unambiguous from context.

**Source types**: file path · URL · relative link to another spec-doc.
Omit line numbers — they go stale with code changes.

**BAD** — agent must search to resolve:
```markdown
The `AuthManager` handles token refresh. Rate limits follow Stripe's rules.
```

**GOOD** — traceable on first mention, concise thereafter:
```markdown
[`AuthManager`](/src/auth/manager.ts) handles token refresh.
Rate limits follow [Stripe's API rules](https://docs.stripe.com/rate-limits) (≤100 req/s per key).

... later in the same doc ...

`AuthManager` delegates to the refresh service when tokens expire.
```

## §4 Style

- **Imperative mood**: "Validate tokens" not "The system should validate"
- **Direct**: No filler ("It's worth noting...", "As mentioned earlier...")
- **Precise & quantified**: "Use Redis (5min TTL)" not "Consider using Redis"
- **Current state only**: No changelogs — history lives in git
- **Single topic per doc**: Don't mix unrelated concerns
- **File links**: Workspace-relative with forward slashes (`/src/core.py`). Same-level or sub-directory may use `./`

## §5 Lifecycle

### Updating

When a change modifies code covered by a spec-doc's `scope`:

1. Add task in tasks.md: "Update spec-doc `spec-docs/<name>.md`"
2. Update `updated` field and affected sections
3. Verify `scope` still matches actual files

Spec-docs MUST NOT be silently outdated by a change.

### Deprecation

Mark `deprecated: true` + `replacement: /path/to/new.md` in frontmatter. Move to `spec-docs/archive/`. Strip details; keep only: what it was, why deprecated, link to replacement.

### Multi-file Specs

Use `sspec doc new "<name>" --dir`. Entry point is `index.md` with overview + navigation. Each sub-file has its own frontmatter with narrowed scope. Cross-references use relative paths.
