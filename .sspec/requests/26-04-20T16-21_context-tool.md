---
name: context-tool
created: 2026-04-20T16:21:00
status: DONE
attach-change: null
tldr: ""
---

<!-- @RULE: Frontmatter Type
status: OPEN | DOING | DONE | CLOSED;
tldr: One-sentence summary for list views — fill this!
 -->

# Request: context-tool

## Background
<!-- Current situation, background information -->
当前 sspec tool context 的功能是拼接 prompt 但是存在各种问题

## Problem
<!-- What is not working or missing -->

1. 要求 sspec project root，按理说 sspec tool 系列是通用的，不需要这种限制
2. sspec tool context --help 中没有提示 --add-xxx 这些通用 flag
3. 运行失败，无法添加 glob
```bash
H:\SrcCode\playground\sspec                                                                                     main  👾   Ⓜ 21GiB/31GiB
❯❯❯ uv run sspec tool context --add-glob .\scripts\*
Error: Unexpected positional token in prompt source list: '.\scripts\debug_runner.py'
```

## Relational Context
<!-- Constraints, preferences, related filelinks -->
- @src\sspec\builtin_tools\context.py
