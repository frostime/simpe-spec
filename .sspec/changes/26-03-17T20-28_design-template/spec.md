---
name: design-template
status: DONE
type: ''
change-type: single
created: 2026-03-17 20:28:51
reference:
- source: .sspec/requests/26-03-17T19-42_design-template.md
  type: request
  note: Linked from request
---
<!-- @RULE: Frontmatter
status: PLANNING | DOING | REVIEW | DONE | BLOCKED
change-type: single | sub
reference?: Array<{source, type: 'request'|'root-change'|'sub-change'|'prev-change' |'doc', note?}>

Sub-change MUST link root:
reference:
  - source: ".sspec/changes/<root-change-dir>"
    type: "root-change"
    note: "Phase <n>: <phase-name>"

Single-change common reference:
reference:
  - source: ".sspec/requests/<request-file>.md"
    type: "request"
  - source: ".sspec/changes/<change-dir>"
    type: "prev-change"
    note: "This change is a follow-up to <change-name> which introduced <feature/bug>. This change addresses <issue> with that feature/bug."
-->

# design-template

## A. Problem Statement

### Current Situation

sspec-design SKILL 的 Step 3A 将 Section B 的子节结构近乎固定为 `Interface Design / Data Flow / Key Logic / Scope Summary`。这套结构在 feature-code 场景下表现良好，但在其他场景下产生了两类问题：

1. **削足适履**：文档型 change（如 `refresh-spec-docs`）被迫造出 `DocTarget` TypedDict 来凑 Interface Design；批量重命名（如 `rename-ask`）直接跳过所有推荐子节只留 Scope Summary。
2. **隐性突破**：强模型在不适配场景下自发放弃推荐结构（如 `generalize-align-interaction` 用 Change A-E，`better-spec-design` 用完全自定义子节），但缺乏指引，弱模型则机械遵循产出低质量设计。

根本原因：SKILL 规定了"写什么子节"（Interface/DataFlow/KeyLogic），但 spec.md 的本质目的是让用户能预测执行结果。不同类型的 change，用户需要预测的维度不同，固定子节无法覆盖。

### User Requirement

重新设计 Step 3A 的子节选择机制：从"固定模板"改为"维度菜单 + 思维框架"，让 Agent 根据 change 性质选择最能帮助用户建立预期的设计维度。兼容 feature-code 场景的已有优势，同时大幅改善其他场景。

## B. Proposed Solution

### Approach

核心思路：**教 Agent 思考"用户需要预测什么"，而不是规定"必须写哪些子节"。**

spec.md 的本质是一份预测契约——用户读完后应能在脑中形成对执行结果的预期。不同 change 需要不同的预测维度：feature 需要接口和行为规格，文档 change 需要内容大纲，重构需要 before/after 对比和迁移路径，bug fix 需要结果预览。

改动集中在四个层面：

1. **SKILL 主体**：用"预测维度菜单 + 元思考引导"替换当前的固定子节推荐
2. **维度卡片 howto 化**：每个维度一个 howto，Agent 按需加载，避免 examples 文件的"范式效应"
3. **howto 分类机制**：给 howto 加 `type` 字段，`sspec howto list` 支持 `--type` 过滤
4. **spec.md 模板注释**：从列举固定子节改为指向 SKILL 的维度菜单

不改动模板文件结构（不拆分 `change/spec.md`），不改动 Root change 的 Step 3B。

为什么不用 examples 文件承载维度指引：examples 文件天然有"范式效应"——Agent 看到完整示例会倾向于复制结构，而不是真正思考。维度卡片作为独立 howto 存在，Agent 看到的是"你有这些积木可以用"，而不是"这个场景应该长这样"。

### Key Design

#### Change A: Predictability Dimensions Menu (SKILL core addition)

Introduce "predictability dimensions" in Step 3A. The SKILL body holds only the dimension overview table and meta-thinking guidance; each dimension's detailed writing spec lives in its own howto, loaded on demand.

Dimension overview in SKILL:

```markdown
## Predictability Dimensions

A spec is a prediction contract. Before writing Key Design, ask:
what does the user need to predict after reading this spec?

| Dimension | User's Question | When to Use |
|-----------|----------------|-------------|
| Outcome Preview | "What will it look like when done?" | Result is visually demonstrable (CLI output, UI, before/after) |
| Interface Contract | "What are the boundaries and contracts?" | Involves function signatures, APIs, type definitions |
| Structural Blueprint | "How are things organized?" | Involves module splits, file trees, component hierarchy |
| Behavioral Spec | "How does the system behave?" | Involves call chains, state machines, algorithm flows |
| Data Architecture | "What does the data look like and how does it flow?" | Involves schemas, storage structures, data pipelines |
| Content Outline | "What will the content structure be?" | Changes target documents, templates, or specs |
| Migration Path | "How do we get from here to there?" | Needs migration, compatibility, or rollback strategy |
| Impact Map | "What changes and what doesn't?" | Scope needs explicit boundaries |

Pick the 2-4 most relevant as Key Design sub-sections.
The menu is open — custom dimensions are allowed; briefly note the rationale in Approach.

Detailed writing spec and snippet examples for each dimension:
`sspec howto list --type design-dimension`
`sspec howto write-dim-<name>`
```

#### Change B: Dimension Howto Cards

One howto per dimension, `type: design-dimension`. Each card contains:

```markdown
---
name: write-dim-interface-contract
desc: "Design dimension: Interface Contract — function signatures, API contracts, type definitions"
type: design-dimension
---

# Interface Contract

## What It Answers
User's question: "What are the boundaries and contracts?"

## When to Choose
- Adding or modifying function signatures, class methods
- Defining or changing API endpoints
- Introducing new types/dataclasses/schemas
- Configuration format changes

## How to Write
Interfaces and type definitions MUST appear in fenced typed code blocks. Prose is supplementary only.

\`\`\`python
# Good — concrete, typed, annotatable
@dataclass
class ChangeRef:
    source: str             # workspace-relative path
    type: RefType           # 'request' | 'root-change' | 'sub-change'
    note: str | None = None  # optional annotation
\`\`\`

## Pairs Well With
- Behavioral Spec (interfaces define "what", behavior defines "how it's used")
- Impact Map (interface changes usually need explicit blast radius)
```

8 dimension howto files:
- `write-dim-outcome-preview.md`
- `write-dim-interface-contract.md`
- `write-dim-structural-blueprint.md`
- `write-dim-behavioral-spec.md`
- `write-dim-data-architecture.md`
- `write-dim-content-outline.md`
- `write-dim-migration-path.md`
- `write-dim-impact-map.md`

#### Change C: Howto Type Classification

Current howto frontmatter has only `name` and `desc`. Add optional `type` field:

```python
# src/sspec/services/howto_service.py — HowtoInfo extension
@dataclass
class HowtoInfo:
    name: str
    desc: str
    source: str
    path: Path
    type: str | None = None  # NEW: optional classification
```

Frontmatter parsing reads `type`:

```python
# In collect_howtos(), when building HowtoInfo
howto_type = meta.get('type')  # None if not present
```

`sspec howto list` gains `--type` filter:

```python
# src/sspec/commands/howto.py — list_cmd new parameter
@click.option('--type', 'howto_type', default=None, help='Filter by howto type')
def list_cmd(howto_type: str | None, ...):
    catalog = collect_howtos(sspec_root)
    items = catalog.items
    if howto_type:
        items = [h for h in items if h.type == howto_type]
    ...
```

List output adds a type column (shown only when typed howtos exist).

Existing howtos unaffected — `type` is optional, defaults to None.

#### Change D: Meta-thinking Guidance (Step 3A flow adjustment)

Lightweight guidance before Key Design writing. Not a separate step, no explicit output required:

```markdown
### Choosing Dimensions (internal thinking, not a separate output)

Before writing Key Design sub-sections, ask yourself:
1. What kind of change is this? (feature / fix / refactor / docs / ...)
2. What does the user need to predict to feel in control?
3. Which 2-4 dimensions best serve that prediction?

Your choice is reflected in the sub-section headings you use.
No need to write a "dimension selection rationale" — the structure speaks for itself.

Browse available dimensions: `sspec howto list --type design-dimension`
Read a specific dimension: `sspec howto write-dim-<name>`
```

#### Change E: Presentation Rules Restructure

Current Rule 1-4 are split into two tiers:

**Tier 1 — Universal rules (stay in SKILL, elevated to Key Design level)**:
- Scope Summary (≥3 files → `File | Change` table) — formerly Rule 3
- Item Labeling (≥3 independent items → label each Fix A / Feat B / ...) — formerly Rule 4

These apply regardless of which dimensions are chosen. They sit alongside `### Key Design` in the SKILL, not nested under a "Presentation Rules" section.

**Tier 2 — Dimension-specific writing norms (move into dimension howtos)**:
- "Interfaces/types → typed code block" (formerly Rule 1) → moves into `write-dim-interface-contract` and `write-dim-data-architecture` howtos
- "Flow/structure → ASCII diagram" (formerly Rule 2) → moves into `write-dim-behavioral-spec` and `write-dim-structural-blueprint` howtos

This way the SKILL stays lean: only universal rules that every spec must follow. Dimension-specific presentation norms live where they belong — in the dimension card the Agent loads when it picks that dimension.

#### Change F: spec.md Template Comment Update

```markdown
### Key Design
<!-- Choose 2-4 predictability dimensions as sub-sections (see SKILL.md).
Ask: what does the user need to predict to feel in control of this change?
Browse dimensions: `sspec howto list --type design-dimension`

Universal rules:
- ≥3 files → end with Scope Summary table (| File | Change |)
- ≥3 independent items → label each (Fix A / Feat B / Refactor C…)

Dimension-specific writing norms are in each dimension's howto. -->
```

#### Change G: Examples File Reorganization

Current `examples-single.md` (organized by complexity: Simple/Medium/Complex) splits into scenario-based files. Each file shows dimension selection and a complete spec example, clearly marked as reference not prescription.

- `examples-feature.md`: Feature/Bugfix scenario (Interface Contract + Behavioral Spec + Impact Map)
- `examples-docs.md`: Protocol/Template/Docs scenario (Content Outline + Impact Map)
- `examples-refactor.md`: Refactor/Migration scenario (Structural Blueprint + Migration Path + Impact Map)

`examples-root.md` stays unchanged.

### Scope Summary

| File | Change |
|------|--------|
| `src/sspec/templates/skills/sspec-design/SKILL.md` | Rewrite Step 3A: predictability dimensions menu, meta-thinking guidance, universal rules (Scope Summary + Item Labeling) elevated; remove old Presentation Rules section; Step 3B unchanged |
| `src/sspec/templates/change/spec.md` | Update Key Design comment: dimension menu + universal rules |
| `src/sspec/templates/skills/sspec-design/examples-single.md` | Delete (split into three scenario files below) |
| `src/sspec/templates/skills/sspec-design/examples-feature.md` | New: Feature/Bugfix scenario examples |
| `src/sspec/templates/skills/sspec-design/examples-docs.md` | New: Protocol/Template/Docs scenario examples |
| `src/sspec/templates/skills/sspec-design/examples-refactor.md` | New: Refactor/Migration scenario examples |
| `src/sspec/services/howto_service.py` | Add `type` field to `HowtoInfo`; parse `type` in `collect_howtos` |
| `src/sspec/commands/howto.py` | Add `--type` filter to `list_cmd`; show type column when applicable |
| `src/sspec/howto/write-dim-outcome-preview.md` | New: Outcome Preview dimension card |
| `src/sspec/howto/write-dim-interface-contract.md` | New: Interface Contract dimension card (absorbs old Rule 1 examples) |
| `src/sspec/howto/write-dim-structural-blueprint.md` | New: Structural Blueprint dimension card (absorbs old Rule 2 for structure) |
| `src/sspec/howto/write-dim-behavioral-spec.md` | New: Behavioral Spec dimension card (absorbs old Rule 2 for flow) |
| `src/sspec/howto/write-dim-data-architecture.md` | New: Data Architecture dimension card |
| `src/sspec/howto/write-dim-content-outline.md` | New: Content Outline dimension card |
| `src/sspec/howto/write-dim-migration-path.md` | New: Migration Path dimension card |
| `src/sspec/howto/write-dim-impact-map.md` | New: Impact Map dimension card (absorbs old Rule 3 Scope Summary as its primary form) |

### What Stays Unchanged

- Root change Step 3B (already has its own structure, no dimension-ization needed)
- `examples-root.md` (root scenario unchanged)
- Section A writing norms (Problem Statement unaffected)
- Template file structure, `change-root/spec.md`
- Existing howto files (`type` is optional, backward compatible)
- CLI commands (no new commands beyond `--type` filter on existing `howto list`)
