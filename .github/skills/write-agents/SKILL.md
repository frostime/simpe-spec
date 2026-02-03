---
skill: write-agents
description: "编写优化 Agents.md 时需要遵循的规范、风格、指南"

# write-agents

## Writing Effective AGENTS.md

When improving the AGENTS.md template or writing AI guidance documents, apply these principles:

### 1. Executability (可执行性)

**Definition**: Every paragraph MUST translate to concrete Agent actions or decision criteria.

**Litmus test**: For each paragraph, ask— *"After reading this, what does the Agent do next?"* If the answer is vague, the paragraph is ineffective.

| Pattern | ❌ Ineffective (Will Be Ignored) | ✅ Effective (Actionable) |
|---------|----------------------------------|---------------------------|
| Tech stack listing | `Tech stack: React 18, TypeScript, Tailwind` | `Components MUST use React function components + TypeScript. Styling MUST use Tailwind classes; CSS files are FORBIDDEN.` |
| Important markers | `Important file: src/config/settings.ts` | `When adding environment variables, MUST update default values in src/config/settings.ts` |
| Vague quality asks | `Keep code clean` | `Functions >40 lines MUST be split. Files >300 lines SHOULD be split into modules.` |
| Implicit expectations | `Follow existing project style` | `Naming: Components=PascalCase, hooks=camelCase with "use" prefix, constants=UPPER_SNAKE_CASE` |
| Abstract goals | `Consider performance and security` | `Database queries MUST use parameterized statements. Lists >50 items MUST use virtual scrolling.` |
| Background info | `This is an e-commerce backend service` | `This service handles payments. Monetary calculations MUST use Decimal; float is FORBIDDEN.` |

### 2. Explicit Over Implicit (显式优于隐式)

**Definition**: Never assume the Agent will "understand intent" or "automatically connect context." All expected behaviors must be stated explicitly.

**Anti-pattern**:
```markdown
❌ IMPLICIT EXPECTATION

## Project Structure
src/
├── components/   # Reusable components
├── features/     # Business modules
└── utils/        # Utilities

(User's thought: Agent should know where to put new code, right?)
(Reality: Agent may place files randomly or ask every time)
```

**Correct pattern**:
```markdown
✅ EXPLICIT RULES

## File Placement Rules

When creating new files, determine location by type:

| File Type | Target Path | Example |
|-----------|-------------|---------|
| Feature-specific component | src/features/{feature}/components/ | src/features/checkout/components/ |
| Global utility | src/utils/ | src/utils/format.ts |
```

### 3. Minimal Sufficiency (最小充分)

**Definition**: Provide exactly what the Agent needs to complete the task—no more, no less.

- **No more**: Avoid background knowledge that "might be useful"—it wastes context window
- **No less**: All decision-affecting constraints MUST be explicitly stated

**Anti-pattern**: Including a 500-line API reference when Agent only needs 3 endpoints
**Correct**: Reference the doc, specify which endpoints to use, state the constraints

### 4. Determinism (确定性)

**Definition**: Same input → predictable output. Eliminate ambiguity.

**Anti-pattern**: "You can use A, B, or C" → Agent may choose differently each time

**Correct patterns**:
```markdown
✅ Priority order: Try A first. If A fails, use B. C is last resort.

✅ Selection criteria:
  - Use A when: <condition>
  - Use B when: <condition>
  - Default to C otherwise
```
