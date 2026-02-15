# Document Standards: spec.md & tasks.md

Quality criteria and filling guidance. Load when writing or reviewing these documents.

## Table of Contents

- [spec.md](#specmd) (L14-167) — Frontmatter, Sections A/B/C/D
- [tasks.md](#tasksmd) (L168-229) — Granularity, phases, verification
- [Optional Directories](#optional-directories) (L230-258) — reference/ etc.
- [Anti-Patterns](#anti-patterns) (L259-END)

---

## spec.md

### Frontmatter Schema

```yaml
---
name: <change-name>           # Auto-filled by CLI
status: PLANNING               # PLANNING | DOING | REVIEW | DONE | BLOCKED
type: ""                       # User-defined label (optional)
change-type: single            # single | sub | root
created: <iso-timestamp>       # Auto-filled by CLI
reference: null                # Array<{source, type, note?}> or null
---
```

**`change-type`**:
- `single`: Standalone change (default)
- `sub`: Part of a multi-change; must have `reference` linking to root
- `root`: Coordinator for sub-changes; spec.md C lists phases, not file-level tasks

**`reference`** field types:

| RefType | Meaning | Example |
|---------|---------|---------|
| `request` | Originating user request | `{source: "requests/26-02-05_auth.md", type: "request"}` |
| `root-change` | Parent root change (used in sub) | `{source: "changes/auth-root", type: "root-change"}` |
| `sub-change` | Child sub-change (used in root) | `{source: "changes/auth-phase1", type: "sub-change"}` |
| `doc` | Related spec-doc | `{source: "spec-docs/auth-system.md", type: "doc"}` |

### Section Standards

#### A. Problem Statement

**Standard**: Quantify impact. Format: "[metric] causing [impact]".

| Scenario | Approach |
|----------|----------|
| Simple change (≤5 files, clear scope) | Single paragraph. No sub-headings needed. |
| Complex change (ambiguous scope, multiple stakeholders) | Split into "Current Situation" + "User Requirement" sub-headings |

| ❌ Fail | ✅ Pass |
|---------|---------|
| "Need to refactor" | "Auth takes 5s → 12% conversion drop" |
| "Improve the UI" | "Form completion rate 23% → target 60%" |

#### B. Proposed Solution

**Standard**: Design document — What & Why. Includes approach, rationale, interface design, data models, and key logic.

**Core Purpose**: Describe the solution at the design level, not the execution level. This is where architectural decisions live.

**Required Sub-sections**:
- **Approach**: Core idea (1-3 paragraphs) + why this over alternatives
- **Key Changes**: Major modules, interfaces, dependencies affected

**Optional Sub-sections** (use when applicable):

| Sub-section | When to Include | Content |
|-------------|-----------------|---------|
| **Interface Design** | New/modified APIs, functions, classes | Function signatures, class structures, API contracts |
| **Data Model** | New/modified data structures | Core data types, state machines, data flow diagrams |
| **Key Logic** | Non-trivial algorithms or workflows | Pseudocode, edge cases, critical decision points |

**Complexity Scaling**:

| Complexity | Approach |
|------------|----------|
| **Simple** (≤5 files, clear logic) | Interface/data model inline in "Approach", brief mention |
| **Medium** (5-15 files, cross-module) | Dedicated sub-sections (### Interface Design, ### Data Model) |
| **Complex** (>15 files, architectural) | Detailed design in `reference/design.md` (follow write-spec-doc SKILL), link from Section B |

📚 **Detailed examples**: See [doc-examples.md](./doc-examples.md)

**What NOT to include in B**:
- Execution order (that's Section C)
- File-level task lists (that's Section C or tasks.md)
- Verification criteria (that's tasks.md)

#### C. Implementation Strategy

**Standard**: Execution plan — How to implement the design from Section B. Focus on phase division, file scope, dependencies, and risks.

**Core Purpose**: Break down the design (from B) into executable phases. Reference B's design decisions; don't re-describe them.

**Required Content**:

1. **Phase Division**: Organize work into logical phases
2. **File Scope per Phase**: Which files are affected + brief "what" (not detailed "how" — that's in tasks.md)
3. **Dependencies** (if applicable): What must complete first
4. **Risks & Mitigations**: Technical risks + how to handle them

**Complexity Scaling**:

| Change Type | Phase Content |
|-------------|---------------|
| **single/sub** | File-level mentions: `path/file.py` — create/modify, brief what |
| **root** | Milestone-level: one phase per sub-change, with goal/scope/dependencies |

**Key Principle**: **Reference Section B's design instead of repeating it**.

- ✅ "Implement Tool Interface per B"
- ✅ "按 B 中描述的三种场景逻辑实现"
- ❌ Re-listing all function signatures (that's in B)
- ❌ Re-describing core algorithm (that's in B)

📚 **Detailed examples**: See [doc-examples.md](./doc-examples.md)

**What NOT to include in C**:
- Interface definitions (that's Section B)
- Data model details (that's Section B)
- Core algorithm logic (that's Section B)
- Task-level verification criteria (that's tasks.md)

---

### spec.md vs tasks.md: When to Write What

**Core Distinction**:
- **spec.md** (Sections B + C) = **Design + Plan** (What to build, Why this way, How to organize phases)
- **tasks.md** = **Execution Checklist** (File-level tasks, check-off items, verification)

| Aspect | spec.md Section B | spec.md Section C | tasks.md |
|--------|-------------------|-------------------|----------|
| **Purpose** | Design doc — What & Why | Execution plan — Phase organization | Task checklist — What to do |
| **Granularity** | Approach + Interfaces + Data + Logic | Phase-level file mentions | File/function-level tasks |
| **Content** | Interface signatures, data models, core algorithms, design rationale | Phase division, file scope per phase, dependencies, risks | Actionable tasks (<2h each), verification criteria |
| **Why vs What** | Why this approach, what's the design | How to organize execution | What files to change, what to verify |
| **Complexity Scaling** | More design detail (interface/data/logic) as complexity grows | More phase breakdown as complexity grows | More task breakdown as complexity grows |
| **Relationship** | Standalone design document | References B, doesn't repeat design | References C phases, distills into tasks |

**Rule of Thumb**:
- If explaining **why** or **"how it works"** (design) → **spec.md Section B**
- If organizing **phases** and **file scope** (plan) → **spec.md Section C**
- If listing **actionable file-level steps** (checklist) → **tasks.md**
- If uncertain → Write in spec.md B first, distill execution in C & tasks.md later

📚 **Complete example flow** (Medium complexity): See [doc-examples.md](./doc-examples.md#complete-example-flow)

---

#### D. Blockers & Feedback

**Standard**: Dated, actionable entries.

```markdown
### Blocker (2026-02-10)
**Blocked**: Redis connection pooling | **Needed**: DevOps to provide host:port

### PIVOT (2026-02-12)
Direction change: switched from JWT to session-based auth. Reason: client requires server-side revocation.
```

---

## tasks.md

### Frontmatter

```yaml
---
change: "<change-name>"
updated: ""                  # ISO date, updated by agent
---
```

Root changes additionally have `change-type: root`.

### Task Granularity

| Change Type | Task Level | Example |
|-------------|-----------|---------|
| single / sub | File-level, <2h each | `- [ ] Create src/auth/jwt.py — refresh_token()` |
| root | Milestone-level (one per sub-change) | `- [ ] Phase 1 sub-change completed and archived` |

### Phase Structure

```markdown
### Phase 1: <name> 🚧
- [ ] Task description `path/file.py`
- [ ] Task description `path/file.py`
**Verification**: <how to verify this phase>
```

### Phase Emoji Convention

| Emoji | Meaning |
|-------|---------|
| 🚧 | In progress — actively working |
| ✅ | Done — all tasks completed and verified |
| ⏳ | Pending — not yet started |

### Progress Table

```markdown
**Overall**: 40%

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 | 100% | ✅ |
| Phase 2 | 30% | 🚧 |
| Phase 3 | 0% | ⏳ |
```

**Critical Rule**: Update percentage and status after **EACH** task completion, not in batches. `sspec change status` auto-calculates from checkboxes — keep tasks.md as the single source of truth.

### Verification Criteria

Each task (or at minimum each phase) must have explicit pass criteria:

| ❌ Vague | ✅ Specific |
|----------|------------|
| "Add tests" | "Add tests in `tests/test_jwt.py`, cover: valid token, expired token, malformed token" |
| "Update config" | "Add `REDIS_URL` to `.env.example`, verify `config.py` reads it with fallback" |

---

## Optional Directories

### reference/ (Design Iteration & Complex Designs)

**Purpose**: Store detailed design documents, research notes, and architectural exploration.

**Common Files**:

| File | Purpose | When to Create |
|------|---------|----------------|
| `design.md` | Detailed architecture spec (follow write-spec-doc SKILL) | Complex changes (>15 files, cross-module) |
| `research.md` | Code investigation, dependency analysis, technical findings | Before design, after code exploration |
| `comparison.md` | Technology/approach evaluation (pros/cons, tradeoffs) | Multiple viable solutions exist |
| `benchmark.md` | Performance test results, stress test data | Performance-critical changes |
| `spec-v*.md` | Design iteration history | When pivoting direction |

**Use Cases**:
1. **Complex Design**: Create `design.md` (follow write-spec-doc SKILL) → Link from spec.md Section B
2. **Research**: Explore codebase → Document findings in `research.md` → Inform design in spec.md B
3. **Iteration**: Draft in reference/ → `@ask` → Revise → Finalize to spec.md → Keep reference/ for record

**Workflow**:
- **Complex**: `reference/design.md` → spec.md B links it → Keep for record
- **Research**: `reference/research.md` → summarize in spec.md A (Problem) or B (Approach)
- **Comparison**: `reference/comparison.md` → final choice in spec.md B
- **Simple changes** (≤5 files): Skip reference/ entirely

---

## Anti-Patterns

| Bad Practice | Correct Approach |
|--------------|------------------|
| Missing interface design in B | Always define interfaces/data models in Section B, even if brief |
| Repeating interface signatures in C | Reference Section B ("implement interface per B"), don't duplicate |
| Repeating core logic in tasks.md | tasks.md lists tasks, not logic — logic lives in spec.md B |
| No file mentions in C | Each phase should mention key files affected, even if not exhaustive |
| Task list in spec.md C | Section C organizes phases, tasks.md has the checklist |
| Mark `[x]` without testing | Done = coded **AND** verified |
| Stay DOING when blocked | BLOCKED immediately + document in D |
| Skip REVIEW status | DOING → REVIEW → DONE, no shortcuts |
| Batch progress updates | Update tasks.md after **each** task |
| Over-structure simple changes | Simple = brief inline design in B, flat phase list in C |
| Forget reference field | Always link to originating request |
