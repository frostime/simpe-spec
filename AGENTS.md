# SSPEC Project Development Guide

## What is This Project?

**sspec** is a spec-driven CLI framework that helps users practice vibe coding with AI agents. This project is **self-hosted** - we use sspec itself to manage sspec's development.

⚠️ **Important for Agents**: This project develops the SSPEC framework itself. Do NOT use the SSPEC protocol embedded below for development guidance - it may be outdated.

---

## For AI Agents Working on SSPEC

### 📍 Ground Truth

**The authoritative SSPEC protocol is the template we're developing**:
- **Template source**: [src/sspec/templates/AGENTS.md](src/sspec/templates/AGENTS.md)
- This is what gets copied to user projects during `sspec project init`

**When working on SSPEC features**:
1. Read the template files to understand current behavior
2. Test changes using `.venv\Scripts\sspec.exe` in `tmp/` directories
3. Refer to [.sspec/](.sspec/) for this project's changes and tasks

### 🧪 Testing Protocol

**Always test CLI changes before considering them complete**:

```powershell
# Create test directory
cd tmp
New-Item -ItemType Directory test_<feature_name>
cd test_<feature_name>

# Test using the editable install
..\..\.venv\Scripts\sspec.exe project init [--options]
..\..\.venv\Scripts\sspec.exe change new example
# ... test other commands
```

**Verification checklist**:
- ✅ Generated files match templates in `src/sspec/templates/`
- ✅ CLI output is clear and helpful
- ✅ File structure is correct
- ✅ Error handling works as expected

### 🛠️ Development Setup

**Tech Stack**:
- Python 3.11+
- uv for package management
- Click for CLI
- Rich for terminal output

**Key directories**:
- `src/sspec/` - Source code
  - `cli.py` - Entry point
  - `commands/` - CLI command implementations
  - `core.py` - Core utilities
  - `templates/` - File templates (AGENTS.md, spec.md, etc.)
- `.sspec/` - This project's own sspec data (dogfooding)
- `tmp/` - Testing sandbox

**Installation (editable mode)**:
```powershell
# Install/reinstall after code changes
uv pip install -e .
```

### 📋 Conventions

**Code Style**:
- Follow existing patterns in codebase
- Line length ≤ 90 characters (linter enforced)
- Use type hints for function signatures
- Docstrings for public functions

**Testing Philosophy**:
- Real CLI testing over mocks (test in `tmp/`)
- Verify generated output matches templates
- Test both happy path and error cases

**Commit Message Style**:
- Prefix: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`
- Example: `feat: add --skill-loc parameter to project init`

---

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

---

## Project Context and Glossary

| Term | Definition |
|------|------------|
| **sspec** | The CLI tool / framework this project builds |
| **template** | Files in `src/sspec/templates/` copied to user projects |
| **AGENTS.md** | The protocol file for AI agents (the template we're developing) |
| **self-hosting** | Using sspec to manage sspec's own development |
| **change** | A unit of work tracked in `.sspec/changes/` |
| **vibe coding** | Iterative, AI-assisted development workflow |

---

**Agent Recommendations**:
1. **Always test in tmp/**: Don't assume template changes work until tested
2. **Use .sspec/ for planning**: The structure genuinely helps organize complex refactors
3. **Update handover.md**: It's tedious but critical for session continuity
4. **Leverage auto mode**: For medium complexity tasks, it saves back-and-forth

---

## Quick Reference

### Frequently Modified Files

| File | Purpose | When to Edit |
|------|---------|--------------|
| `src/sspec/templates/AGENTS.md` | User-facing protocol | Improving agent guidance |
| `src/sspec/templates/skills/sspec/SKILL.md` | Extended reference | Status rules, edge cases |
| `src/sspec/commands/*.py` | CLI implementations | Adding/modifying commands |
| `src/sspec/core.py` | Shared utilities | Cross-cutting functionality |
| `pyproject.toml` | Package metadata | Dependencies, version, entry points |

### Common Development Tasks

```powershell
# Reinstall after changes
uv pip install -e .

# Test in clean environment
cd tmp; mkdir test_xyz; cd test_xyz
..\..\..\.venv\Scripts\sspec.exe project init

# List changes (dogfooding)
.venv\Scripts\sspec.exe change list
```

---

**Remember**: You're developing the framework that guides other agents. Test thoroughly, write clear templates, and use `.sspec/` to track your own work.