---
name: sspec-align
description: "Structured, efficient agent-user synchronization at decision points. Formalized exchange over prose."
metadata:
  author: frostime
  version: 12.0.0
---

# SSPEC Align

`@align` is how agents synchronize with users at decision points — **efficiently, structurally, and with minimal friction**. The goal is 5-second scan, instant decision.

**Core principle**: Every @align must answer three questions — What happened? What needs deciding? What are the options? — in structured format, not prose.

---

## 1. Levels (When)

| Level | Agent behavior | Typical situations |
|---|---|---|
| `report` | Structured summary, **keep going** | Plan done, progress update, low-risk confirmation |
| `gate` | Structured summary, **stop and wait** | Design done, implement complete, blocker, scope change, irreversible action |

**Rule**: If safe progress depends on a user decision, the agent MUST use `gate`. Otherwise prefer `report`.

---

## 2. Presentation (How)

@align information MUST use structured format. Prose-style @align is an anti-pattern.

### Required format elements

- **Tables** for comparisons, options, scope summaries
- **Labeled items** for decisions, risks, constraints
- **Code blocks** for interfaces, commands, config
- **Explicit decision point** — atomic, confirmable question at the end

### Anti-patterns

```
❌ Prose @align:
"I've been thinking about the design and I believe we should
split the service into three parts. The first handles auth,
the second manages sessions, and the third provides the API.
What do you think?"

✅ Structured @align:
## Design Gate

| Component | Source → Target | Responsibility |
|-----------|----------------|----------------|
| Auth      | `handlers/monolith.py` → `services/auth.py` | Authentication |
| Session   | `middleware/chain.py` → `services/session.py` | State mgmt |
| API       | (new) `api/surface.py` | Thin wrapper |

**Rationale**: Testability + independent deployment
**Risk**: Migration complexity (feature flag mitigates)

→ Proceed with this split?
```

### Context and decision separation

1. Present structured context in normal output (tables, diagrams, labeled items)
2. Use `question-like` tool ONLY for the final concise ask
3. MUST NOT stuff analysis, tradeoff tables, or multi-paragraph context into the question tool payload

---

## 3. Tools (What)

- If a built-in `question`-like tool is available → use it for the final ask
- Otherwise, if `sspec tool ask` is available → use it as fallback
- Otherwise → state the question clearly in output, end turn

For large context, write analysis to `.sspec/tmp/` and link it instead of pasting inline.

Fallback tool usage reference: `sspec tool ask --prompt`

---

## 4. After Align — Records

Alignment without record = information lost on next session.

| What changed | Where to record |
|---|---|
| Design confirmed/revised | `spec.md` / `design.md` |
| Plan confirmed/revised | `tasks.md` |
| Direction changed, key decision made | `handover.md` Durable Memory |
| User feedback received | `handover.md` Session Log (new `user-feedback` entry) |
| Scope/design change after gate | `revisions/NNN-*.md` + `tasks.md` |

**No separate ask record is required.** Put the decision in its natural home.
