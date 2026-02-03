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
<ProjectDir>\.venv\Scripts\python.exe -m sspec.cli project init [--options]
uv run sspec <command>  # Use UV to run sspec command
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

## Ask-Prompt：轮内用户交互

在 Agent 运行过程中，遇到困惑、需要用户决策、需注入信息的情况，使用 Ask-Prompt 咨询用户：

1. **Human-in-the-loop**——关键决策点引入人类确认，降低幻觉和方向性错误
2. **省钱**——避免提前结束对话轮次，提高单轮效率

**重要：在 Invoke 之前，必须要查看** SKILL `ask-prompt`

**核心原理**：Copilot 按对话轮次计费。工具调用序列中使用 `ask-prompt` SKILL 可在不结束当前轮次的情况下获取用户输入。

**推荐调用方案 ：** 阅读 Ask-Prompt Skill → 创建 `tmp_<ask>.py` 临时文件 → 运行 → 获取回复 → 删除临时文件

**触发条件**：

- [ ] 信息缺失会阻碍后续工作可靠性
- [ ] 后续步骤依赖方向性选择（不是微调）
- [ ] Agent 认为已完成工作，需确认是否结束

> [!WARNING]
>
> 严禁 Agent 私自结束对话，当发现做无可做的时候，请发起一个 Ask Prompt，询问用户是否已经满意，是否可以结束当前对话轮次

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
.venv/Scripts/activate
# Test in clean environment
cd tmp; mkdir test_xyz; cd test_xyz
uv run sspec project init
```

---

**Remember**: You're developing the framework that guides other agents. Test thoroughly, write clear templates, and use `.sspec/` to track your own work.