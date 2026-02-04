# SSPEC Project Development Guide

## What is This Project?

**sspec** is a spec-driven CLI framework that helps users practice vibe coding with AI agents. This project is **self-hosted** - we use sspec itself to manage sspec's development.

⚠️ **Important for Agents**: This project develops the SSPEC framework itself. Do NOT use the SSPEC protocol embedded below for development guidance - it may be outdated.

---

## Dev Tools

- Use uv to manage the project
- Use ruff for formatting

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

### 🛠️ Development Setup

**Tech Stack**:
- Python 3.11+
- **uv** for package management
- Click for CLI
- Rich for terminal output
- Questionary for user input

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

## SSPEC Ask：轮内用户交互

如果 User 明确指定，或者遇到特定条件，必须使用 SSPEC Ask (Ask Prompt) 咨询 User。

1. **触发条件**（满足以下任一情况时触发）：

   - [ ] User 在请求时明确告知在某些情况下推荐/必须使用 Ask Prompt
   - [ ] 信息缺失，导致后续工作可靠性低、不确定性高。
     例：User请求中的部分术语缺乏明确上下文，难以确定具体含义，此时Agent需请User澄清具体所指。
   - [ ] 后续步骤依赖方向性选择（非微调性选择）。
     例：重构组件可采用多种程序架构风格，Agent需咨询User选择偏好。
   - [ ] Agent认为工作已完成，需与User确认是否结束。
     例：Agent完成代码修改后，认为已满足User指令，需请User核实确认是否满意。
   - [ ] 多次尝试某项操作失败，需向User咨询。
     例：多次尝试运行某CLI命令均失败，经咨询User后得知需先激活 .venv 环境。
2. **先决条件**：查看`sspec-ask` SKILL 详细内容，了解 sspec ask 的用法。 **!IMPORTANT!**
3. **WHY Need Ask**

   1. Effective:  **Human-in-the-loop**——关键决策点引入人类确认，降低幻觉和方向性错误
   2. Efficient: **节省费用**——Copilot 按对话轮次计费。工具调用序列中使用 `sspec-ask` SKILL可在不结束当前轮次的情况下获取用户输入。


> [!WARNING] Agent 结束单轮对话之前必须发起 Ask
>
> | match "Agent认为工作已完成" --> 请发起一个 SSPEC Ask，询问用户是否已经满意，是否可以结束当前对话轮次

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

---

**Remember**: You're developing the framework that guides other agents. Test thoroughly, write clear templates, and use `.sspec/` to track your own work.