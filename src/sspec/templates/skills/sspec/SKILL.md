---
name: sspec
description: Core decision-making for SSPEC workflow. Complexity assessment (micro/single/multi), knowledge routing, reference field usage, and edge case handling. Consult when starting work or unsure where something belongs.
metadata:
  author: frostime
  version: 7.1.0
---

# SSPEC Skill

**When to consult**:
- Starting new work → Complexity assessment below
- "Where does this knowledge go?" → Knowledge routing below
- Filling spec.md / tasks.md / handover.md → [references/quality-standards.md](./references/quality-standards.md)
- Multi-change coordination → [references/multi-change.md](./references/multi-change.md)
- Quick checkpoint checks → [references/checklists.md](./references/checklists.md)

**Note**: Core protocol (directives, status transitions, cold start) is in AGENTS.md. This SKILL provides decision depth.

---

## Complexity Assessment

**FIRST DECISION** when receiving work: how big is this?

### Micro (no change needed)

ALL of: ≤3 files, ≤30 minutes, no design decisions, trivially reversible.

**Action**: Do directly, or track in request file (`## Plan` / `## Done`). No change ceremony.

**Examples**: Fix typo, adjust config, add import, rename variable, update version.

### Single Change (default)

ALL of: ≤1 week, ≤15 files in one subsystem, ≤20 tasks, low risk.

**Examples**: Bug fix, add API endpoint, refactor one module, update docs.

### Multi-Change (complex)

ANY of: >1 week, >15 files across subsystems, >20 tasks, high risk.

**Pattern**: Root change (`--root`) for coordination + sub-changes for execution.

**When uncertain**: Use `@ask` to consult user on splitting approach.

📋 Multi-change structure, workflow, and linking → [references/multi-change.md](./references/multi-change.md)

---

## Knowledge Routing

Where does a piece of knowledge belong?

| Question | Destination |
|----------|-------------|
| One-liner, applies across all work? | `project.md` **Conventions** |
| Learned gotcha/preference, project-wide? | `project.md` **Notes** (append with date) |
| Needs paragraphs, diagrams, sections? | `spec-docs/` |
| Only relevant to current change? | `handover.md` **Conventions Discovered** |

**Examples**:

| Knowledge | → Goes to |
|-----------|-----------|
| "Use snake_case for Python" | project.md Conventions |
| "pip install -e . needed after template change" | project.md Notes |
| "Auth uses JWT + Redis with token rotation" | spec-docs/auth.md |
| "This change's cache key: auth:{id}" | handover.md |

**Notes lifecycle**: Append → Promote to Conventions if confirmed → Prune if outdated → Graduate to spec-doc if complex.

---

## Reference Field

Track relationships in spec.md frontmatter:

```yaml
reference:
  - source: "requests/26-02-05T14-00_add-auth.md"  # Relative to .sspec/
    type: "request"
    note: "Original feature proposal"               # Optional
```

| Type | Meaning | Direction |
|------|---------|-----------|
| `request` | Originating request | change → request |
| `root-change` | Parent coordinator | sub-change → root |
| `sub-change` | Child execution unit | root → sub-change |
| `doc` | Related spec-doc | change → spec-doc |

---

## Edge Cases

### Partial Blockers

- Blocked tasks are dependencies → Status = BLOCKED, document in spec.md D
- Blocked tasks are non-critical → Continue others, document in spec.md D
- Ambiguous → Consider splitting into two changes

### REVIEW Across Sessions

Keep status = REVIEW. Update handover: "Awaiting review since \<date\>". Can start other work meanwhile. Next session: prompt user for review result first.

### Mid-Flight Rejection (@argue)

1. **STOP** immediately
2. **Clarify** scope: implementation detail → tasks.md only; design → revise spec.md B; requirement → revise spec.md A + PIVOT in D
3. **Re-plan** if scope changed significantly: DOING → PLANNING
4. **Wait** for explicit approval

### Multiple Active Changes

≤2 changes in DOING simultaneously. Switch via: `@handover` current → `@change <other>` → read handover.md.

### Design Iteration Loop

spec.md keeps getting revised → Version to `reference/spec-v1.md` → Brainstorm in `reference/` → Iterate via `@ask` → Write final to spec.md.

---

## Further Reading

| Need | Reference |
|------|-----------|
| Quality standards for spec.md / tasks.md / handover.md | [references/quality-standards.md](./references/quality-standards.md) |
| Multi-change structure, workflow, linking | [references/multi-change.md](./references/multi-change.md) |
| Quick checklists for checkpoints | [references/checklists.md](./references/checklists.md) |
