---
name: simplify-skill-install
created: 2026-03-04 19:40:31
status: DOING
attach-change: .sspec/changes/26-03-04T19-50_simplify-skill-install/spec.md
tldr: ''
---
<!-- @RULE: Frontmatter Type
status: OPEN | DOING | DONE | CLOSED;
tldr: One-sentence summary for list views — fill this!
 -->

# Request: simplify-skill-install

## Background
<!-- Current situation, background information -->
请先参考 spec-doc 中 skill installation ；理解当前 SKILL 安装的策略和逻辑
然后参考 .meta.json 了解当前的规格

## Problem
<!-- What is not working or missing -->
由于历史原因，当前 SKILL 安装的相关代码有些复杂甚至繁琐
这是因为旧版本中，SKILL 用 symbolic link 安装，在 windows 下就有一大堆复杂的权限问题
不过后来改用 junction link，发现也 Ok，所以现在的做法一直是默认 junction link (win 平台)

现在看来，windows 下的 symbolic link 完全可以去掉。

## Initial Direction
<!-- Your rough idea or preferred direction — details are fine but not required.
This becomes the starting point for the change's spec.md Section A/B. -->

- 改进 SKILL 安装策略
  - windows 下默认直接使用 junction link
  - Linux 下默认直接使用 symbolic link
  - 两者都不需要 sudo 权限
- 简化 src\sspec\skill_installer.py 去掉无用的逻辑
- 简化 .meta.json，去掉 skill_install_strategies 字段
  - 更新 .meta.json 的 meta_schema 为 2.1，并做好迁移策略
  - 具体迁移请参考 `config-schema-design` SKILL


## Relational Context
<!-- Constraints, preferences, related filelinks -->

- src\sspec\skill_installer.py
- src\sspec\commands\project.py
- src\sspec\commands\skill.py

---

## @AGENT
<!-- What should Agent do to implement this request -->
Adhere to the SSPEC protocol specifications and commence development from the current Request file, following the SSPEC/Development Lifecycle.
Next step: Read `sspec-research` SKILL + `sspec-design` SKILLs + `sspec change new --from <this>`.

- 在 design 完成之后，发送 ask/question 给我让我批准你的方案再执行
- 在完成所有代码之后，调用 subagnet 按照 clean code 的标准，去检查和 SKILL 相关的代码
