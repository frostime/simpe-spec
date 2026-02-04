---
skill: sspec-ask
version: 1.0.0
description: Use `sspec ask` to ask users questions mid-execution and persist the Q/A record under .sspec/asks/. Alais of the skill "sspec ask", "ask prompt", "user ask". This is very important SKILL, use this skill actively whenever Agents need user's feedback in-loop.
---

# SSPEC Ask Skill

## Purpose

Use `sspec ask` when Agent need user input mid-execution. It agents to ask users questions mid-execution without ending the current conversation turn, reducing billing costs by up to 50%.

**Vibe coding  benefit:** Human-in-the-loop at decision points reduces hallucination and directional errors.
**Cost benefit for copilot:**
- Traditional: Turn 1 (5 tool calls) → Stop → 1 Credit + Turn 2 (5 tool calls) → 1 Credit = **2 Credits**
- Ask-Prompt: Turn 1 (5 tool calls → ask user → 5 tool calls) = **1 Credit**

## Usage

Execute `sspec ask` CLI command under root directiory (where exists `.sspec`)

```
>> sspec ask --help
Usage: sspec ask [OPTIONS]

  Ask user for input and save the Q/A record under .sspec/asks/.

Options:
  --name TEXT      Ask topic/name (used in filename)  [required]
  --question TEXT  Question text (multi-line supported). Use '-' to read full
                   stdin.  [required]
  --why TEXT       Why this question is being asked (optional)
  --help           Show this message and exit.
```

## Guidelines

- Always provide a short `--why` so future Agents understand the intent.
- Use a stable `--name` so records are easy to search.
- For multi-line questions:
  - PowerShell: pass a here-string to `--question`.
  - Bash/Zsh: use `--question -` and provide the question via stdin.
  - If markdown is used in the question, limit headings to a maximum of Header 3 (`###`).
- The command prompts the user for an answer (multi-line). The user finishes by typing `END` on a new line.
- The result is saved to `.sspec/asks/<yymmddHHMMSS>_<name>.md`.

## Use Conditions !IMPORTANT!

Use this when:

- [ ] The user explicitly requests that Ask Prompt be recommended or required in certain scenarios.
- [ ] Information is missing, leading to low reliability and high uncertainty in subsequent work.
  - Example: Some terms in the user's request lack clear context, making it difficult to determine their specific meaning. In such cases, the Agent should ask the user to clarify the intended meaning.
- [ ] Subsequent steps depend on directional choices (not minor adjustments).
  - Example: When refactoring a component, multiple architectural styles can be applied. The Agent should consult the user for their preference.
- [ ] The Agent believes the task is complete and needs to confirm with the user whether to end.
  - Example: After modifying the code, if the Agent believes the user's instructions have been fulfilled, it should ask the user to verify and confirm satisfaction.
- [ ] Multiple attempts at an operation have failed, requiring consultation with the user.
  - Example: After multiple failed attempts to run a CLI command, the Agent consults the user and learns that the .venv environment must be activated first.

## Examples

### PowerShell (multi-line question)

```powershell
sspec ask --name "test_error" --why "无法理解为何 test 命令总是出错" --question @'
请问：
1) 你希望 test 运行哪些步骤？
2) 你看到的错误日志是哪些？
'@
```

### Bash/Zsh (stdin question)

```bash
sspec ask --name "test_error" --why "无法理解为何 test 命令总是出错" --question - << 'EOF'
请问：
1) 你希望 test 运行哪些步骤？
2) 你看到的错误日志是哪些？
EOF
```
